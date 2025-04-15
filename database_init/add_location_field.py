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
        # Check if the Location column already exists in APN table
        cursor.execute("PRAGMA table_info(APN)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'Location' not in columns:
            print("Adding 'Location' column to APN table...")
            cursor.execute("ALTER TABLE APN ADD COLUMN Location TEXT")
            conn.commit()
            print("Schema updated successfully!")
            
            # Add some sample locations for testing (optional)
            print("Adding sample location data...")
            
            # Get all APN IDs first
            cursor.execute("SELECT PIN_id FROM APN")
            apn_ids = [row[0] for row in cursor.fetchall()]
            
            # Assign some sample locations - in real implementation, use actual data
            cabinets = ['A', 'B', 'C', 'D', 'E']
            for i, apn_id in enumerate(apn_ids):
                cabinet = cabinets[i % len(cabinets)]
                drawer = f"{(i % 12) + 1:02d}"  # 01 through 12
                location = f"ARMOIRE {cabinet}-{drawer}"
                
                cursor.execute("UPDATE APN SET Location = ? WHERE PIN_id = ?", (location, apn_id))
                
                if i < 5:  # Just log a few to confirm
                    print(f"Set APN ID {apn_id} location to: {location}")
            
            conn.commit()
            print(f"Added sample locations to {len(apn_ids)} APNs")
        else:
            print("Location column already exists. No need to update schema.")
            
            # Update existing locations to ensure they have the ARMOIRE prefix
            cursor.execute("SELECT PIN_id, Location FROM APN WHERE Location IS NOT NULL")
            locations = cursor.fetchall()
            
            updated_count = 0
            for pin_id, location in locations:
                if location and not location.startswith("ARMOIRE "):
                    # If it's like "C-07", convert to "ARMOIRE C-07"
                    parts = location.split('-')
                    if len(parts) == 2:
                        cabinet, drawer = parts
                        new_location = f"ARMOIRE {cabinet.strip()}-{drawer.strip()}"
                        cursor.execute("UPDATE APN SET Location = ? WHERE PIN_id = ?", (new_location, pin_id))
                        updated_count += 1
            
            if updated_count > 0:
                conn.commit()
                print(f"Updated {updated_count} locations to include ARMOIRE prefix")
            
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