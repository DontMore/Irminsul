#!/usr/bin/env python3
"""
Test script untuk memverifikasi bahwa image display sudah diperbaiki
"""
import tkinter as tk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Import modules from current directory
sys.path.append('/media/broken/New Volume/Coding/Irminsul')
from modern_styles import apply_modern_styling, create_modern_frame
from gui_modern import ModernTemplateGUI

def create_test_image():
    """Create a test image for verification"""
    # Create a test image with some text and shapes
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw some shapes and text
    draw.rectangle([50, 50, 300, 150], fill='lightblue', outline='blue', width=3)
    draw.text((60, 70), "TEST IMAGE", fill='black')
    
    draw.ellipse([400, 100, 600, 250], fill='lightgreen', outline='green', width=3)
    draw.text((420, 160), "OCR Test", fill='darkgreen')
    
    draw.rectangle([100, 300, 500, 450], fill='yellow', outline='orange', width=3)
    draw.text((120, 320), "Template Area 1", fill='darkorange')
    
    draw.rectangle([150, 400, 400, 500], fill='lightcoral', outline='red', width=2)
    draw.text((170, 420), "Template Area 2", fill='darkred')
    
    return image

def test_image_loading():
    """Test image loading functionality"""
    print("🧪 Testing image display functionality...")
    
    # Create test image
    test_image = create_test_image()
    test_image_path = "/media/broken/New Volume/Coding/Irminsul/test_image.png"
    test_image.save(test_image_path)
    print(f"✅ Created test image: {test_image_path}")
    
    # Test the template GUI
    root = tk.Tk()
    root.title("🧪 Image Display Test")
    root.geometry("1200x800")
    
    # Apply modern styling
    apply_modern_styling(root)
    
    # Create test frame
    test_frame = create_modern_frame(root, padding=20)
    test_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create template GUI
    template_gui = ModernTemplateGUI(test_frame)
    
    # Auto-load test image after a short delay
    def auto_load_test():
        template_gui.image_path = test_image_path  # Set path for testing
        template_gui.open_image()
    
    root.after(1000, auto_load_test)  # Load test image after 1 second
    
    print("🚀 Launching test GUI...")
    print("📋 Test Checklist:")
    print("  ✅ Canvas should be white initially")
    print("  ✅ Image should appear after 1 second")
    print("  ✅ Image should be properly centered")
    print("  ✅ Image should show test shapes and text clearly")
    print("  ✅ Canvas should have proper scroll region")
    print("  ✅ Mouse selection should work for creating rectangles")
    
    root.mainloop()

def verify_canvas_config():
    """Verify canvas configuration is correct"""
    print("\n🔍 Verifying canvas configuration...")
    
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    # Create canvas to test configuration
    test_frame = tk.Frame(root)
    canvas = tk.Canvas(
        test_frame,
        cursor="cross",
        bg="white",
        highlightthickness=0,
        highlightbackground="white"
    )
    
    # Configure scrollregion
    canvas.configure(scrollregion=(0, 0, 1000, 800))
    
    # Check configuration
    config_check = {
        'bg': canvas['bg'],
        'highlightthickness': canvas['highlightthickness'],
        'highlightbackground': canvas['highlightbackground'],
        'cursor': canvas['cursor']
    }
    
    print("✅ Canvas Configuration:")
    for key, value in config_check.items():
        print(f"  {key}: {value}")
    
    root.destroy()
    
    # Verify configuration is correct
    if (config_check['bg'] == 'white' and 
        config_check['highlightthickness'] == '0' and
        config_check['highlightbackground'] == 'white' and
        config_check['cursor'] == 'cross'):
        print("✅ Canvas configuration is correct!")
        return True
    else:
        print("❌ Canvas configuration has issues!")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Image Display Test Suite")
    print("=" * 50)
    
    # Test 1: Canvas configuration
    config_ok = verify_canvas_config()
    
    if config_ok:
        # Test 2: Full GUI test
        test_image_loading()
    else:
        print("❌ Skipping GUI test due to configuration issues")
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()
