from app import create_app
from models import APN
import os
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_apn_images():
    app = create_app()
    
    with app.app_context():
        # Get all APN records
        apns = APN.query.all()
        logging.info(f"Found {len(apns)} APN records")
        
        # Define the correct paths
        pin_source = os.path.join('attached_assets', 'APN', 'pin')
        apn_source = os.path.join('attached_assets', 'APN')
        pin_dest = os.path.join('static', 'apn_pin_images')
        apn_dest = os.path.join('static', 'apn_images')
        
        # Check if directories exist
        for path in [pin_source, apn_source, pin_dest, apn_dest]:
            if not os.path.exists(path):
                logging.warning(f"Directory does not exist: {path}")
                os.makedirs(path, exist_ok=True)
                logging.info(f"Created directory: {path}")
        
        for apn in apns:
            logging.info(f"\nAPN Record:")
            logging.info(f"ID: {apn.PIN_id}")
            logging.info(f"DPN: {apn.DPN}")
            logging.info(f"Image Path: {apn.Image}")
            
            if apn.Image:
                # Get the filename from the path
                filename = apn.Image.split('/')[-1]
                
                # Check if it's a pin image based on the Image path
                is_pin = '/pin/' in apn.Image
                source_folder = pin_source if is_pin else apn_source
                dest_folder = pin_dest if is_pin else apn_dest
                folder_type = "PIN" if is_pin else "APN"
                
                # Check source folder
                source_path = os.path.join(source_folder, filename)
                if os.path.exists(source_path):
                    logging.info(f"✓ Image found in {folder_type} source folder: {source_path}")
                else:
                    logging.warning(f"✗ Image NOT found in {folder_type} source folder: {source_path}")
                
                # Check destination folder
                dest_path = os.path.join(dest_folder, filename)
                if os.path.exists(dest_path):
                    logging.info(f"✓ Image found in {folder_type} destination folder: {dest_path}")
                else:
                    logging.warning(f"✗ Image NOT found in {folder_type} destination folder: {dest_path}")
                    
                    # If image exists in source but not in destination, copy it
                    if os.path.exists(source_path):
                        try:
                            shutil.copy2(source_path, dest_path)
                            logging.info(f"✓ Copied image from source to destination")
                        except Exception as e:
                            logging.error(f"Error copying image: {str(e)}")

if __name__ == '__main__':
    check_apn_images() 