import os
import sys
from getpass import getpass
from flask import Flask
from extensions import db
from models import User

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///probes.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def add_first_user(username, employee_id, password=None, role='admin'):
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists!")
            return False
            
        # Create new user
        new_user = User(username=username, employee_id=employee_id, role=role)
        
        # If password not provided, prompt securely
        if not password:
            while True:
                password = getpass("Enter password: ")
                password_confirm = getpass("Confirm password: ")
                
                if password == password_confirm:
                    break
                print("Passwords don't match. Try again.")
        
        new_user.set_password(password)
        
        # Add and commit to database
        db.session.add(new_user)
        db.session.commit()
        
        print(f"User {username} created successfully with role: {role}!")
        return True

if __name__ == "__main__":
    # Set default values
    default_username = "Ahmed Benmimoun"
    default_employee_id = "2465"
    
    if len(sys.argv) > 1:
        # Command-line arguments: username employee_id [password]
        username = sys.argv[1]
        employee_id = sys.argv[2] if len(sys.argv) > 2 else default_employee_id
        password = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Use defaults for quick setup
        username = default_username
        employee_id = default_employee_id
        password = None
        
    success = add_first_user(username, employee_id, password)
    if not success:
        sys.exit(1) 