from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import Task, User

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing tasks"""
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    return render_template('dashboard.html', tasks=tasks)

@main.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    """Create a new task"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        priority = int(request.form.get('priority', 1))
        
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('new_task.html')

@main.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task"""
    task = Task.query.get_or_404(task_id)
    
    # Check if the current user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        task.priority = int(request.form.get('priority', 1))
        
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        else:
            task.due_date = None
            
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('edit_task.html', task=task)

@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    
    # Check if the current user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    
    # Check if the current user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    task.completed = not task.completed
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('main.dashboard')) 