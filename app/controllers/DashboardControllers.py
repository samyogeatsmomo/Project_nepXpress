from flask import render_template, session, redirect, url_for, flash, get_flashed_messages, make_response
from functools import wraps


# ========== DECORATOR: Prevent page caching (disable back button) ==========
def no_cache(f):
    """Decorator to prevent page caching (disable back button)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function


# ========== DECORATOR: Require login ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


class DashboardController:  
    
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def dashboard(self):
        # CLEAR OLD FLASH MESSAGES
        get_flashed_messages()
        
        return render_template('dashboard.html')
    
    
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def admin_dashboard(self):
        # CLEAR OLD FLASH MESSAGES
        get_flashed_messages()
        
        return render_template('admin-dashboard.html')