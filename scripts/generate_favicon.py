import os
from PIL import Image, ImageDraw

def create_favicon():
    """Create a simple red circle favicon.ico file"""
    # Create directories if they don't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Create images of different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create a transparent image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a red circle
        padding = int(size * 0.1)  # 10% padding
        draw.ellipse(
            [(padding, padding), (size - padding, size - padding)],
            fill=(255, 0, 0, 255)  # Red circle
        )
        
        images.append(img)
    
    # Save as ICO (multi-size)
    favicon_path = 'static/images/favicon.ico'
    images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(size, size) for size in sizes],
        append_images=images[1:]
    )
    
    print(f"Favicon created successfully: {favicon_path}")

if __name__ == "__main__":
    create_favicon() 