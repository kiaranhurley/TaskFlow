from datetime import datetime

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import Task, TaskCategory, TaskShare, User

# Create blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# Main routes
@main.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/tasks')
@login_required
def tasks():
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    now = datetime.utcnow()
    return render_template('tasks.html', tasks=tasks, categories=categories, now=now)

@main.route('/dashboard')
@login_required
def dashboard():
    # Get current user's tasks
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    
    # Calculate statistics
    now = datetime.utcnow()
    stats = {
        'total_tasks': len(tasks),
        'completed_tasks': sum(1 for task in tasks if task.status == 'completed'),
        'in_progress_tasks': sum(1 for task in tasks if task.status == 'in_progress'),
        'overdue_tasks': sum(1 for task in tasks if task.due_date and task.due_date < now and task.status != 'completed'),
        'priority_high': sum(1 for task in tasks if task.priority == 3),
        'priority_medium': sum(1 for task in tasks if task.priority == 2),
        'priority_low': sum(1 for task in tasks if task.priority == 1)
    }
    
    # Prepare category data for chart
    category_names = [category.name for category in categories]
    category_counts = [len(category.tasks) for category in categories]
    category_colors = [category.color for category in categories]
    
    # Get recent activity (last 10 changes)
    recent_activity = []
    for task in tasks:
        if task.status == 'completed':
            recent_activity.append({
                'task_title': task.title,
                'action': 'Completed',
                'timestamp': task.completion_date or task.last_modified
            })
        elif task.status == 'in_progress':
            recent_activity.append({
                'task_title': task.title,
                'action': 'Started',
                'timestamp': task.last_modified
            })
        
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_activity[:10]
    
    return render_template('dashboard.html',
                         stats=stats,
                         category_names=category_names,
                         category_counts=category_counts,
                         category_colors=category_colors,
                         recent_activity=recent_activity)

@main.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        priority = int(request.form.get('priority', 1))
        status = request.form.get('status', 'pending')
        category_ids = request.form.getlist('categories[]')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('task_form.html', categories=categories)
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status,
            user_id=current_user.id
        )
        
        # Add selected categories
        if category_ids:
            categories = TaskCategory.query.filter(
                TaskCategory.id.in_(category_ids),
                TaskCategory.user_id == current_user.id
            ).all()
            task.categories.extend(categories)
        
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('task_form.html', categories=categories)

@main.route('/task/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.', 'error')
        return redirect(url_for('main.index'))
    
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        task.title = request.form.get('title', task.title)
        task.description = request.form.get('description', task.description)
        task.priority = int(request.form.get('priority', task.priority))
        task.status = request.form.get('status', task.status)
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('task_form.html', task=task, categories=categories)
        else:
            task.due_date = None
        
        # Update categories
        category_ids = request.form.getlist('categories[]')
        task.categories = []
        if category_ids:
            categories = TaskCategory.query.filter(
                TaskCategory.id.in_(category_ids),
                TaskCategory.user_id == current_user.id
            ).all()
            task.categories.extend(categories)
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('task_form.html', task=task, categories=categories)

@main.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    
    # Check if the current user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task.', 'danger')
        return redirect(url_for('main.index'))
    
    # Toggle between completed and pending
    if task.status == 'completed':
        task.status = 'pending'
        task.completion_date = None
    else:
        task.status = 'completed'
        task.completion_date = datetime.utcnow()
    
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('main.index'))

@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if the current user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('main.tasks'))
    
    # Delete all shares associated with this task
    TaskShare.query.filter_by(task_id=task_id).delete()
    
    # Delete the task
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.tasks'))

# Authentication routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Form validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@main.route('/categories', methods=['GET'])
@login_required
def list_categories():
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories)

@main.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#808080')
        
        if name:
            category = TaskCategory(name=name, color=color, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('main.list_categories'))
    
    return render_template('category_form.html')

@main.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = TaskCategory.query.get_or_404(id)
    if category.user_id != current_user.id:
        flash('You do not have permission to edit this category.', 'error')
        return redirect(url_for('main.list_categories'))
    
    if request.method == 'POST':
        category.name = request.form.get('name', category.name)
        category.color = request.form.get('color', category.color)
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.list_categories'))
    
    return render_template('category_form.html', category=category)

