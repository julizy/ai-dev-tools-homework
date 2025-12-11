"""
Integration tests for Online Coding Interview Platform

Tests the interaction between client and server through WebSocket and HTTP endpoints.
"""

import pytest
import json
import time
from threading import Thread
import requests
from socketio import Client
from app import app, db, InterviewSession


class TestServerIntegration:
    """Test suite for server-side functionality"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app.test_client()
            db.session.remove()
            db.drop_all()

    def test_create_session_endpoint(self, client):
        """Test session creation via REST API"""
        response = client.post('/api/session')
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data['success'] == True
        assert 'session_id' in data
        assert 'session_code' in data
        assert 'url' in data
        assert len(data['session_code']) == 8

    def test_get_session_endpoint(self, client):
        """Test retrieving session details"""
        # Create a session first
        create_response = client.post('/api/session')
        session_code = json.loads(create_response.data)['session_code']

        # Get session details
        response = client.get(f'/api/session/{session_code}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert 'session' in data
        assert data['session']['session_code'] == session_code

    def test_get_nonexistent_session(self, client):
        """Test getting non-existent session"""
        response = client.get('/api/session/INVALID00')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Session not found' in data['error']

    def test_index_route(self, client):
        """Test landing page route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data

    def test_interview_page_route(self, client):
        """Test interview page route"""
        # Create session first
        create_response = client.post('/api/session')
        session_code = json.loads(create_response.data)['session_code']

        # Access interview page
        response = client.get(f'/interview/{session_code}')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data


