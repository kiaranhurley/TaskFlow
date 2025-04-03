import secrets
from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

# Task-Category Association Table
task_categories = db.Table('task_categories',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('task_category.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='user', lazy=True)
    categories = db.relationship('TaskCategory', backref='user', lazy=True)
    # Add profile fields
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expires_in=3600):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return self.reset_token
    
    def is_reset_token_valid(self):
        return self.reset_token_expiry and self.reset_token_expiry > datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'

class TaskCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#808080")  # Hex color code
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)  # 1=Low, 2=Medium, 3=High
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, archived
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    is_shared = db.Column(db.Boolean, default=False)
    share_link = db.Column(db.String(100), unique=True, nullable=True)
    categories = db.relationship('TaskCategory', secondary=task_categories, lazy='dynamic',
                               backref=db.backref('tasks', lazy=True))
    shared_with = db.relationship('TaskShare', back_populates='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.title}>'

    def generate_share_link(self):
        """Generate a unique share link for the task"""
        if not self.share_link:
            self.share_link = secrets.token_urlsafe(16)
        return self.share_link

class TaskShare(db.Model):
    __tablename__ = 'task_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    shared_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission = db.Column(db.String(20), default='view')  # view, edit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', back_populates='shared_with')
    shared_by = db.relationship('User', 
                              foreign_keys=[shared_by_id],
                              backref=db.backref('tasks_shared_by_me', lazy=True))
    shared_with = db.relationship('User', 
                                foreign_keys=[shared_with_id],
                                backref=db.backref('tasks_shared_with_me', lazy=True))

    def __repr__(self):
        return f'<TaskShare {self.task_id} - {self.shared_with_id}>' 