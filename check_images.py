from app import create_app
from models import CP
import os
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_images():
    app = create_app()
    
    with app.app_context():
        # Get all CP records
        cps = CP.query.all()
        logging.info(f"Found {len(cps)} CP records")
        
        # Define the correct paths
        cp_source = os.path.join('attached_assets', 'CP')
        cp_sub51_source = os.path.join('attached_assets', 'CP_SUB51')
        cp_dest = os.path.join('static', 'cp_images')
        cp_sub51_dest = os.path.join('static', 'cp_sub51_images')
        
        # Check if directories exist
        for path in [cp_source, cp_sub51_source, cp_dest, cp_sub51_dest]:
            if not os.path.exists(path):
                logging.warning(f"Directory does not exist: {path}")
                os.makedirs(path, exist_ok=True)
                logging.info(f"Created directory: {path}")
        
        for cp in cps:
            logging.info(f"\nCP Record:")
            logging.info(f"ID: {cp.CP_ID}")
            logging.info(f"CP Name: {cp.CP}")
            logging.info(f"Image Path: {cp.Image}")
            
            if cp.Image:
                # Get the filename from the path
                filename = cp.Image.split('/')[-1]
                
                # Check if it's a SUB51 CP based on the Image path
                is_sub51 = '/CP_SUB51/' in cp.Image
                source_folder = cp_sub51_source if is_sub51 else cp_source
                dest_folder = cp_sub51_dest if is_sub51 else cp_dest
                folder_type = "CP_SUB51" if is_sub51 else "CP"
                
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
            else:
                logging.warning("No image path in database")

if __name__ == '__main__':
    check_images() 