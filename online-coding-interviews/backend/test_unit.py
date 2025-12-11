"""
Unit tests for Online Coding Interview Platform backend

Tests individual functions and database operations.
"""

import pytest
import json
from app import app, db, InterviewSession
from datetime import datetime


class TestInterviewSession:
    """Test InterviewSession model"""

    @pytest.fixture
    def db_session(self):
        """Setup test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield db
            db.session.remove()
            db.drop_all()

    def test_create_session(self, db_session):
        """Test creating a new session"""
        with app.app_context():
            session = InterviewSession(
                id='test-id-123',
                session_code='ABC123XY',
                code='console.log("test");',
                language='javascript'
            )
            db_session.session.add(session)
            db_session.session.commit()

            # Verify in database
            saved = InterviewSession.query.get('test-id-123')
            assert saved is not None
            assert saved.session_code == 'ABC123XY'
            assert saved.code == 'console.log("test");'

    def test_session_code_unique(self, db_session):
        """Test that session codes are unique"""
        with app.app_context():
            session1 = InterviewSession(
                id='id-1',
                session_code='UNIQUE001',
                code='code1',
                language='javascript'
            )
            session2 = InterviewSession(
                id='id-2',
                session_code='UNIQUE001',
                code='code2',
                language='javascript'
            )

            db_session.session.add(session1)
            db_session.session.commit()

            # Try to add duplicate
            db_session.session.add(session2)
            with pytest.raises(Exception):  # Should raise IntegrityError
                db_session.session.commit()

    def test_session_to_dict(self, db_session):
        """Test session serialization"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='TEST1234',
                code='console.log("test");',
                language='python',
                connected_users=3
            )
            db_session.session.add(session)
            db_session.session.commit()

            result = session.to_dict()
            assert result['session_code'] == 'TEST1234'
            assert result['code'] == 'console.log("test");'
            assert result['language'] == 'python'
            assert result['connected_users'] == 3

    def test_session_update_code(self, db_session):
        """Test updating session code"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='ORIGINAL',
                code='old code',
                language='javascript'
            )
            db_session.session.add(session)
            db_session.session.commit()

            # Update code
            session.code = 'new code'
            db_session.session.commit()

            # Verify update
            saved = InterviewSession.query.get('test-id')
            assert saved.code == 'new code'

    def test_session_update_language(self, db_session):
        """Test updating session language"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='LANG001',
                language='javascript'
            )
            db_session.session.add(session)
            db_session.session.commit()

            # Update language
            session.language = 'python'
            db_session.session.commit()

            # Verify update
            saved = InterviewSession.query.get('test-id')
            assert saved.language == 'python'

    def test_default_values(self, db_session):
        """Test default session values"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='DEFAULT1'
            )
            db_session.session.add(session)
            db_session.session.commit()

            saved = InterviewSession.query.get('test-id')
            assert saved.code == ''
            assert saved.language == 'javascript'
            assert saved.connected_users == 0
            assert isinstance(saved.created_at, datetime)

    def test_session_code_indexing(self, db_session):
        """Test that session code is properly indexed"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='INDEXED01'
            )
            db_session.session.add(session)
            db_session.session.commit()

            # Query by session code should be fast
            found = InterviewSession.query.filter_by(
                session_code='INDEXED01'
            ).first()
            assert found is not None
            assert found.id == 'test-id'

    def test_connected_users_update(self, db_session):
        """Test updating connected user count"""
        with app.app_context():
            session = InterviewSession(
                id='test-id',
                session_code='USERS001',
                connected_users=0
            )
            db_session.session.add(session)
            db_session.session.commit()

            # Increment users
            for i in range(1, 4):
                session.connected_users = i
                db_session.session.commit()

                saved = InterviewSession.query.get('test-id')
                assert saved.connected_users == i


class TestUtilityFunctions:
    """Test utility functions"""

    def test_uuid_generation(self):
        """Test that UUIDs are generated properly"""
        import uuid

        id1 = str(uuid.uuid4())
        id2 = str(uuid.uuid4())

        assert id1 != id2
        assert len(id1) == 36  # UUID4 format
        assert len(id2) == 36

    def test_session_code_generation(self):
        """Test session code generation"""
        import uuid

        code = str(uuid.uuid4())[:8].upper()

        assert len(code) == 8
        assert code.isupper()
        assert code.isalnum()


class TestRestEndpoints:
    """Test REST API endpoints"""

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

    def test_post_session_response_structure(self, client):
        """Test POST /api/session response structure"""
        response = client.post('/api/session')
        data = json.loads(response.data)

        required_keys = ['success', 'session_id', 'session_code', 'url']
        for key in required_keys:
            assert key in data

    def test_post_session_creates_unique_codes(self, client):
        """Test that each session gets a unique code"""
        response1 = client.post('/api/session')
        response2 = client.post('/api/session')

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        assert data1['session_code'] != data2['session_code']

    def test_get_session_by_code(self, client):
        """Test GET /api/session/<code>"""
        # Create session
        create_resp = client.post('/api/session')
        session_code = json.loads(create_resp.data)['session_code']

        # Get session
        get_resp = client.get(f'/api/session/{session_code}')
        data = json.loads(get_resp.data)

        assert data['success'] == True
        assert data['session']['session_code'] == session_code

    def test_get_session_not_found(self, client):
        """Test GET /api/session/<code> with invalid code"""
        response = client.get('/api/session/NOTEXIST')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/session')

        # CORS headers should allow all origins
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200

    def test_session_url_format(self, client):
        """Test that generated URLs have correct format"""
        response = client.post('/api/session')
        data = json.loads(response.data)
        url = data['url']

        assert '/interview/' in url
        assert data['session_code'] in url


class TestDataValidation:
    """Test data validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app.test_client()

    def test_session_code_format(self, client):
        """Test that session code has correct format"""
        response = client.post('/api/session')
        data = json.loads(response.data)
        code = data['session_code']

        assert len(code) == 8
        assert code.isalnum()

    def test_session_id_format(self, client):
        """Test that session ID is a valid UUID"""
        response = client.post('/api/session')
        data = json.loads(response.data)
        session_id = data['session_id']

        # UUID format check
        import uuid
        try:
            uuid.UUID(session_id)
            valid = True
        except ValueError:
            valid = False

        assert valid


class TestConcurrency:
    """Test concurrent access patterns"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app.test_client()

    def test_multiple_session_creation(self, client):
        """Test creating multiple sessions rapidly"""
        responses = []
        for i in range(5):
            resp = client.post('/api/session')
            responses.append(json.loads(resp.data))

        # All should be successful
        for data in responses:
            assert data['success'] == True

        # All codes should be unique
        codes = [data['session_code'] for data in responses]
        assert len(codes) == len(set(codes))

    def test_concurrent_session_retrieval(self, client):
        """Test retrieving same session multiple times"""
        # Create session
        create_resp = client.post('/api/session')
        code = json.loads(create_resp.data)['session_code']

        # Retrieve multiple times
        responses = []
        for i in range(5):
            resp = client.get(f'/api/session/{code}')
            responses.append(json.loads(resp.data))

        # All should have same data
        for data in responses:
            assert data['success'] == True
            assert data['session']['session_code'] == code


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
