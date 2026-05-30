from flask import Flask, render_template, session, redirect, url_for, flash, request, get_flashed_messages, make_response
from app.routes.authroutes import Authroutes
from app.models.database import Database
from app.models.UserModel import User
from functools import wraps
import config
import os


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


def create_app():
    # Get project paths
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(app_dir)
    
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    
    # Create Flask app
    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )
    
    # Set secret key for session management
    app.secret_key = config.SECRET_KEY
    
    # Create database tables on app startup
    with app.app_context():
        Database.create_tables()
    
    # Register authentication routes (login, register, settings)
    auth_routes = Authroutes()
    app.register_blueprint(auth_routes.login())

    
    # ========== PUBLIC ROUTES (No authentication required) ==========
    
    @app.route("/")
    def home():
        """Home page - redirects to login"""
        return render_template("login.html")
    
    
    # ========== PROTECTED ROUTES (Require login) ==========
    
    @app.route("/dashboard")
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def dashboard():
        """User dashboard - requires login"""
        get_flashed_messages()  # Clear old messages
        return render_template("dashboard.html")
    
    
    @app.route("/create-shipment")
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def create_shipment():
        """Create shipment page - requires login"""
        get_flashed_messages()  # Clear old messages
        return render_template("create-shipment.html")
    
    
    @app.route("/shipment-history")
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def shipment_history():
        """Shipment history page - requires login"""
        get_flashed_messages()  # Clear old messages
        return render_template("shipment-history.html")

    
    @app.route("/settings")
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def settings():
        """Settings page - requires login"""
        get_flashed_messages()  # Clear old messages
        return render_template("settings.html")

    
    @app.route("/admin-dashboard")
    @no_cache  # ← ADD THIS: Prevent back button
    @login_required  # ← ADD THIS: Require login
    def admin_dashboard():
        """Admin dashboard - requires login AND admin role"""
        if session.get("user_role") != "admin":
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for("dashboard"))
        get_flashed_messages()  # Clear old messages
        return render_template("admin-dashboard.html")

    
    # ========== LOGOUT ROUTE - WITH PASSWORD CONFIRMATION ==========
    
    @app.route("/logout", methods=["GET", "POST"])
    @login_required  # ← Require login to access logout
    def logout():
        """Logout with password confirmation"""
        get_flashed_messages()  # Clear old messages
        
        # GET request: show logout confirmation form
        if request.method == "GET":
            return render_template("logout.html")
        
        # POST request: verify password and logout
        if request.method == "POST":
            password = request.form.get("password", "").strip()
            
            # Check if password is provided
            if not password:
                flash("Password is required to logout.", "danger")
                return render_template("logout.html")
            
            # Get current user from session
            user_email = session.get("user_email")
            
            # Verify password
            user = User(email=user_email)
            user_data = user.find_by("email", user_email)
            
            if not user_data:
                flash("User not found.", "danger")
                return render_template("logout.html")
            
            # Check if password is correct
            if not user.check_password(password):
                flash("Incorrect password. Please try again.", "danger")
                return render_template("logout.html")
            
            # PASSWORD CORRECT: Clear session and logout
            session.clear()
            flash("You have been logged out successfully.", "success")
            return redirect(url_for("auth.login"))

   
    # ========== ERROR HANDLERS ==========
    
    @app.errorhandler(404)
    def error(e):
        """Handle 404 errors"""
        return render_template("error.html"), 404
    
    
    return app