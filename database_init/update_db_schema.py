import os
import sqlite3
import sys
from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///probes.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def update_schema():
    # Get the path to the SQLite database file
    app = create_app()
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    
    # Connect directly to the SQLite database
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(f"instance/{db_path}")
    cursor = conn.cursor()
    
    try:
        # Check if the users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table doesn't exist yet. No need to update schema.")
            return True
            
        # Check if role column already exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in columns:
            print("Adding 'role' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")
            conn.commit()
            print("Schema updated successfully!")
        else:
            print("Role column already exists. No need to update schema.")
            
        # Update all existing users to admin role
        cursor.execute("UPDATE users SET role = 'admin'")
        conn.commit()
        print("All existing users have been set to admin role.")
        
        return True
    except Exception as e:
        print(f"Error updating schema: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = update_schema()
    if not success:
        sys.exit(1)
    print("Database schema update completed.") 