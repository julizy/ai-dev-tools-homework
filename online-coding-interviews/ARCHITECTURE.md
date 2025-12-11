# Architecture & Technical Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HTML/CSS/JavaScript                                │  │
│  │  ├─ Ace Editor (syntax highlighting)                │  │
│  │  ├─ Socket.IO Client (real-time communication)      │  │
│  │  ├─ Pyodide (Python runtime)                        │  │
│  │  └─ JavaScript Executor                             │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────┘
                            │ WebSocket
                            │ HTTP
┌───────────────────────────▼────────────────────────────────┐
│                Backend (Flask/Python)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask Application                                  │  │
│  │  ├─ Flask-SocketIO (WebSocket server)              │  │
│  │  ├─ REST API (session management)                   │  │
│  │  ├─ SQLAlchemy ORM (database layer)                │  │
│  │  └─ Session Manager (broadcast logic)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database (SQLite)                                  │  │
│  │  ├─ InterviewSession                                │  │
│  │  ├─ Session Code                                    │  │
│  │  ├─ Code Content                                    │  │
│  │  └─ Active Users                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with variables
- **JavaScript (ES6+)** - Client-side logic
- **Ace Editor** - Code editor with syntax highlighting
- **Socket.IO Client** - Real-time bidirectional communication
- **Pyodide** - Python interpreter compiled to WebAssembly

### Backend
- **Flask** - Lightweight web framework
- **Flask-SocketIO** - WebSocket support for real-time features
- **SQLAlchemy** - ORM for database operations
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Lightweight embedded database
- **Python 3.8+** - Server runtime

### Build & Deployment
- **npm** - Package management (optional, not used currently)
- **pip** - Python package management
- **Virtual Environment** - Python isolation

## File Structure

```
online-coding-interviews/
├── backend/
│   ├── app.py                          # Main Flask application
│   ├── requirements.txt                # Python dependencies
│   ├── venv/                           # Virtual environment
│   └── coding_interviews.db            # SQLite database
├── frontend/
│   ├── static/
│   │   ├── app.js                      # Main app logic (landing page)
│   │   ├── editor.js                   # Editor page logic
│   │   └── styles.css                  # Global styling
│   └── templates/
│       ├── index.html                  # Landing page template
│       └── editor.html                 # Editor page template
├── README.md                           # Project documentation
├── QUICKSTART.md                       # Quick start guide
├── TESTING.md                          # Testing guide
├── start.sh                            # Linux/macOS startup script
├── start.bat                           # Windows startup script
└── ARCHITECTURE.md                     # This file
```

## Core Components

### 1. Backend Architecture (app.py)

#### Database Models
```python
class InterviewSession(db.Model):
    id: str                              # UUID primary key
    session_code: str                    # Human-readable code
    code: str                            # Current code content
    language: str                        # Programming language
    connected_users: int                 # Active user count
    created_at: datetime                 # Session creation time
```

#### REST Endpoints
```
POST   /api/session                     # Create new session
GET    /api/session/<code>              # Get session details
GET    /interview/<code>                # Load editor page
```

#### WebSocket Events (Socket.IO)

**Client → Server:**
- `join_session` - User joins a session
- `code_change` - Code updated by user
- `language_change` - Programming language changed
- `execute_code` - Request code execution

**Server → Client:**
- `user_joined` - Notification of new user
- `user_left` - Notification of user departure
- `code_updated` - Code changed by another user
- `language_updated` - Language changed by another user
- `sync_code` - Initial code sync for new users
- `error` - Error notification

### 2. Frontend Architecture

#### Landing Page (index.html + app.js)
- Session creation
- Session joining via code
- Share modal dialog
- Initial editor setup

#### Editor Page (editor.html + editor.js)
- Active editing interface
- Real-time synchronization display
- Code execution interface
- Multi-user awareness

#### Shared Components
- Ace Editor integration
- WebSocket management
- Code execution engine
- UI state management

### 3. Real-time Communication Flow

```
User A Types → Socket.IO Client → WebSocket → Flask Server
                                                    ↓
                                           Store in memory & DB
                                                    ↓
                                    Broadcast to all users
                                                    ↓
            WebSocket ← Socket.IO Client ← Updated Code
                ↓
        Update Editor (preserve cursor)
                ↓
            User B sees changes
```

### 4. Code Execution Pipeline

#### JavaScript
```
User Code → JavaScript eval() → Capture console.log
                ↓
            Execute in browser context
                ↓
            Display in output panel
```

#### Python
```
User Code → Pyodide (WebAssembly) → Capture stdout
                ↓
            Execute in WASM runtime
                ↓
            Display in output panel
```

#### HTML/CSS
```
User Code → Create iframe → Inject HTML
                ↓
            Render in isolated sandbox
                ↓
            Display preview in output
```

## Session Management

### Session Lifecycle

1. **Creation**
   - Generate UUID and session code
   - Create database record
   - Add to in-memory tracking
   - Return session info to user

2. **Joining**
   - Validate session exists
   - Create WebSocket room
   - Add user to tracking set
   - Send current code/language
   - Notify other users

3. **Editing**
   - Capture code changes
   - Update database and memory
   - Broadcast to room
   - Preserve cursor position

4. **Disconnection**
   - Remove user from tracking
   - Update user count
   - Notify remaining users
   - Clean up if empty

