import pandas as pd
import os
import sqlite3
from flask import Flask
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///probes.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return app

def update_locations():
    # Path to Excel file - adjusted for new location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, "EMPLACEMENT le 15.03.2025 (3).xlsx")
    sheet_name = "Emp"
    
    # Check if the Excel file exists
    if not os.path.exists(excel_file):
        logging.error(f"Excel file not found: {excel_file}")
        return False
    
    logging.info(f"Reading data from Excel file: {excel_file}")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Print column names for debugging
        logging.info(f"Excel columns: {df.columns.tolist()}")
        
        # Find APN column (Column B)
        apn_column = 'APN'
        if apn_column not in df.columns:
            logging.error(f"APN column not found. Available columns: {df.columns.tolist()}")
            return False
        
        # Find Location column (Column G - "Emplacement ")
        location_column = None
        for col in df.columns:
            if 'EMPLACE' in str(col).upper():
                location_column = col
                logging.info(f"Found Location column: {col}")
                break
        
        if not location_column:
            location_column = df.columns[6]  # Column G
            logging.info(f"Using column position G for Location: {location_column}")
        
        # Find Process column (Column I - "PROCESS")
        process_column = 'PROCESS'
        if process_column not in df.columns:
            logging.error(f"PROCESS column not found. Available columns: {df.columns.tolist()}")
            return False
        
        # Filter rows where PROCESS column contains "ROB"
        rob_df = df[df[process_column].astype(str).str.contains('ROB', na=False)]
        logging.info(f"Found {len(rob_df)} rows with PROCESS='ROB'")
        
        # Get database path
        app = create_app()
        db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        
        # Adjust database path to point to parent directory
        parent_dir = os.path.dirname(script_dir)
        db_full_path = os.path.join(parent_dir, "instance", db_path)
        
        # Check if database exists
        if not os.path.exists(db_full_path):
            logging.error(f"Database file not found: {db_full_path}")
            return False
            
        logging.info(f"Connecting to database: {db_full_path}")
        conn = sqlite3.connect(db_full_path)
        cursor = conn.cursor()
        
        # Get APN and location data
        locations_data = []
        for _, row in rob_df.iterrows():
            apn = str(row[apn_column]).strip()
            location = str(row[location_column]).strip()
            
            # Only add entries that have valid data
            if apn and location and pd.notna(apn) and pd.notna(location):
                # Make sure location is in the correct format
                if not location.startswith("ARMOIRE "):
                    location = f"ARMOIRE {location}"
                locations_data.append((apn, location))
        
        logging.info(f"Found {len(locations_data)} valid APN and location pairs")
        
        # Print first few entries for verification
        for i, (apn, location) in enumerate(locations_data[:5]):
            logging.info(f"Sample data {i+1}: APN={apn}, Location={location}")
        
        # Check if the APN table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='APN'")
        if not cursor.fetchone():
            logging.error("APN table does not exist in the database")
            return False
        
        # Update database
        update_count = 0
        not_found_count = 0
        not_found_apns = []
        
        for apn, location in locations_data:
            # Try to find matching APN in database
            cursor.execute("SELECT PIN_id, DPN FROM APN WHERE CAST(DPN AS TEXT) = ?", (apn,))
            apn_record = cursor.fetchone()
            
            if apn_record:
                pin_id = apn_record[0]
                cursor.execute("UPDATE APN SET Location = ? WHERE PIN_id = ?", (location, pin_id))
                update_count += 1
                if update_count % 10 == 0:
                    logging.info(f"Updated {update_count} records so far...")
            else:
                not_found_count += 1
                if len(not_found_apns) < 10:  # Only store first 10 for logging
                    not_found_apns.append(apn)
        
        conn.commit()
        logging.info(f"Successfully updated {update_count} APN locations")
        
        if not_found_count > 0:
            logging.warning(f"Could not find {not_found_count} APNs in the database")
            logging.warning(f"Examples of APNs not found: {', '.join(not_found_apns[:10])}")
        
        # Close database connection
        conn.close()
        
    except Exception as e:
        logging.error(f"Error updating locations: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    logging.info("Starting APN location update process")
    success = update_locations()
    if success:
        logging.info("APN location update process completed successfully")
    else:
        logging.error("APN location update process failed")
        sys.exit(1) 