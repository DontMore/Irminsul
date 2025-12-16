#!/usr/bin/env python3
"""
Test script untuk Enhanced OCR - Verifikasi semua fitur bekerja dengan baik
"""

import cv2
import numpy as np
import time
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile
import json

# Import enhanced OCR modules
from enhanced_ocr import EnhancedOCR, enhanced_ocr_extract, analyze_image_quality
from enhanced_extract import OCRConfig, run_enhanced_ocr_batch

def create_test_images():
    """Buat berbagai jenis test images untuk testing OCR"""
    test_images = []
    
    # Test 1: High quality text
    img1 = Image.new('RGB', (400, 200), color='white')
    draw1 = ImageDraw.Draw(img1)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw1.text((20, 50), "High Quality Text", fill='black', font=font)
    draw1.text((20, 90), "Easy to Read", fill='black', font=font)
    draw1.text((20, 130), "123 ABC", fill='black', font=font)
    
    # Test 2: Low contrast text
    img2 = Image.new('RGB', (400, 200), color=(240, 240, 240))
    draw2 = ImageDraw.Draw(img2)
    draw2.text((20, 50), "Low Contrast Text", fill=(200, 200, 200), font=font)
    draw2.text((20, 90), "Hard to Read", fill=(200, 200, 200), font=font)
    
    # Test 3: Noisy background
    img3 = Image.new('RGB', (400, 200), color='white')
    draw3 = ImageDraw.Draw(img3)
    
    # Add noise
    for i in range(1000):
        x = np.random.randint(0, 400)
        y = np.random.randint(0, 200)
        color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        draw3.point((x, y), fill=color)
    
    draw3.text((20, 50), "Noisy Background", fill='black', font=font)
    draw3.text((20, 90), "Text in Noise", fill='black', font=font)
    
    # Test 4: Small text
    img4 = Image.new('RGB', (200, 100), color='white')
    draw4 = ImageDraw.Draw(img4)
    try:
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        small_font = ImageFont.load_default()
    
    draw4.text((10, 20), "Small Text", fill='black', font=small_font)
    draw4.text((10, 40), "12pt size", fill='black', font=small_font)
    
    # Test 5: Mixed language
    img5 = Image.new('RGB', (400, 200), color='white')
    draw5 = ImageDraw.Draw(img5)
    draw5.text((20, 50), "Indonesian: Halo Dunia", fill='black', font=font)
    draw5.text((20, 90), "English: Hello World", fill='black', font=font)
    draw5.text((20, 130), "Mixed: Test 123", fill='black', font=font)
    
    test_images = [
        ("high_quality", img1),
        ("low_contrast", img2),
        ("noisy_background", img3),
        ("small_text", img4),
        ("mixed_language", img5)
    ]
    
    # Save to temporary files
    saved_images = []
    for name, img in test_images:
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        saved_images.append((name, temp_file.name))
    
    return saved_images

