#!/usr/bin/env python3
"""Create simple placeholder icons for Chrome extension"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    # Create image with blue background
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)

    # Draw white circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='white')

    # Draw blue 'M' in center (simplified - just use a smaller circle for now)
    inner_margin = size // 4
    draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], fill='#007bff')

    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

if __name__ == '__main__':
    import os
    os.chdir('icons')

    try:
        create_icon(16, 'icon16.png')
        create_icon(48, 'icon48.png')
        create_icon(128, 'icon128.png')
        print("\n✓ All icons created successfully!")
    except ImportError:
        print("ERROR: PIL/Pillow not installed")
        print("Install with: pip install Pillow")
        print("\nAlternatively, create placeholder icons manually:")
        print("  - icon16.png (16x16)")
        print("  - icon48.png (48x48)")
        print("  - icon128.png (128x128)")