@main.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = TaskCategory.query.get_or_404(id)
    if category.user_id != current_user.id:
        flash('You do not have permission to delete this category.', 'error')
        return redirect(url_for('main.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.list_categories'))

@main.route('/tasks/filter')
@login_required
def filter_tasks():
    # Get filter parameters
    status = request.args.get('status')
    priority = request.args.get('priority')
    category_id = request.args.get('category')
    sort_by = request.args.get('sort_by', 'created_at')

    # Start with base query
    query = Task.query.filter_by(user_id=current_user.id)

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=int(priority))
    if category_id:
        query = query.filter(Task.categories.any(id=int(category_id)))

    # Apply sorting
    if sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc())
    elif sort_by == 'priority':
        query = query.order_by(Task.priority.desc())
    elif sort_by == 'title':
        query = query.order_by(Task.title.asc())
    else:  # default to created_at
        query = query.order_by(Task.created_at.desc())

    # Execute query
    tasks = query.all()
    
    # Get categories for the filter dropdown
    categories = TaskCategory.query.filter_by(user_id=current_user.id).all()
    
    # Get current time for overdue detection
    now = datetime.utcnow()

    return render_template('tasks.html', 
                         tasks=tasks,
                         categories=categories,
                         now=now)

@main.route('/tasks/<int:id>/share', methods=['POST'])
@login_required
def share_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have permission to share this task.', 'error')
        return redirect(url_for('main.index'))
    
    share_email = request.form.get('share_email')
    permission = request.form.get('permission', 'view')
    
    if not share_email:
        flash('Please provide an email address.', 'error')
        return redirect(url_for('main.index'))
    
    # Find user by email
    user_to_share_with = User.query.filter_by(email=share_email).first()
    if not user_to_share_with:
        flash('User not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if task is already shared with this user
    existing_share = TaskShare.query.filter_by(
        task_id=task.id,
        shared_with_id=user_to_share_with.id
    ).first()
    
    if existing_share:
        flash('Task is already shared with this user.', 'warning')
        return redirect(url_for('main.index'))
    
    # Create new share
    share = TaskShare(
        task_id=task.id,
        shared_by_id=current_user.id,
        shared_with_id=user_to_share_with.id,
        permission=permission
    )
    
    task.is_shared = True
    if not task.share_link:
        task.generate_share_link()
    
    db.session.add(share)
    db.session.commit()
    
    flash(f'Task shared with {share_email}!', 'success')
    return redirect(url_for('main.index'))

@main.route('/task/<int:task_id>/generate-share-link', methods=['POST'])
@login_required
def generate_share_link(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    task.generate_share_link()
    db.session.commit()
    
    share_link = url_for('main.view_shared_task', share_link=task.share_link, _external=True)
    return jsonify({'success': True, 'share_link': share_link})

@main.route('/task/<int:task_id>/share/<int:share_id>/remove', methods=['POST'])
@login_required
def remove_share(task_id, share_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    share = TaskShare.query.get_or_404(share_id)
    db.session.delete(share)
    
    # If this was the last share, update task.is_shared
    remaining_shares = TaskShare.query.filter_by(task_id=task_id).count()
    if remaining_shares == 0:
        task.is_shared = False
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/shared-task/<share_link>')
def view_shared_task(share_link):
    task = Task.query.filter_by(share_link=share_link).first_or_404()
    
    # Check if user has explicit share permission
    share = None
    if current_user.is_authenticated:
        share = TaskShare.query.filter_by(
            task_id=task.id,
            shared_with_id=current_user.id
        ).first()
    
    can_edit = share and share.permission == 'edit'
    
    return render_template('shared_task.html', task=task, can_edit=can_edit)

@main.route('/shared-with-me')
@login_required
def shared_with_me():
    shared_tasks = TaskShare.query.filter_by(shared_with_id=current_user.id).all()
    return render_template('shared_with_me.html', shared_tasks=shared_tasks)

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.change_password'))
            
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password has been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('change_password.html')

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.generate_reset_token()
            # For development, we'll just show the reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Password reset link (for development): {reset_url}', 'info')
            return redirect(url_for('auth.login'))
        
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.is_reset_token_valid():
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('set_new_password.html', token=token)
        
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('set_new_password.html', token=token) 