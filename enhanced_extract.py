#!/usr/bin/env python3
"""
Enhanced OCR Extraction Script dengan multiple preprocessing strategies
Solusi untuk meningkatkan akurasi ekstraksi teks dari gambar
"""

import os
import json
import cv2
import pandas as pd
import sys
import base64
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import time
from typing import Dict, List, Tuple, Optional
import logging

# Import enhanced OCR
from enhanced_ocr import EnhancedOCR, enhanced_ocr_extract, analyze_image_quality

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRConfig:
    """Configuration class untuk OCR settings"""
    
    def __init__(self):
        # Basic settings
        self.languages = "eng+ind"
        self.confidence_threshold = 0.6
        
        # Preprocessing settings
        self.enable_preprocessing = True
        self.auto_preprocessing = True
        self.preprocess_strategies = [
            'original', 'grayscale', 'threshold', 'adaptive', 
            'denoise', 'contrast', 'sharpen', 'morphology', 'combined'
        ]
        
        # Quality settings
        self.min_image_size = (50, 20)  # Minimum width, height
        self.max_image_size = (2000, 2000)  # Maximum width, height
        self.target_dpi = 300  # Target DPI for resizing
        
        # Output settings
        self.save_detailed_results = True
        self.save_debug_images = False
        self.output_format = "csv"  # csv, json, excel
        
    def to_dict(self):
        """Convert config to dictionary"""
        return {
            'languages': self.languages,
            'confidence_threshold': self.confidence_threshold,
            'enable_preprocessing': self.enable_preprocessing,
            'auto_preprocessing': self.auto_preprocessing,
            'preprocess_strategies': self.preprocess_strategies,
            'min_image_size': self.min_image_size,
            'max_image_size': self.max_image_size,
            'target_dpi': self.target_dpi,
            'save_detailed_results': self.save_detailed_results,
            'save_debug_images': self.save_debug_images,
            'output_format': self.output_format
        }

