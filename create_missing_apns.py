import logging
from app import app, db
from models import APN

# Set up logging
logging.basicConfig(level=logging.INFO)

def create_missing_apns():
    """Create missing APN records for foreign key references"""
    
    # List of APN IDs needed based on CP data analysis
    missing_apn_ids = [43, 44, 45, 46, 47, 48, 50, 51, 54, 55, 57, 60, 61, 62, 63, 64]
    
    # Track results
    created_count = 0
    skipped_count = 0
    
    for pin_id in missing_apn_ids:
        # Check if already exists
        existing = APN.query.filter_by(PIN_id=pin_id).first()
        if existing:
            logging.info(f"APN with PIN_id {pin_id} already exists. Skipping.")
            skipped_count += 1
            continue
        
        # Create a new APN record with the PIN_id
        apn = APN(
            PIN_id=pin_id,
            DPN=f"DPN-{pin_id}",
            Image=f"/pin/default_{pin_id}.jpg",
            Type="PIN"  # Default type
        )
        
        db.session.add(apn)
        created_count += 1
        
        logging.info(f"Created APN record for PIN_id {pin_id}")
    
    # Commit changes
    try:
        db.session.commit()
        logging.info(f"Successfully created {created_count} missing APN records.")
        logging.info(f"Skipped {skipped_count} existing records.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error committing new APN records: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        create_missing_apns()