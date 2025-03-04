from datetime import datetime, timedelta

import pytest

from app import create_app, db
from app.models import Task, User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
        
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        
        # Create a test admin user
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('adminpass')
        db.session.add(admin)
        
        db.session.commit()
        
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, email='test@example.com', password='password123'):
            return client.post(
                '/auth/login',
                data={'email': email, 'password': password},
                follow_redirects=True
            )
            
        def logout(self):
            return client.get('/auth/logout', follow_redirects=True)
    
    return AuthActions()


@pytest.fixture
def logged_in_client(client, auth):
    """A test client that's already logged in."""
    auth.login()
    return client


@pytest.fixture
def sample_task(app, logged_in_client):
    """Create a sample task for testing."""
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        task = Task(
            title='Sample Task',
            description='This is a sample task for testing',
            due_date=datetime.now() + timedelta(days=1),
            priority=2,
            user_id=user.id
        )
        db.session.add(task)
        db.session.commit()
        return task 