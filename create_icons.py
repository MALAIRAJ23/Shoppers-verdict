#!/usr/bin/env python3
"""
Generate placeholder icons for Shopper's Verdict browser extension
Creates 16x16, 48x48, and 128x128 PNG icons with a shopping cart theme
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon(size, filename):
        """Create a simple shopping cart icon"""
        # Create image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Define colors - gradient from #667eea to #764ba2
        primary_color = (102, 126, 234, 255)  # #667eea
        secondary_color = (118, 75, 162, 255)  # #764ba2
        
        # Scale measurements based on icon size
        scale = size / 16.0
        
        # Draw shopping cart outline
        # Cart body (rectangle)
        cart_left = int(2 * scale)
        cart_top = int(6 * scale)
        cart_right = int(12 * scale)
        cart_bottom = int(10 * scale)
        
        # Cart outline
        draw.rectangle([cart_left, cart_top, cart_right, cart_bottom], 
                      outline=primary_color, width=max(1, int(scale)))
        
        # Cart handle
        handle_start = int(1 * scale)
        handle_end = int(4 * scale)
        handle_y = int(8 * scale)
        draw.line([handle_start, handle_y, handle_end, handle_y], 
                  fill=primary_color, width=max(1, int(scale)))
        
        # Cart wheels
        wheel1_x = int(4 * scale)
        wheel2_x = int(10 * scale)
        wheel_y = int(12 * scale)
        wheel_radius = max(1, int(1.5 * scale))
        
        # Draw wheels as circles
        draw.ellipse([wheel1_x - wheel_radius, wheel_y - wheel_radius,
                     wheel1_x + wheel_radius, wheel_y + wheel_radius],
                    fill=secondary_color)
        draw.ellipse([wheel2_x - wheel_radius, wheel_y - wheel_radius,
                     wheel2_x + wheel_radius, wheel_y + wheel_radius],
                    fill=secondary_color)
        
        # Add a checkmark or verdict symbol
        if size >= 32:
            # Add checkmark for larger icons
            check_color = (76, 175, 80, 255)  # Green
            check_x = int(8 * scale)
            check_y = int(3 * scale)
            check_size = max(2, int(2 * scale))
            
            # Simple checkmark
            draw.line([check_x, check_y + check_size, 
                      check_x + check_size//2, check_y + check_size + check_size//2], 
                     fill=check_color, width=max(1, int(scale)))
            draw.line([check_x + check_size//2, check_y + check_size + check_size//2,
                      check_x + check_size, check_y], 
                     fill=check_color, width=max(1, int(scale)))
        
        # Save the image
        img.save(filename, 'PNG')
        print(f"Created {filename} ({size}x{size})")
        
    # Create icons directory if it doesn't exist
    icons_dir = 'd:/PROJECTS/NLP/shoppers-verdict/browser-extension/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate all required icon sizes
    create_icon(16, f'{icons_dir}/icon16.png')
    create_icon(48, f'{icons_dir}/icon48.png')  
    create_icon(128, f'{icons_dir}/icon128.png')
    
    print("✅ All extension icons created successfully!")
    print("📁 Icons saved in:", icons_dir)
    
except ImportError:
    print("❌ PIL (Pillow) not installed. Installing...")
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✅ Pillow installed successfully!")
        print("🔄 Please run this script again to generate icons.")
    except Exception as e:
        print(f"❌ Failed to install Pillow: {e}")
        print("📌 Manual installation: pip install Pillow")
        
except Exception as e:
    print(f"❌ Error creating icons: {e}")
    
    # Fallback: Create simple colored squares as placeholders
    print("🔄 Creating simple placeholder icons...")
    
    try:
        from PIL import Image
        
        def create_simple_icon(size, filename, color):
            img = Image.new('RGBA', (size, size), color)
            img.save(filename, 'PNG')
            
        icons_dir = 'd:/PROJECTS/NLP/shoppers-verdict/browser-extension/icons'
        os.makedirs(icons_dir, exist_ok=True)
        
        # Create simple colored squares
        blue_color = (102, 126, 234, 255)  # #667eea
        
        create_simple_icon(16, f'{icons_dir}/icon16.png', blue_color)
        create_simple_icon(48, f'{icons_dir}/icon48.png', blue_color)
        create_simple_icon(128, f'{icons_dir}/icon128.png', blue_color)
        
        print("✅ Simple placeholder icons created!")
        
    except Exception as fallback_error:
        print(f"❌ Fallback failed: {fallback_error}")
        print("📌 You'll need to manually create PNG icon files:")
        print("   - icon16.png (16x16 pixels)")
        print("   - icon48.png (48x48 pixels)")  
        print("   - icon128.png (128x128 pixels)")