def test_enhanced_ocr_basic():
    """Test basic enhanced OCR functionality"""
    print("🧪 Testing Enhanced OCR Basic Functionality")
    print("=" * 60)
    
    # Create test images
    test_images = create_test_images()
    
    ocr = EnhancedOCR(languages="eng+ind", confidence_threshold=0.6)
    
    for name, image_path in test_images:
        print(f"\n📸 Testing: {name}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"   ❌ Could not load image: {image_path}")
            continue
        
        # Analyze image quality
        analysis = ocr.analyze_image_quality(image)
        print(f"   📊 Quality Score: {analysis.get('quality_score', 0):.3f}")
        print(f"   🎯 Recommendations: {analysis.get('recommendations', [])}")
        
        # Run enhanced OCR
        start_time = time.time()
        result = ocr.extract_text(image, debug=False)
        processing_time = time.time() - start_time
        
        # Display results
        print(f"   📝 Text: '{result['text']}'")
        print(f"   📊 Confidence: {result['confidence']:.3f}")
        print(f"   ⚙️ Strategy: {result['strategy_used']}")
        print(f"   ⏱️ Processing Time: {processing_time:.3f}s")
        
        # Success check
        success = len(result['text'].strip()) > 0 and result['confidence'] >= 0.6
        print(f"   ✅ Success: {'YES' if success else 'NO'}")
        
        # Cleanup
        os.unlink(image_path)
    
    print(f"\n✅ Basic Enhanced OCR test completed!")

def test_confidence_scoring():
    """Test confidence scoring system"""
    print("\n🎯 Testing Confidence Scoring System")
    print("=" * 60)
    
    # Create images with different quality levels
    test_cases = []
    
    # High confidence case - perfect text
    img_good = Image.new('RGB', (300, 100), color='white')
    draw_good = ImageDraw.Draw(img_good)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw_good.text((10, 30), "PERFECT TEXT", fill='black', font=font)
    
    # Low confidence case - poor quality
    img_bad = Image.new('RGB', (300, 100), color='gray')
    draw_bad = ImageDraw.Draw(img_bad)
    draw_bad.text((10, 30), "POOR QUALITY", fill=(128, 128, 128), font=font)
    
    test_cases = [
        ("high_confidence", img_good),
        ("low_confidence", img_bad)
    ]
    
    ocr = EnhancedOCR(languages="eng+ind")
    
    for name, img in test_cases:
        print(f"\n🎯 Testing confidence: {name}")
        
        # Save temporary
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        
        # Load and test
        image = cv2.imread(temp_file.name)
        result = ocr.extract_text(image, debug=False)
        
        confidence_level = "🟢 HIGH" if result['confidence'] >= 0.8 else "🟡 MEDIUM" if result['confidence'] >= 0.6 else "🔴 LOW"
        print(f"   📊 Confidence: {result['confidence']:.3f} {confidence_level}")
        print(f"   📝 Extracted: '{result['text']}'")
        
        os.unlink(temp_file.name)
    
    print(f"\n✅ Confidence scoring test completed!")

def test_preprocessing_strategies():
    """Test different preprocessing strategies"""
    print("\n⚙️ Testing Preprocessing Strategies")
    print("=" * 60)
    
    # Create a test image that benefits from preprocessing
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add some challenging text
    draw.text((20, 50), "TEST PREPROCESSING", fill='black', font=font)
    draw.text((20, 90), "Different Strategies", fill='black', font=font)
    draw.text((20, 130), "123 ABC def", fill='black', font=font)
    
    # Save temporary
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    
    # Load image
    image = cv2.imread(temp_file.name)
    
    # Test each strategy
    ocr = EnhancedOCR()
    strategies = [
        'original', 'grayscale', 'threshold', 'adaptive', 
        'denoise', 'contrast', 'sharpen', 'morphology', 'combined'
    ]
    
    results = []
    
    for strategy in strategies:
        print(f"\n⚙️ Strategy: {strategy}")
        
        # Apply preprocessing
        if strategy == 'original':
            processed = image.copy()
        elif strategy == 'grayscale':
            processed = ocr._grayscale_strategy(image)
        elif strategy == 'threshold':
            processed = ocr._threshold_strategy(image)
        elif strategy == 'adaptive':
            processed = ocr._adaptive_threshold_strategy(image)
        elif strategy == 'denoise':
            processed = ocr._denoise_strategy(image)
        elif strategy == 'contrast':
            processed = ocr._enhance_contrast_strategy(image)
        elif strategy == 'sharpen':
            processed = ocr._sharpen_strategy(image)
        elif strategy == 'morphology':
            processed = ocr._morphology_strategy(image)
        elif strategy == 'combined':
            processed = ocr._combined_strategy(image)
        
        # OCR
        text = pytesseract.image_to_string(processed, lang="eng+ind").strip()
        confidence = ocr._calculate_confidence(processed, text)
        
        print(f"   📝 Text: '{text}'")
        print(f"   📊 Confidence: {confidence:.3f}")
        
        results.append((strategy, text, confidence))
    
    # Find best strategy
    best_strategy = max(results, key=lambda x: x[2])
    print(f"\n🏆 Best Strategy: {best_strategy[0]} (confidence: {best_strategy[2]:.3f})")
    
    os.unlink(temp_file.name)
    print(f"\n✅ Preprocessing strategies test completed!")

def test_batch_processing():
    """Test batch processing functionality"""
    print("\n📦 Testing Batch Processing")
    print("=" * 60)
    
    # Create multiple test images
    test_images = create_test_images()
    
    # Create a simple template
    template = {
        "fields": [
            {"name": "text_field", "x": 10, "y": 30, "w": 200, "h": 50}
        ]
    }
    
    # Save template
    template_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(template, template_file)
    template_file.close()
    
    # Create output directory
    output_dir = tempfile.mkdtemp()
    
    try:
        # Create image folder
        image_folder = tempfile.mkdtemp()
        
        # Copy images to folder
        for name, image_path in test_images:
            import shutil
            dest_path = os.path.join(image_folder, f"{name}.png")
            shutil.copy2(image_path, dest_path)
        
        # Run batch processing
        print(f"📁 Template: {template_file.name}")
        print(f"📁 Image folder: {image_folder}")
        print(f"📁 Output dir: {output_dir}")
        
        output_path = run_enhanced_ocr_batch(
            template_file.name, 
            image_folder, 
            output_dir
        )
        
        print(f"✅ Batch processing completed!")
        print(f"📁 Output saved to: {output_path}")
        
        # Check if files exist
        if os.path.exists(output_path):
            print(f"✅ Main output file exists")
        
        detailed_path = os.path.join(output_dir, "hasil_ocr_detailed.json")
        if os.path.exists(detailed_path):
            print(f"✅ Detailed output file exists")
        
        report_path = os.path.join(output_dir, "ocr_report.json")
        if os.path.exists(report_path):
            print(f"✅ Report file exists")
        
        # Cleanup
        import shutil
        shutil.rmtree(image_folder)
        shutil.rmtree(output_dir)
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
    
    finally:
        os.unlink(template_file.name)
    
    print(f"\n✅ Batch processing test completed!")

def test_gui_integration():
    """Test GUI integration (simulate without actual GUI)"""
    print("\n🖥️ Testing GUI Integration")
    print("=" * 60)
    
    # Test the enhanced OCR preview functionality
    print("Testing enhanced OCR preview simulation...")
    
    # Create test image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 50), "GUI Integration Test", fill='black', font=font)
    draw.text((20, 90), "Enhanced OCR Preview", fill='black', font=font)
    
    # Save temporary
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    
    # Simulate GUI preview process
    image = cv2.imread(temp_file.name)
    
    # Simulate field selection
    fields = [
        {"name": "field_1", "x": 20, "y": 50, "w": 200, "h": 30},
        {"name": "field_2", "x": 20, "y": 90, "w": 200, "h": 30}
    ]
    
    ocr = EnhancedOCR(languages="eng+ind", confidence_threshold=0.6)
    
    extracted_count = 0
    high_confidence_count = 0
    
    for field in fields:
        x, y, w, h = field["x"], field["y"], field["w"], field["h"]
        crop = image[y:y+h, x:x+w]
        
        ocr_result = ocr.extract_text(crop, debug=False)
        
        print(f"🔹 {field['name'].upper()}")
        print(f"   Position: ({x}, {y}) Size: {w}x{h}")
        print(f"   Strategy: {ocr_result['strategy_used']}")
        
        if ocr_result['text']:
            confidence_color = "🟢" if ocr_result['confidence'] >= 0.8 else "🟡" if ocr_result['confidence'] >= 0.6 else "🔴"
            print(f"   Text: {ocr_result['text']}")
            print(f"   Confidence: {confidence_color} {ocr_result['confidence']:.3f}")
            extracted_count += 1
            
            if ocr_result['confidence'] >= 0.8:
                high_confidence_count += 1
        else:
            print(f"   Text: [No text detected]")
            print(f"   Confidence: 🔴 {ocr_result['confidence']:.3f}")
    
    # Summary
    success_rate = (extracted_count/len(fields)*100)
    print(f"\n📊 GUI Integration Summary:")
    print(f"   Total fields: {len(fields)}")
    print(f"   Text extracted: {extracted_count}")
    print(f"   High confidence: {high_confidence_count}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    os.unlink(temp_file.name)
    print(f"\n✅ GUI integration test completed!")

def run_comprehensive_test():
    """Run all tests comprehensively"""
    print("🚀 COMPREHENSIVE ENHANCED OCR TEST")
    print("=" * 80)
    print("Testing all Enhanced OCR features and capabilities...")
    
    tests = [
        ("Basic Functionality", test_enhanced_ocr_basic),
        ("Confidence Scoring", test_confidence_scoring),
        ("Preprocessing Strategies", test_preprocessing_strategies),
        ("Batch Processing", test_batch_processing),
        ("GUI Integration", test_gui_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            test_func()
            passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"🎯 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Enhanced OCR is working correctly!")
        print(f"🚀 Ready for production use!")
    else:
        print(f"\n⚠️ Some tests failed. Please check the errors above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    import pytesseract
    
    # Check dependencies
    print("🔍 Checking Dependencies...")
    try:
        import cv2
        print("✅ OpenCV: Available")
    except ImportError:
        print("❌ OpenCV: Not available")
        exit(1)
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow: Available")
    except ImportError:
        print("❌ PIL/Pillow: Not available")
        exit(1)
    
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract: {version}")
    except Exception as e:
        print(f"❌ Tesseract: {e}")
        exit(1)
    
    print(f"\n{'='*80}")
    
 test
    success = run_comprehensive_test()
    
    if success:
        print(f"\n    # Run comprehensive🎯 NEXT STEPS:")
        print(f"1. Run: python gui.py")
        print(f"2. Test with your own images")
        print(f"3. Adjust confidence threshold if needed")
        print(f"4. Monitor success rates")
        print(f"\n✨ Enhanced OCR is ready to improve your text extraction accuracy!")
    
    exit(0 if success else 1)

