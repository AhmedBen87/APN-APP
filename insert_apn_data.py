import csv
import os
import logging
from app import app, db
from models import APN

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_csv_value(value):
    """Clean CSV values by removing quotes and handling empty strings."""
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    # Remove quotes if they exist
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value.lower() == 'na' or value.lower() == "n/a":
        return None
    return value

def insert_apn_data():
    """Insert APN data from CSV file into the database."""
    csv_path = 'apn_data.csv'
    
    # Keep track of row count
    total_rows = 0
    inserted_rows = 0
    error_rows = 0
    skipped_rows = 0
    
    # Process in batches of 10
    BATCH_SIZE = 10
    batch_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            batch = []
            
            for row in csv_reader:
                total_rows += 1
                
                # Skip rows with no PIN_id or invalid PIN_id
                pin_id = clean_csv_value(row.get('PIN_id'))
                if not pin_id or not pin_id.isdigit():
                    logging.warning(f"Skipping row {total_rows}: Invalid PIN_id: {pin_id}")
                    skipped_rows += 1
                    continue
                
                # Check if APN already exists with the given PIN_id
                existing_apn = APN.query.filter_by(PIN_id=int(pin_id)).first()
                if existing_apn:
                    logging.info(f"APN with PIN_id {pin_id} already exists. Skipping.")
                    skipped_rows += 1
                    continue
                
                try:
                    # Create a new APN record
                    apn = APN(
                        PIN_id=int(pin_id),
                        DPN=clean_csv_value(row.get('DPN')),
                        Image=clean_csv_value(row.get('Image')),
                        Ref_Emdep=clean_csv_value(row.get('Ref_Emdep')),
                        Ref_Ingun=clean_csv_value(row.get('Ref_Ingun')),
                        Ref_Fenmmital=clean_csv_value(row.get('Ref_Fenmmital')),
                        Ref_Ptr=clean_csv_value(row.get('Ref_Ptr')),
                        Type=clean_csv_value(row.get('Type')),
                        Multi_APN=clean_csv_value(row.get('Multi_APN'))
                    )
                    
                    # Add the record to the session
                    db.session.add(apn)
                    batch.append(apn)
                    inserted_rows += 1
                    
                    # Commit every BATCH_SIZE records
                    if len(batch) >= BATCH_SIZE:
                        db.session.commit()
                        batch_count += 1
                        logging.info(f"Committed batch {batch_count} - Total records inserted so far: {inserted_rows}")
                        batch = []
                    
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error inserting row {total_rows} with PIN_id {pin_id}: {str(e)}")
                    error_rows += 1
            
            # Commit any remaining records
            if batch:
                try:
                    db.session.commit()
                    batch_count += 1
                    logging.info(f"Committed final batch {batch_count} - Total records inserted: {inserted_rows}")
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error committing final batch: {str(e)}")
        
        # Summary
        logging.info(f"Successfully completed data import!")
        logging.info(f"Total rows processed: {total_rows}")
        logging.info(f"Inserted rows: {inserted_rows}")
        logging.info(f"Skipped rows: {skipped_rows}")
        logging.info(f"Error rows: {error_rows}")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred during data import: {str(e)}")

# Create a CSV file from the provided data
def create_csv_from_data(data_path, output_path='apn_data.csv'):
    """Create a CSV file from the provided data file."""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        with open(output_path, 'w', encoding='utf-8', newline='') as csv_out:
            csv_out.write(data)
        
        logging.info(f"CSV file created at {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        # Path to the provided data file
        data_path = 'attached_assets/Pasted--PIN-id-DPN-Image-Ref-Emdep-Ref-Ingun-Ref-Fenmmital-Ref-Ptr-Type-Multi-APN-1-155-1743756318239.txt'
        
        # Create CSV file from the provided data
        if create_csv_from_data(data_path):
            # Insert data into the database
            insert_apn_data()
        else:
            logging.error("Failed to create CSV file. Data import aborted.")