### In-Memory Tracking

```python
active_sessions = {
    'session-uuid-1': {
        'users': {user_id_1, user_id_2},
        'code': '...',
        'language': 'javascript'
    },
    'session-uuid-2': {
        ...
    }
}
```

## Data Flow

### Code Change Flow
```
1. User types in editor
2. Ace Editor fires 'change' event
3. JavaScript captures code
4. Socket.IO emits 'code_change'
5. Server receives code_change event
6. Server updates database
7. Server broadcasts via Socket.IO to room
8. All other clients receive 'code_updated'
9. Clients update editor (with cursor preservation)
10. Process repeats for next change
```

### Language Change Flow
```
1. User selects language from dropdown
2. JavaScript calls changeLanguage()
3. Ace Editor mode changes (syntax highlighting)
4. Socket.IO emits 'language_change'
5. Server receives and broadcasts
6. Other clients update language
```

## Performance Optimizations

### Frontend
- **Debounced Updates**: Limit WebSocket messages
- **Cursor Preservation**: Save/restore cursor position on sync
- **Lazy Loading**: Pyodide loads asynchronously
- **Code Caching**: Ace Editor buffers code efficiently
- **Event Delegation**: Efficient event listeners

### Backend
- **In-Memory Cache**: Active sessions cached in memory
- **Database Indexing**: Session code indexed for quick lookup
- **Selective Broadcasting**: Messages only sent to relevant room
- **Efficient Serialization**: Minimal JSON overhead

### Network
- **WebSocket Over HTTP**: Persistent connection
- **Binary Frame Support**: Potentially faster than text
- **Message Batching**: Multiple changes combined
- **Compression**: Socket.IO supports compression

## Security Considerations

### Current Implementation
- ✓ Code execution sandboxed in browser
- ✓ No direct server code execution
- ✓ SQLite prevents SQL injection (ORM usage)
- ✓ CORS enabled for development

### Recommended for Production
- [ ] Session token authentication
- [ ] Rate limiting on WebSocket events
- [ ] HTTPS/WSS encryption
- [ ] Code execution timeouts
- [ ] Memory limits for Pyodide
- [ ] Input validation and sanitization
- [ ] Session encryption at rest
- [ ] Audit logging

## Scalability

### Current Limitations
- **Single Server**: One Flask instance
- **In-Memory Sessions**: Lost on restart
- **SQLite Database**: Limited concurrent writes
- **Local Storage**: File-based persistence

### Scaling Strategy
1. **Horizontal Scaling**
   - Load balancer (nginx)
   - Multiple Flask instances
   - Redis for session sharing
   - Database connection pooling

2. **Vertical Scaling**
   - Use Gunicorn/uWSGI
   - Increase worker processes
   - Optimize database queries
   - Cache frequently accessed data

3. **Database Optimization**
   - Migrate to PostgreSQL
   - Add proper indexing
   - Archive old sessions
   - Connection pooling

## Configuration

### Environment Variables
```bash
PORT              # Server port (default: 5000)
FLASK_ENV         # Environment (development/production)
DATABASE_URL      # Database connection string
SECRET_KEY        # Flask secret key
MAX_CONTENT_LENGTH # Max upload size
```

### Flask Configuration
```python
DEBUG              # Debug mode (disable in production)
TESTING            # Test mode
SESSION_COOKIE_SECURE  # HTTPS only
PERMANENT_SESSION_LIFETIME  # Session timeout
SQLALCHEMY_ECHO    # SQL query logging
```

## Monitoring & Logging

### Server Logs
- Application startup/shutdown
- WebSocket connection events
- Database operations
- Error messages

### Metrics to Track
- Active sessions
- Connected users
- WebSocket message frequency
- Code execution duration
- Error rates

## Deployment

### Development
```bash
# Local development on port 5000/8000
python app.py
```

### Production
```bash
# Using Gunicorn
gunicorn --worker-class eventlet -w 1 app:app

# Using docker
docker build -t coding-interviews .
docker run -p 5000:5000 coding-interviews
```

### Docker Setup
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

## Testing Strategy

### Unit Tests
- WebSocket event handlers
- Database operations
- Utility functions

### Integration Tests
- Full user session lifecycle
- Multi-user synchronization
- Code execution

### E2E Tests
- Browser automation (Selenium/Cypress)
- Multiple concurrent users
- UI interactions

## Troubleshooting Guide

### WebSocket Connection Issues
- Check browser console for errors
- Verify firewall allows WebSocket
- Ensure backend is running
- Check Socket.IO version compatibility

### Code Sync Delays
- Monitor network latency
- Check server CPU usage
- Verify database performance
- Review WebSocket message queue

### Memory Issues
- Monitor Pyodide memory usage
- Clear output panel regularly
- Restart session if needed
- Check browser memory (DevTools)

## Future Enhancements

### Short Term
- Code syntax error detection
- Auto-save functionality
- Session password protection
- User authentication

### Medium Term
- Code version history
- Collaborative cursors (show other users' positions)
- Code comments/annotations
- Export functionality

### Long Term
- AI-powered code suggestions
- Video/audio integration
- Team workspaces
- Integration with popular coding platforms
- Mobile native app

---

**Last Updated:** December 2024
**Version:** 1.0.0