class TestWebSocketIntegration:
    """Test suite for WebSocket functionality"""

    @pytest.fixture
    def server_thread(self):
        """Start server in background thread"""
        def run_server():
            app.config['TESTING'] = True
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            with app.app_context():
                db.create_all()
                from app import socketio
                socketio.run(app, port=5001, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

        thread = Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(2)  # Wait for server to start
        return thread

    @pytest.fixture
    def socket_client(self, server_thread):
        """Create Socket.IO client"""
        client = Client()
        try:
            client.connect('http://localhost:5001')
            yield client
            client.disconnect()
        except Exception as e:
            print(f"Socket connection error: {e}")

    def test_connect_to_server(self, socket_client):
        """Test connecting to server via WebSocket"""
        assert socket_client.connected == True

    def test_join_session_event(self, socket_client):
        """Test joining a session"""
        received_data = {}

        @socket_client.on('sync_code')
        def on_sync_code(data):
            received_data['sync'] = data

        # First, create a session via HTTP
        response = requests.post('http://localhost:5001/api/session')
        session_data = response.json()
        session_code = session_data['session_code']

        # Join session
        socket_client.emit('join_session', {'session_code': session_code})
        time.sleep(0.5)

        assert 'sync' in received_data
        assert 'code' in received_data['sync']
        assert 'language' in received_data['sync']

    def test_code_change_broadcast(self):
        """Test code change synchronization"""
        # Create two clients
        client1 = Client()
        client2 = Client()

        try:
            client1.connect('http://localhost:5001')
            client2.connect('http://localhost:5001')

            # Create a session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            received_data = {'client2': {}}

            @client2.on('code_updated')
            def on_code_update(data):
                received_data['client2'] = data

            # Both clients join same session
            client1.emit('join_session', {'session_code': session_code})
            client2.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Client1 changes code
            test_code = 'console.log("hello");'
            client1.emit('code_change', {
                'session_code': session_code,
                'code': test_code
            })
            time.sleep(0.5)

            # Verify client2 received the update
            assert 'client2' in received_data
            assert received_data['client2'].get('code') == test_code

        finally:
            if client1.connected:
                client1.disconnect()
            if client2.connected:
                client2.disconnect()

    def test_language_change_broadcast(self):
        """Test language change synchronization"""
        client1 = Client()
        client2 = Client()

        try:
            client1.connect('http://localhost:5001')
            client2.connect('http://localhost:5001')

            # Create a session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            received_data = {'client2': {}}

            @client2.on('language_updated')
            def on_language_update(data):
                received_data['client2'] = data

            # Both clients join
            client1.emit('join_session', {'session_code': session_code})
            client2.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Client1 changes language
            client1.emit('language_change', {
                'session_code': session_code,
                'language': 'python'
            })
            time.sleep(0.5)

            # Verify client2 received update
            assert 'client2' in received_data
            assert received_data['client2'].get('language') == 'python'

        finally:
            if client1.connected:
                client1.disconnect()
            if client2.connected:
                client2.disconnect()

    def test_user_join_notification(self):
        """Test user join notification"""
        client1 = Client()
        client2 = Client()

        try:
            client1.connect('http://localhost:5001')

            # Create session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            received_data = {'notifications': []}

            @client1.on('user_joined')
            def on_user_join(data):
                received_data['notifications'].append(('joined', data))

            # Client1 joins
            client1.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Client2 connects and joins
            client2.connect('http://localhost:5001')
            client2.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Verify client1 was notified
            assert len(received_data['notifications']) > 0
            notification_type, data = received_data['notifications'][-1]
            assert notification_type == 'joined'
            assert data['user_count'] == 2

        finally:
            if client1.connected:
                client1.disconnect()
            if client2.connected:
                client2.disconnect()

    def test_user_leave_notification(self):
        """Test user leave notification"""
        client1 = Client()
        client2 = Client()

        try:
            client1.connect('http://localhost:5001')
            client2.connect('http://localhost:5001')

            # Create session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            received_data = {'notifications': []}

            @client1.on('user_left')
            def on_user_left(data):
                received_data['notifications'].append(('left', data))

            # Both join
            client1.emit('join_session', {'session_code': session_code})
            client2.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Client2 disconnects
            client2.disconnect()
            time.sleep(0.5)

            # Verify client1 was notified
            assert len(received_data['notifications']) > 0
            notification_type, data = received_data['notifications'][-1]
            assert notification_type == 'left'

        finally:
            if client1.connected:
                client1.disconnect()
            if client2.connected:
                try:
                    client2.disconnect()
                except:
                    pass


class TestMultiUserScenarios:
    """Test complex multi-user scenarios"""

    def test_three_user_collaboration(self):
        """Test three users editing simultaneously"""
        clients = [Client(), Client(), Client()]

        try:
            # Connect all clients
            for client in clients:
                client.connect('http://localhost:5001')

            time.sleep(1)

            # Create session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            # Setup receivers with list to collect updates
            received_updates = [[] for _ in range(3)]

            @clients[0].on('code_updated')
            def on_update_1(data):
                received_updates[0].append(data)

            @clients[1].on('code_updated')
            def on_update_2(data):
                received_updates[1].append(data)

            @clients[2].on('code_updated')
            def on_update_3(data):
                received_updates[2].append(data)

            # All join
            for i, client in enumerate(clients):
                client.emit('join_session', {'session_code': session_code})

            time.sleep(0.5)

            # Client 0 sends code
            code1 = 'let x = 1;'
            clients[0].emit('code_change', {
                'session_code': session_code,
                'code': code1
            })
            time.sleep(1)

            assert len(received_updates[1]) > 0 and received_updates[1][0].get('code') == code1
            assert len(received_updates[2]) > 0 and received_updates[2][0].get('code') == code1

            # Client 1 sends code
            code2 = 'let x = 2;'
            clients[1].emit('code_change', {
                'session_code': session_code,
                'code': code2
            })
            time.sleep(1)

            assert len(received_updates[0]) > 0 and received_updates[0][0].get('code') == code2
            assert len(received_updates[2]) > 1 and received_updates[2][1].get('code') == code2

        finally:
            for client in clients:
                if client.connected:
                    client.disconnect()

    def test_session_persistence(self, client=None):
        """Test that session data persists in database"""
        if client is None:
            app.config['TESTING'] = True
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            with app.app_context():
                db.create_all()
                client = app.test_client()

        # Create session
        response = client.post('/api/session')
        data = json.loads(response.data)
        session_code = data['session_code']

        # Verify in database
        with app.app_context():
            session = InterviewSession.query.filter_by(
                session_code=session_code
            ).first()
            assert session is not None
            assert session.code == '// Start coding here...\n'
            assert session.language == 'javascript'


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_session_code_format(self):
        """Test handling of invalid session code"""
        client = Client()
        try:
            client.connect('http://localhost:5001')

            received_errors = []

            @client.on('error')
            def on_error(data):
                received_errors.append(data)

            # Try to join invalid session
            client.emit('join_session', {'session_code': 'INVALID'})
            time.sleep(0.5)

            # Should not crash
            assert client.connected

        finally:
            if client.connected:
                client.disconnect()

    def test_missing_session_code_in_event(self):
        """Test handling of missing session code"""
        client = Client()
        try:
            client.connect('http://localhost:5001')

            # Try to change code without session code
            client.emit('code_change', {'code': 'console.log("test");'})
            time.sleep(0.5)

            # Should not crash
            assert client.connected

        finally:
            if client.connected:
                client.disconnect()

    def test_large_code_submission(self):
        """Test handling of large code files"""
        client1 = Client()
        client2 = Client()

        try:
            client1.connect('http://localhost:5001')
            client2.connect('http://localhost:5001')

            # Create session
            response = requests.post('http://localhost:5001/api/session')
            session_code = response.json()['session_code']

            received_data = {}

            @client2.on('code_updated')
            def on_update(data):
                received_data['code'] = data.get('code')

            # Both join
            client1.emit('join_session', {'session_code': session_code})
            client2.emit('join_session', {'session_code': session_code})
            time.sleep(0.5)

            # Send large code (50KB)
            large_code = '// ' + 'x' * 50000
            client1.emit('code_change', {
                'session_code': session_code,
                'code': large_code
            })
            time.sleep(1)

            # Verify it was transmitted
            assert received_data.get('code') is not None
            assert len(received_data['code']) > 40000

        finally:
            if client1.connected:
                client1.disconnect()
            if client2.connected:
                client2.disconnect()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
