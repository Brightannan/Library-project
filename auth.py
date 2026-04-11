from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
import logging

auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'librarian']:
            flash('Librarian access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User {username} logged in successfully")
            
            # Log the login
            log = Log(
                user_id=user.id,
                action='LOGIN',
                details=f'User {username} logged in',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Log the logout
    log = Log(
        user_id=current_user.id,
        action='LOGOUT',
        details=f'User {current_user.username} logged out',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            
            # Log password change
            log = Log(
                user_id=current_user.id,
                action='PASSWORD_CHANGE',
                details='User changed password',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('main.profile'))
    
    return render_template('change_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user:
            # In a real application, you would send an email with reset link
            token = user.generate_reset_token()
            # Store token in database or cache
            flash('Password reset instructions sent to your email', 'info')
        else:
            flash('Email not found', 'danger')
    
    return render_template('reset_password.html')