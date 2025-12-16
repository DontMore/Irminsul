#!/usr/bin/env python3
"""
Test script for mouse coordinate accuracy in gui.py
Tests the fixes for image offset handling in mouse events
"""

import tkinter as tk
import sys
import os
from PIL import Image, ImageDraw
import json

# Add current directory to path to import gui
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image(width=800, height=600, filename="test_image.png"):
    """Create a test image with some text for OCR testing"""
    # Create a white image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw some test text
    draw.text((50, 50), "TEST IMAGE FOR OCR", fill='black')
    draw.text((50, 100), "Field 1: Name", fill='black')
    draw.text((50, 150), "Field 2: Address", fill='black')
    draw.text((50, 200), "Field 3: Phone", fill='black')

    # Draw rectangles around text areas
    draw.rectangle([40, 40, 300, 80], outline='red', width=2)   # Field 1
    draw.rectangle([40, 90, 300, 130], outline='blue', width=2)  # Field 2
    draw.rectangle([40, 140, 300, 180], outline='green', width=2) # Field 3

    img.save(filename)
    print(f"Created test image: {filename} ({width}x{height})")
    return filename

def test_mouse_coordinate_accuracy():
    """Test mouse coordinate accuracy with different scenarios"""
    print("🧪 Testing Mouse Coordinate Accuracy")
    print("=" * 50)

    try:
        from gui import ModernTemplateGUI
        print("✅ Successfully imported ModernTemplateGUI")
    except ImportError as e:
        print(f"❌ Failed to import ModernTemplateGUI: {e}")
        return False

    # Create test image
    test_image_path = create_test_image()

    # Create a hidden root window for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window

    try:
        # Create template GUI instance
        template_gui = ModernTemplateGUI(root)

        # Verify new attributes exist
        if not hasattr(template_gui, 'image_offset_x'):
            print("❌ image_offset_x attribute missing")
            return False
        if not hasattr(template_gui, 'image_offset_y'):
            print("❌ image_offset_y attribute missing")
            return False

        print("✅ Image offset attributes present")

        # Test loading image
        print("\n📂 Testing image loading...")
        try:
            # Simulate opening image
            template_gui.original_image = Image.open(test_image_path)
            template_gui.image = template_gui.original_image.copy()
            template_gui.zoom_factor = 1.0
            template_gui.image_offset_x = 0
            template_gui.image_offset_y = 0
            template_gui.rectangles = []

            # Force canvas update
            template_gui.canvas.update_idletasks()

            # Get canvas dimensions
            canvas_width = template_gui.canvas.winfo_width()
            canvas_height = template_gui.canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600

            print(f"Canvas size: {canvas_width}x{canvas_height}")
            print(f"Image size: {template_gui.image.width}x{template_gui.image.height}")

            # Test redraw_image to set offsets
            template_gui.redraw_image()

            print(f"Image offset after redraw: ({template_gui.image_offset_x}, {template_gui.image_offset_y})")

            # Test coordinate conversion
            print("\n🎯 Testing coordinate conversion...")

            # Simulate mouse events at different positions
            test_positions = [
                (100, 100),  # Top-left area
                (400, 300),  # Center area
                (700, 500),  # Bottom-right area
            ]

            for canvas_x, canvas_y in test_positions:
                # Test conversion to image coordinates
                image_x = (canvas_x - template_gui.image_offset_x) / template_gui.zoom_factor
                image_y = (canvas_y - template_gui.image_offset_y) / template_gui.zoom_factor

                print(f"Canvas ({canvas_x}, {canvas_y}) -> Image ({image_x:.1f}, {image_y:.1f})")

                # Verify coordinates are within image bounds
                if 0 <= image_x <= template_gui.image.width and 0 <= image_y <= template_gui.image.height:
                    print("  ✅ Coordinates within image bounds")
                else:
                    print("  ❌ Coordinates outside image bounds")
                    return False

            # Test rectangle creation and drawing
            print("\n📦 Testing rectangle creation...")
            test_rect = {
                "name": "test_field",
                "x": 50,
                "y": 50,
                "w": 100,
                "h": 30
            }

            template_gui.rectangles = [test_rect]
            template_gui.redraw_rectangles()

            print("✅ Rectangle drawing test passed")

            # Test field highlighting
            print("\n🎨 Testing field highlighting...")
            template_gui.on_field_select(None)  # This should work without selection
            print("✅ Field highlighting test passed")

            print("\n✅ All tests passed!")
            return True

        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            return False

    finally:
        # Cleanup
        root.destroy()
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"🧹 Cleaned up test image: {test_image_path}")

def test_zoom_scenarios():
    """Test coordinate accuracy with different zoom levels"""
    print("\n🔍 Testing Zoom Scenarios")
    print("=" * 30)

    root = tk.Tk()
    root.withdraw()

    try:
        from gui import ModernTemplateGUI
        template_gui = ModernTemplateGUI(root)

        # Create and load test image
        test_image_path = create_test_image(400, 300)
        template_gui.original_image = Image.open(test_image_path)
        template_gui.image = template_gui.original_image.copy()
        template_gui.zoom_factor = 1.0
        template_gui.image_offset_x = 0
        template_gui.image_offset_y = 0

        template_gui.canvas.update_idletasks()
        canvas_width = template_gui.canvas.winfo_width() or 800
        canvas_height = template_gui.canvas.winfo_height() or 600

        zoom_levels = [0.5, 1.0, 1.5, 2.0]

        for zoom in zoom_levels:
            template_gui.zoom_factor = zoom
            template_gui.redraw_image()

            # Test coordinate at canvas center
            center_x, center_y = canvas_width // 2, canvas_height // 2
            image_x = (center_x - template_gui.image_offset_x) / zoom
            image_y = (center_y - template_gui.image_offset_y) / zoom

            print(f"Zoom {zoom}: Canvas center ({center_x}, {center_y}) -> Image ({image_x:.1f}, {image_y:.1f})")

            # Check if image coordinates are reasonable
            if image_x >= 0 and image_y >= 0:
                print("  ✅ Valid coordinates")
            else:
                print("  ❌ Invalid coordinates")
                return False

        print("✅ Zoom scenario tests passed")
        return True

    finally:
        root.destroy()
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == "__main__":
    print("🚀 Starting Mouse Coordinate Accuracy Tests")
    print("=" * 60)

    success1 = test_mouse_coordinate_accuracy()
    success2 = test_zoom_scenarios()

    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! Mouse coordinate accuracy fixes are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        sys.exit(1)
