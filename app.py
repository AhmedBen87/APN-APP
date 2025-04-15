import os
import logging
import sys
from flask import Flask, send_from_directory
from extensions import db
from models import APN, CP, User
from flask_login import LoginManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    try:
        # Create the app
        app = Flask(__name__)
        app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

        # Configure the SQLite database
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///probes.db")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }

        # Configure static file paths
        app.config['CP_IMAGES_FOLDER'] = os.path.join(app.root_path, 'static', 'cp_images')
        app.config['CP_SUB51_IMAGES_FOLDER'] = os.path.join(app.root_path, 'static', 'cp_sub51_images')
        app.config['APN_IMAGES_FOLDER'] = os.path.join(app.root_path, 'static', 'apn_images')
        app.config['APN_PIN_IMAGES_FOLDER'] = os.path.join(app.root_path, 'static', 'apn_pin_images')

        # Create image directories if they don't exist
        os.makedirs(app.config['CP_IMAGES_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CP_SUB51_IMAGES_FOLDER'], exist_ok=True)
        os.makedirs(app.config['APN_IMAGES_FOLDER'], exist_ok=True)
        os.makedirs(app.config['APN_PIN_IMAGES_FOLDER'], exist_ok=True)

        # Initialize the app with the extension
        db.init_app(app)
        
        # Initialize Flask-Login
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        login_manager.login_message = 'Please log in to access this page.'
        login_manager.login_message_category = 'warning'
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Create tables
        with app.app_context():
            db.create_all()

        # Register routes
        from routes import register_routes
        register_routes(app)

        return app
    except Exception as e:
        logging.error(f"Error creating Flask application: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        logging.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
        raise

if __name__ == '__main__':
    try:
        app = create_app()
        logging.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Fatal error in application: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        logging.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
        sys.exit(1)
