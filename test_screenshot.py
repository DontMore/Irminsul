#!/usr/bin/env python3
"""
Test script for the enhanced screenshot functionality
This script tests the different screenshot methods without running the full GUI
"""

import sys
import os
import time
from PIL import Image

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screenshot import ScreenshotMiniGUI

def test_screenshot_methods():
    """Test different screenshot methods to see which ones work"""
    
    print("🧪 Testing Screenshot Methods")
    print("=" * 40)
    
    # Test Method 1: PyAutoGUI
    print("\n📷 Method 1: Testing PyAutoGUI...")
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        print("✅ PyAutoGUI: SUCCESS")
        print(f"   Screenshot size: {screenshot.size}")
    except Exception as e:
        print(f"❌ PyAutoGUI: FAILED - {e}")
    
    # Test Method 2: PIL ImageGrab
    print("\n📷 Method 2: Testing PIL ImageGrab...")
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        print("✅ ImageGrab: SUCCESS")
        print(f"   Screenshot size: {screenshot.size}")
    except Exception as e:
        print(f"❌ ImageGrab: FAILED - {e}")
    
    # Test Method 3: Subprocess methods
    print("\n📷 Method 3: Testing Subprocess methods...")
    import subprocess
    
    methods = [
        ("scrot", ["scrot", "--version"]),
        ("gnome-screenshot", ["gnome-screenshot", "--version"]),
        ("flameshot", ["flameshot", "--version"]),
        ("spectacle", ["spectacle", "--version"])
    ]
    
    for name, cmd in methods:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {name}: AVAILABLE")
            else:
                print(f"❌ {name}: NOT AVAILABLE")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {name}: NOT AVAILABLE")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
    
    print("\n" + "=" * 40)
    print("🏁 Screenshot method testing completed!")

def test_screenshot_class():
    """Test the ScreenshotMiniGUI class methods"""
    
    print("\n🧪 Testing ScreenshotMiniGUI Class")
    print("=" * 40)
    
    # Create a dummy root window
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create ScreenshotMiniGUI instance
    screenshot_gui = ScreenshotMiniGUI(root, save_dir="test_screenshots")
    
    # Test individual methods
    print("\n📷 Testing individual screenshot methods:")
    
    # Test pyautogui method
    result = screenshot_gui._take_screenshot_pyautogui()
    if result:
        print("✅ PyAutoGUI method: SUCCESS")
    else:
        print("❌ PyAutoGUI method: FAILED")
    
    # Test ImageGrab method
    result = screenshot_gui._take_screenshot_imagegrab()
    if result:
        print("✅ ImageGrab method: SUCCESS")
    else:
        print("❌ ImageGrab method: FAILED")
    
    # Test subprocess method
    result = screenshot_gui._take_screenshot_subprocess()
    if result:
        print("✅ Subprocess method: SUCCESS")
    else:
        print("❌ Subprocess method: FAILED")
    
    root.destroy()
    print("\n" + "=" * 40)
    print("🏁 ScreenshotMiniGUI testing completed!")

if __name__ == "__main__":
    print("🚀 Starting Screenshot Functionality Tests")
    print(f"Python version: {sys.version}")
    
    # Check Pillow version
    try:
        from PIL import Image
        print(f"Pillow version: {Image.__version__}")
    except ImportError:
        print("❌ Pillow not found!")
        sys.exit(1)
    
    # Run tests
    test_screenshot_methods()
    test_screenshot_class()
    
    print("\n🎉 All tests completed!")
