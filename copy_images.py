import os
import shutil
import logging
import sys

# Set up logging to output to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('image_copy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def setup_directories():
    """Create necessary directories and provide setup instructions."""
    # Create attached_assets directory if it doesn't exist
    if not os.path.exists('attached_assets'):
        os.makedirs('attached_assets', exist_ok=True)
        logging.info("Created attached_assets directory")
    
    # Create CP and CP_SUB51 directories inside attached_assets
    cp_source = os.path.join('attached_assets', 'CP')
    cp_sub51_source = os.path.join('attached_assets', 'CP_SUB51')
    
    os.makedirs(cp_source, exist_ok=True)
    os.makedirs(cp_sub51_source, exist_ok=True)
    
    # Create static image directories
    cp_dest = os.path.join('static', 'cp_images')
    cp_sub51_dest = os.path.join('static', 'cp_sub51_images')
    
    os.makedirs(cp_dest, exist_ok=True)
    os.makedirs(cp_sub51_dest, exist_ok=True)
    
    logging.info("\nDirectory structure has been created:")
    logging.info(f"1. Regular CP images directory: {os.path.abspath(cp_source)}")
    logging.info(f"2. SUB51 CP images directory: {os.path.abspath(cp_sub51_source)}")
    
    return cp_source, cp_sub51_source, cp_dest, cp_sub51_dest

def copy_images():
    """Copy images from source to destination directories."""
    logging.info("Starting image copy process...\n")
    
    # Setup directories and get paths
    cp_source, cp_sub51_source, cp_dest, cp_sub51_dest = setup_directories()
    
    # Copy CP images
    cp_copied = 0
    if os.path.exists(cp_source):
        for filename in os.listdir(cp_source):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    src_path = os.path.join(cp_source, filename)
                    dst_path = os.path.join(cp_dest, filename)
                    shutil.copy2(src_path, dst_path)
                    cp_copied += 1
                    logging.info(f"Copied {filename} to CP images directory")
                except Exception as e:
                    logging.error(f"Error copying {filename}: {str(e)}")
    
    # Copy CP_SUB51 images
    sub51_copied = 0
    if os.path.exists(cp_sub51_source):
        for filename in os.listdir(cp_sub51_source):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    src_path = os.path.join(cp_sub51_source, filename)
                    dst_path = os.path.join(cp_sub51_dest, filename)
                    shutil.copy2(src_path, dst_path)
                    sub51_copied += 1
                    logging.info(f"Copied {filename} to CP_SUB51 images directory")
                except Exception as e:
                    logging.error(f"Error copying {filename}: {str(e)}")

    # Print summary
    logging.info("\nCopy process completed!")
    logging.info(f"CP images copied: {cp_copied}")
    logging.info(f"CP_SUB51 images copied: {sub51_copied}")
    
    if cp_copied == 0 and sub51_copied == 0:
        logging.warning("\nNo images were copied!")
        logging.info("\nTo set up the images:")
        logging.info("1. Place regular CP images in the CP folder:")
        logging.info(f"   {os.path.abspath(cp_source)}")
        logging.info("\n2. Place SUB51 CP images in the CP_SUB51 folder:")
        logging.info(f"   {os.path.abspath(cp_sub51_source)}")
        logging.info("\n3. Image files should have .jpg, .jpeg, or .png extensions")
        logging.info("\n4. Run this script again after adding the images")
        logging.info("\nNote: A log file 'image_copy.log' has been created with these instructions")

if __name__ == '__main__':
    copy_images() 