def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 string ke OpenCV image"""
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise

def validate_image(image: np.ndarray, config: OCRConfig) -> Tuple[bool, str]:
    """Validate image quality dan size"""
    if image is None:
        return False, "Image is None"
    
    if image.size == 0:
        return False, "Image is empty"
    
    height, width = image.shape[:2]
    min_w, min_h = config.min_image_size
    max_w, max_h = config.max_image_size
    
    if width < min_w or height < min_h:
        return False, f"Image too small: {width}x{height}, minimum {min_w}x{min_h}"
    
    if width > max_w or height > max_h:
        return False, f"Image too large: {width}x{height}, maximum {max_w}x{max_h}"
    
    return True, "Valid"

def preprocess_image(image: np.ndarray, config: OCRConfig) -> np.ndarray:
    """Preprocess image berdasarkan konfigurasi"""
    if not config.enable_preprocessing:
        return image
    
    # Auto preprocessing based on image analysis
    if config.auto_preprocessing:
        from enhanced_ocr import EnhancedOCR
        ocr = EnhancedOCR()
        analysis = ocr.analyze_image_quality(image)
        quality_score = analysis.get('quality_score', 0.0)
        
        logger.info(f"Image quality analysis: {quality_score:.3f}")
        
        if quality_score > 0.7:
            return image  # Good quality, no preprocessing needed
        elif quality_score > 0.4:
            return ocr._enhance_contrast_strategy(image)
        else:
            return ocr._combined_strategy(image)
    
    return image

def run_enhanced_ocr_preview(input_data: Dict) -> Dict[str, Dict]:
    """Enhanced OCR preview untuk single image dengan detailed results"""
    logger.info("=== ENHANCED OCR PREVIEW START ===")
    
    image_b64 = input_data.get("image")
    fields = input_data.get("fields", [])
    
    if not image_b64:
        raise ValueError("No image data provided")
    
    # Decode gambar dari base64
    image = decode_base64_image(image_b64)
    
    # Validate image
    config = OCRConfig()
    is_valid, message = validate_image(image, config)
    if not is_valid:
        raise ValueError(f"Image validation failed: {message}")
    
    results = {}
    ocr = EnhancedOCR(languages=config.languages, confidence_threshold=config.confidence_threshold)
    
    for field in fields:
        try:
            x, y, w, h = field["x"], field["y"], field["w"], field["h"]
            
            # Validate field coordinates
            if x < 0 or y < 0 or w <= 0 or h <= 0:
                raise ValueError(f"Invalid field coordinates: x={x}, y={y}, w={w}, h={h}")
            
            # Check bounds
            image_height, image_width = image.shape[:2]
            if x + w > image_width or y + h > image_height:
                raise ValueError(f"Field out of bounds: field {x+w}x{y+h} exceeds image {image_width}x{image_height}")
            
            # Crop area
            crop = image[y:y + h, x:x + w]
            
            # Preprocess if enabled
            if config.enable_preprocessing:
                crop = preprocess_image(crop, config)
            
            # Run enhanced OCR
            start_time = time.time()
            ocr_result = ocr.extract_text(crop, debug=False)
            processing_time = time.time() - start_time
            
            # Store detailed results
            results[field["name"]] = {
                'text': ocr_result['text'],
                'confidence': ocr_result['confidence'],
                'strategy_used': ocr_result['strategy_used'],
                'processing_time': processing_time,
                'coordinates': {'x': x, 'y': y, 'w': w, 'h': h},
                'success': len(ocr_result['text'].strip()) > 0 and ocr_result['confidence'] >= config.confidence_threshold
            }
            
            logger.info(f"Field {field['name']}: '{ocr_result['text']}' (confidence: {ocr_result['confidence']:.3f})")
            
        except Exception as e:
            logger.error(f"Error processing field {field.get('name', '?')}: {e}")
            results[field["name"]] = {
                'text': '',
                'confidence': 0.0,
                'strategy_used': 'error',
                'processing_time': 0.0,
                'coordinates': {'x': field.get('x', 0), 'y': field.get('y', 0), 
                              'w': field.get('w', 0), 'h': field.get('h', 0)},
                'error': str(e),
                'success': False
            }
    
    return results

def run_enhanced_ocr_batch(template_path: str, image_folder: str, output_dir: str = "/data", config: Optional[OCRConfig] = None) -> str:
    """Enhanced OCR batch processing dengan detailed logging"""
    print("=== ENHANCED OCR BATCH START ===")
    logger.info(f"Template path: {template_path}")
    logger.info(f"Image folder: {image_folder}")
    logger.info(f"Output dir: {output_dir}")
    
    if config is None:
        config = OCRConfig()
    
    # Validate paths
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template tidak ditemukan: {template_path}")
    
    if not os.path.isdir(image_folder):
        raise NotADirectoryError(f"Folder gambar tidak ditemukan: {image_folder}")
    
    # Load template
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)
    
    if "fields" not in template:
        raise KeyError("Template JSON tidak memiliki key 'fields'")
    
    fields = template["fields"]
    
    # Initialize OCR
    ocr = EnhancedOCR(languages=config.languages, confidence_threshold=config.confidence_threshold)
    
    # Process images
    images = [f for f in os.listdir(image_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    logger.info(f"Found {len(images)} image files")
    
    if not images:
        raise ValueError("No valid image files found in the specified folder")
    
    rows = []
    detailed_results = []
    total_start_time = time.time()
    
    for filename in images:
        try:
            img_path = os.path.join(image_folder, filename)
            logger.info(f"Processing: {filename}")
            
            # Load image
            image = cv2.imread(img_path)
            if image is None:
                logger.warning(f"Could not load image: {filename}")
                continue
            
            # Validate image
            is_valid, message = validate_image(image, config)
            if not is_valid:
                logger.warning(f"Invalid image {filename}: {message}")
                continue
            
            # Prepare data for this image
            data = {"filename": filename}
            image_results = {"filename": filename, "fields": {}}
            
            # Process each field
            for field in fields:
                try:
                    x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                    
                    # Validate field coordinates
                    if x < 0 or y < 0 or w <= 0 or h <= 0:
                        raise ValueError(f"Invalid field coordinates")
                    
                    # Crop area
                    crop = image[y:y + h, x:x + w]
                    
                    # Preprocess if enabled
                    if config.enable_preprocessing:
                        crop = preprocess_image(crop, config)
                    
                    # Run enhanced OCR
                    start_time = time.time()
                    ocr_result = ocr.extract_text(crop, debug=False)
                    processing_time = time.time() - start_time
                    
                    # Store extracted text
                    data[field["name"]] = ocr_result['text']
                    
                    # Store detailed results
                    field_result = {
                        'field_name': field["name"],
                        'text': ocr_result['text'],
                        'confidence': ocr_result['confidence'],
                        'strategy_used': ocr_result['strategy_used'],
                        'processing_time': processing_time,
                        'coordinates': {'x': x, 'y': y, 'w': w, 'h': h}
                    }
                    image_results["fields"][field["name"]] = field_result
                    
                    logger.info(f"  {field['name']}: '{ocr_result['text']}' (confidence: {ocr_result['confidence']:.3f})")
                    
                except Exception as e:
                    logger.error(f"  Error processing field {field.get('name', '?')} in {filename}: {e}")
                    data[field["name"]] = ""
                    image_results["fields"][field["name"]] = {
                        'field_name': field["name"],
                        'text': '',
                        'confidence': 0.0,
                        'strategy_used': 'error',
                        'error': str(e)
                    }
            
            rows.append(data)
            detailed_results.append(image_results)
            logger.info(f"Completed: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")
            continue
    
    total_processing_time = time.time() - total_start_time
    
    if not rows:
        raise ValueError("No data was extracted from any images")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main results
    output_path = os.path.join(output_dir, "hasil_ocr.csv")
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")
    
    # Save detailed results if enabled
    if config.save_detailed_results:
        detailed_path = os.path.join(output_dir, "hasil_ocr_detailed.json")
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    # Save processing report
    report = {
        'summary': {
            'total_images': len(images),
            'processed_images': len(rows),
            'total_fields': len(fields),
            'total_processing_time': total_processing_time,
            'average_time_per_image': total_processing_time / len(rows) if rows else 0
        },
        'config': config.to_dict(),
        'success_rate': len(rows) / len(images) if images else 0
    }
    
    report_path = os.path.join(output_dir, "ocr_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("=== ENHANCED OCR SELESAI ===")
    print(f"Output file: {output_path}")
    print(f"Detailed results: {detailed_path}")
    print(f"Report: {report_path}")
    print(f"Processing time: {total_processing_time:.2f}s")
    print(f"Success rate: {report['success_rate']:.1%}")
    
    return output_path

def analyze_image_quality_cli(image_path: str) -> Dict:
    """Command line tool untuk analyze image quality"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    from enhanced_ocr import EnhancedOCR
    ocr = EnhancedOCR()
    analysis = ocr.analyze_image_quality(image)
    
    print(f"Image Quality Analysis: {image_path}")
    print("=" * 50)
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    return analysis

