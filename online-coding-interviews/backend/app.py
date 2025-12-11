from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import uuid
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Configure app
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coding_interviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Models
class InterviewSession(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    session_code = db.Column(db.String(10), unique=True, index=True)
    code = db.Column(db.Text, default='')
    language = db.Column(db.String(50), default='javascript')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    connected_users = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'session_code': self.session_code,
            'code': self.code,
            'language': self.language,
            'connected_users': self.connected_users
        }

# Store active sessions and their users
active_sessions = {}  # {session_id: {'users': set(), 'code': '', 'language': ''}}

# Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new interview session"""
    try:
        session_id = str(uuid.uuid4())
        session_code = str(uuid.uuid4())[:8].upper()

        session = InterviewSession(
            id=session_id,
            session_code=session_code,
            code='// Start coding here...\n',
            language='javascript'
        )
        db.session.add(session)
        db.session.commit()

        active_sessions[session_id] = {
            'users': set(),
            'code': session.code,
            'language': session.language
        }

        return jsonify({
            'success': True,
            'session_id': session_id,
            'session_code': session_code,
            'url': f'/interview/{session_code}'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/<session_code>', methods=['GET'])
def get_session(session_code):
    """Get session details by session code"""
    try:
        session = InterviewSession.query.filter_by(session_code=session_code).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/interview/<session_code>')
def interview_page(session_code):
    """Serve the interview page"""
    return render_template('editor.html', session_code=session_code)

# WebSocket Events
@socketio.on('connect')
def handle_connect(auth=None):
    """Handle user connection"""
    print(f'User connected: {request.sid}')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('join_session')
def handle_join_session(data):
    """Handle user joining an interview session"""
    try:
        session_code = data['session_code']
        user_id = request.sid

        # Find session
        session = InterviewSession.query.filter_by(session_code=session_code).first()
        if not session:
            emit('error', {'message': 'Session not found'})
            return

        session_id = session.id
        room = f'session_{session_id}'

        # Join the room
        join_room(room)

        # Track user
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                'users': set(),
                'code': session.code,
                'language': session.language
            }

        active_sessions[session_id]['users'].add(user_id)

        # Update user count
        session.connected_users = len(active_sessions[session_id]['users'])
        db.session.commit()

        # Notify all users in the session
        emit('user_joined', {
            'user_id': user_id,
            'user_count': session.connected_users
        }, room=room)

        # Send current code and language to the new user
        emit('sync_code', {
            'code': session.code,
            'language': session.language
        })

        print(f'User {user_id} joined session {session_code}')
    except Exception as e:
        print(f'Error in join_session: {e}')
        emit('error', {'message': str(e)})

@socketio.on('code_change')
def handle_code_change(data):
    """Handle code change from a user"""
    try:
        session_code = data['session_code']
        code = data['code']

        # Find session
        session = InterviewSession.query.filter_by(session_code=session_code).first()
        if not session:
            return

        session_id = session.id
        room = f'session_{session_id}'

        # Update code in memory
        if session_id in active_sessions:
            active_sessions[session_id]['code'] = code

        # Update code in database
        session.code = code
        db.session.commit()

        # Broadcast code change to all users in the session
        emit('code_updated', {
            'code': code,
            'user_id': request.sid
        }, room=room, skip_sid=request.sid)

    except Exception as e:
        print(f'Error in code_change: {e}')

@socketio.on('language_change')
def handle_language_change(data):
    """Handle language change"""
    try:
        session_code = data['session_code']
        language = data['language']

        # Find session
        session = InterviewSession.query.filter_by(session_code=session_code).first()
        if not session:
            return

        session_id = session.id
        room = f'session_{session_id}'

        # Update language
        if session_id in active_sessions:
            active_sessions[session_id]['language'] = language

        session.language = language
        db.session.commit()

        # Broadcast language change to all users
        emit('language_updated', {
            'language': language
        }, room=room, skip_sid=request.sid)

    except Exception as e:
        print(f'Error in language_change: {e}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection"""
    try:
        user_id = request.sid

        # Find and update session
        for session_id, session_data in list(active_sessions.items()):
            if user_id in session_data['users']:
                session_data['users'].discard(user_id)

                # Update database
                session = InterviewSession.query.get(session_id)
                if session:
                    session.connected_users = len(session_data['users'])
                    db.session.commit()

                # Notify remaining users
                room = f'session_{session_id}'
                socketio.emit('user_left', {
                    'user_id': user_id,
                    'user_count': session.connected_users
                }, room=room)

                print(f'User {user_id} left session {session_id}')
    except Exception as e:
        print(f'Error in disconnect: {e}')

@socketio.on('execute_code')
def handle_execute_code(data):
    """Handle code execution request"""
    try:
        session_code = data['session_code']
        code = data['code']
        language = data['language']

        # Find session
        session = InterviewSession.query.filter_by(session_code=session_code).first()
        if not session:
            emit('execution_error', {'error': 'Session not found'})
            return

        session_id = session.id
        room = f'session_{session_id}'

        # Broadcast execution request to all users
        emit('code_executing', {
            'user_id': request.sid,
            'language': language
        }, room=room, skip_sid=request.sid)

    except Exception as e:
        print(f'Error in execute_code: {e}')
        emit('execution_error', {'error': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use port from environment variable or default to 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
