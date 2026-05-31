import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from extensions import db, login_manager
from models.user import User
from models.customer import Customer
from models.service import Service
from models.subscription import Subscription
from models.notification import Notification
from functools import wraps

app = Flask(__name__)

# Configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Initialize Extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.customer import customer_bp
from routes.service import service_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(service_bp)
app.register_blueprint(admin_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin check decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Public Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for contacting us! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_ENV') != 'production')