if __name__ == "__main__":
    # Add missing import
    import io
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Enhanced OCR Preview: python enhanced_extract.py preview <input.json")
        print("  Enhanced OCR Batch: python enhanced_extract.py batch <template.json> <image_folder> [output_dir]")
        print("  Image Quality Analysis: python enhanced_extract.py analyze <image_path>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "preview":
        if len(sys.argv) < 3:
            print("Usage: python enhanced_extract.py preview <input.json")
            sys.exit(1)
        
        with open(sys.argv[2], 'r') as f:
            input_data = json.load(f)
        
        results = run_enhanced_ocr_preview(input_data)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    elif command == "batch":
        if len(sys.argv) < 4:
            print("Usage: python enhanced_extract.py batch <template.json> <image_folder> [output_dir]")
            sys.exit(1)
        
        template_path = sys.argv[2]
        image_folder = sys.argv[3]
        output_dir = sys.argv[4] if len(sys.argv) > 4 else "/data"
        
        try:
            output_path = run_enhanced_ocr_batch(template_path, image_folder, output_dir)
            print(f"✅ Enhanced OCR completed successfully!")
            print(f"📁 Results saved to: {output_path}")
        except Exception as e:
            print(f"❌ Enhanced OCR failed: {e}")
            sys.exit(1)
            
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python enhanced_extract.py analyze <image_path>")
            sys.exit(1)
        
        try:
            analyze_image_quality_cli(sys.argv[2])
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)
            
    else:
        print(f"Unknown command: {command}")
        print("Available commands: preview, batch, analyze")
        sys.exit(1)
