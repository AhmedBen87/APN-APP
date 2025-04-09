import os
import shutil
import logging
import sys

# Set up logging to output to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('apn_image_copy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def setup_directories():
    """Create necessary directories and provide setup instructions."""
    # Create attached_assets directory if it doesn't exist
    if not os.path.exists('attached_assets'):
        os.makedirs('attached_assets', exist_ok=True)
        logging.info("Created attached_assets directory")
    
    # Create APN and APN/pin directories inside attached_assets
    apn_source = os.path.join('attached_assets', 'APN')
    apn_pin_source = os.path.join('attached_assets', 'APN', 'pin')
    
    os.makedirs(apn_source, exist_ok=True)
    os.makedirs(apn_pin_source, exist_ok=True)
    
    # Create static image directories
    apn_dest = os.path.join('static', 'apn_images')
    apn_pin_dest = os.path.join('static', 'apn_pin_images')
    
    os.makedirs(apn_dest, exist_ok=True)
    os.makedirs(apn_pin_dest, exist_ok=True)
    
    logging.info("\nDirectory structure has been created:")
    logging.info(f"1. Regular APN images directory: {os.path.abspath(apn_source)}")
    logging.info(f"2. PIN APN images directory: {os.path.abspath(apn_pin_source)}")
    
    return apn_source, apn_pin_source, apn_dest, apn_pin_dest

def copy_images():
    """Copy images from source to destination directories."""
    logging.info("Starting APN image copy process...\n")
    
    # Setup directories and get paths
    apn_source, apn_pin_source, apn_dest, apn_pin_dest = setup_directories()
    
    # Copy regular APN images
    apn_copied = 0
    if os.path.exists(apn_source):
        for filename in os.listdir(apn_source):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    src_path = os.path.join(apn_source, filename)
                    dst_path = os.path.join(apn_dest, filename)
                    shutil.copy2(src_path, dst_path)
                    apn_copied += 1
                    logging.info(f"Copied {filename} to APN images directory")
                except Exception as e:
                    logging.error(f"Error copying {filename}: {str(e)}")
    
    # Copy PIN APN images
    pin_copied = 0
    if os.path.exists(apn_pin_source):
        for filename in os.listdir(apn_pin_source):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    src_path = os.path.join(apn_pin_source, filename)
                    dst_path = os.path.join(apn_pin_dest, filename)
                    shutil.copy2(src_path, dst_path)
                    pin_copied += 1
                    logging.info(f"Copied {filename} to APN PIN images directory")
                except Exception as e:
                    logging.error(f"Error copying {filename}: {str(e)}")

    # Print summary
    logging.info("\nCopy process completed!")
    logging.info(f"APN images copied: {apn_copied}")
    logging.info(f"APN PIN images copied: {pin_copied}")
    
    if apn_copied == 0 and pin_copied == 0:
        logging.warning("\nNo images were copied!")
        logging.info("\nTo set up the images:")
        logging.info("1. Place regular APN images in the APN folder:")
        logging.info(f"   {os.path.abspath(apn_source)}")
        logging.info("\n2. Place PIN APN images in the APN/pin folder:")
        logging.info(f"   {os.path.abspath(apn_pin_source)}")
        logging.info("\n3. Image files should have .jpg, .jpeg, or .png extensions")
        logging.info("\n4. Run this script again after adding the images")
        logging.info("\nNote: A log file 'apn_image_copy.log' has been created with these instructions")

if __name__ == '__main__':
    copy_images() 