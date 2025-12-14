#!/usr/bin/env python3
"""
Test script untuk memverifikasi OCR functionality
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

def create_test_image():
    """Buat gambar test sederhana dengan teks"""
    # Buat gambar putih
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Tambah teks menggunakan font default
    try:
        # Coba gunakan font yang lebih baik jika tersedia
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Tambah teks dalam bahasa Indonesia dan Inggris
    draw.text((20, 50), "Test OCR", fill='black', font=font)
    draw.text((20, 90), "Halo dunia!", fill='black', font=font)
    draw.text((20, 130), "This is a test", fill='black', font=font)
    
    # Simpan ke file temporary
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    return temp_file.name

def test_tesseract():
    """Test basic tesseract functionality"""
    print("🧪 Testing Tesseract OCR...")
    
    # Test 1: Check tesseract version and languages
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        languages = pytesseract.get_languages()
        print(f"✅ Available languages: {languages}")
        
        # Check if required languages are available
        if 'eng' in languages and 'ind' in languages:
            print("✅ English and Indonesian language packs are available")
        else:
            print("⚠️  Missing language packs")
            
    except Exception as e:
        print(f"❌ Error checking tesseract: {e}")
        return False
    
    # Test 2: Test OCR on generated image
    try:
        print("\n🖼️  Testing OCR on generated image...")
        image_path = create_test_image()
        
        # Load and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            print("❌ Could not load test image")
            return False
        
        # Test OCR with English
        text_en = pytesseract.image_to_string(img, lang='eng')
        print(f"✅ English OCR result: '{text_en.strip()}'")
        
        # Test OCR with Indonesian  
        text_id = pytesseract.image_to_string(img, lang='ind')
        print(f"✅ Indonesian OCR result: '{text_id.strip()}'")
        
        # Test OCR with both languages
        text_both = pytesseract.image_to_string(img, lang='eng+ind')
        print(f"✅ Combined OCR result: '{text_both.strip()}'")
        
        # Cleanup
        os.unlink(image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during OCR test: {e}")
        return False

def test_gui_dependencies():
    """Test dependencies needed for GUI"""
    print("\n🖥️  Testing GUI dependencies...")
    
    dependencies = [
        ('tkinter', 'GUI framework'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow (PIL)'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas')
    ]
    
    all_ok = True
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError as e:
            print(f"❌ {module}: {description} - {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("🚀 OCR Setup Test")
    print("=" * 50)
    
    # Test 1: GUI dependencies
    gui_ok = test_gui_dependencies()
    
    # Test 2: Tesseract functionality
    ocr_ok = test_tesseract()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"GUI Dependencies: {'✅ OK' if gui_ok else '❌ FAIL'}")
    print(f"OCR Functionality: {'✅ OK' if ocr_ok else '❌ FAIL'}")
    
    if gui_ok and ocr_ok:
        print("\n🎉 All tests passed! OCR preview should work in the GUI.")
        print("\nNext steps:")
        print("1. Run: python gui.py")
        print("2. Go to 'Template Creator' tab")
        print("3. Open an image")
        print("4. Select areas with mouse drag")
        print("5. Click 'Preview Extractions'")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return gui_ok and ocr_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
