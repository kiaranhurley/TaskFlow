import unittest
from datetime import datetime, timedelta

from flask import url_for
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Task, User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def login(self, email='test@example.com', password='password123'):
        return self.client.post(
            '/auth/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )
        
    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
        
    def create_task(self, title='Test Task', description='Test Description', 
                   due_date=None, priority=1):
        if due_date is None:
            due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
        return self.client.post(
            '/task/new',
            data=dict(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority
            ),
            follow_redirects=True
        )


class TestAuth(BaseTestCase):
    def test_login_page(self):
        """Test that login page loads correctly"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
    def test_register_page(self):
        """Test that register page loads correctly"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
        
    def test_valid_login(self):
        """Test login with valid credentials"""
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.login(email='test@example.com', password='wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)
        
    def test_logout(self):
        """Test logout functionality"""
        self.login()
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)
        
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post(
            '/auth/register',
            data=dict(
                username='newuser',
                email='new@example.com',
                password='newpassword',
                confirm_password='newpassword'
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
        
        # Check that user was added to database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')


class TestTasks(BaseTestCase):
    def test_dashboard_access(self):
        """Test that dashboard requires login"""
        # Without login
        response = self.client.get('/dashboard')
        self.assertNotEqual(response.status_code, 200)
        
        # With login
        self.login()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your Tasks', response.data)
        
    def test_create_task(self):
        """Test task creation"""
        self.login()
        response = self.create_task()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task created successfully', response.data)
        
        # Check that task was added to database
        task = Task.query.filter_by(title='Test Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'Test Description')
        
    def test_edit_task(self):
        """Test task editing"""
        self.login()
        self.create_task()
        
        # Get the task
        task = Task.query.filter_by(title='Test Task').first()
        
        # Edit the task
        response = self.client.post(
            f'/task/{task.id}/edit',
            data=dict(
                title='Updated Task',
                description='Updated Description',
                priority=2
            ),
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task updated successfully', response.data)
        
        # Check that task was updated in database
        updated_task = Task.query.get(task.id)
        self.assertEqual(updated_task.title, 'Updated Task')
        self.assertEqual(updated_task.description, 'Updated Description')
        self.assertEqual(updated_task.priority, 2)
        
    def test_delete_task(self):
        """Test task deletion"""
        self.login()
        self.create_task()
        
        # Get the task
        task = Task.query.filter_by(title='Test Task').first()
        
        # Delete the task
        response = self.client.post(
            f'/task/{task.id}/delete',
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task deleted successfully', response.data)
        
        # Check that task was deleted from database
        deleted_task = Task.query.get(task.id)
        self.assertIsNone(deleted_task)
        
    def test_toggle_task(self):
        """Test toggling task completion status"""
        self.login()
        self.create_task()
        
        # Get the task
        task = Task.query.filter_by(title='Test Task').first()
        self.assertFalse(task.completed)
        
        # Toggle the task
        response = self.client.post(
            f'/task/{task.id}/toggle',
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task status updated', response.data)
        
        # Check that task status was updated in database
        updated_task = Task.query.get(task.id)
        self.assertTrue(updated_task.completed)


if __name__ == '__main__':
    unittest.main() 