#!/usr/bin/env python3
"""
Enhanced OCR Module untuk meningkatkan akurasi ekstraksi teks dari gambar
Solusi untuk masalah "no detect" atau teks tidak terbaca
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import warnings
import logging
from typing import Tuple, List, Dict, Optional, Union
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedOCR:
    """
    Enhanced OCR class dengan multiple preprocessing strategies
    untuk meningkatkan akurasi ekstraksi teks
    """
    
    def __init__(self, languages: str = "eng+ind", confidence_threshold: float = 0.6):
        """
        Initialize EnhancedOCR
        
        Args:
            languages: Tesseract languages to use
            confidence_threshold: Minimum confidence untuk accept hasil OCR
        """
        self.languages = languages
        self.confidence_threshold = confidence_threshold
        
        # Preprocessing configurations
        self.preprocess_strategies = [
            self._original_strategy,
            self._grayscale_strategy,
            self._threshold_strategy,
            self._adaptive_threshold_strategy,
            self._denoise_strategy,
            self._enhance_contrast_strategy,
            self._sharpen_strategy,
            self._morphology_strategy,
            self._combined_strategy
        ]
        
    def extract_text(self, image: np.ndarray, debug: bool = False) -> Dict[str, Union[str, float]]:
        """
        Extract text menggunakan multiple strategies dengan confidence scoring
        
        Args:
            image: Input image (OpenCV format)
            debug: Enable debug logging
            
        Returns:
            Dict dengan 'text', 'confidence', 'strategy_used', 'preprocessing_time'
        """
        start_time = time.time()
        
        if debug:
            logger.info("🚀 Starting Enhanced OCR extraction")
            
        # Validate input
        if image is None or image.size == 0:
            return self._empty_result("Invalid image input")
            
        best_result = self._empty_result("No text detected")
        best_confidence = 0.0
        
        # Try each preprocessing strategy
        for i, strategy in enumerate(self.preprocess_strategies):
            try:
                if debug:
                    logger.info(f"🔄 Trying strategy {i+1}: {strategy.__name__}")
                    
                # Apply preprocessing
                processed_image = strategy(image)
                if processed_image is None:
                    continue
                    
                # Extract text
                text = self._extract_text_single(processed_image)
                
                # Calculate confidence
                confidence = self._calculate_confidence(processed_image, text)
                
                if debug:
                    logger.info(f"   📝 Text: '{text[:50]}...'")
                    logger.info(f"   📊 Confidence: {confidence:.3f}")
                
                # Check if this is the best result so far
                if confidence > best_confidence and text.strip():
                    best_result = {
                        'text': text.strip(),
                        'confidence': confidence,
                        'strategy_used': strategy.__name__,
                        'preprocessing_time': time.time() - start_time
                    }
                    best_confidence = confidence
                    
                    # If we have high confidence, we can stop early
                    if confidence >= 0.9:
                        break
                        
            except Exception as e:
                if debug:
                    logger.warning(f"   ⚠️ Strategy {i+1} failed: {str(e)}")
                continue
                
        # Final result
        processing_time = time.time() - start_time
        best_result['preprocessing_time'] = processing_time
        
        if debug:
            logger.info(f"✅ Best result: {best_result['confidence']:.3f} confidence using {best_result['strategy_used']}")
            
        return best_result
        
    def _empty_result(self, message: str) -> Dict[str, Union[str, float]]:
        """Return empty result with metadata"""
        return {
            'text': '',
            'confidence': 0.0,
            'strategy_used': 'none',
            'preprocessing_time': 0.0,
            'error': message
        }
        
    def _extract_text_single(self, image: np.ndarray) -> str:
        """Extract text from single processed image"""
        try:
            # Get detailed data for confidence calculation
            data = pytesseract.image_to_data(image, lang=self.languages, output_type=pytesseract.Output.DICT)
            
            # Extract text with confidence filtering
            n_boxes = len(data['text'])
            confidence_scores = []
            text_parts = []
            
            for i in range(n_boxes):
                conf = int(data['conf'][i])
                if conf > 0:  # Filter out -1 confidence
                    text = data['text'][i].strip()
                    if text:
                        confidence_scores.append(conf / 100.0)
                        text_parts.append(text)
                        
            # Return joined text
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.warning(f"OCR extraction failed: {str(e)}")
            return ""
            
    def _calculate_confidence(self, image: np.ndarray, text: str) -> float:
        """Calculate confidence score for OCR result"""
        if not text.strip():
            return 0.0
            
        try:
            # Get detailed data
            data = pytesseract.image_to_data(image, lang=self.languages, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence of detected text
            confidences = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                conf = int(data['conf'][i])
                if conf > 0 and data['text'][i].strip():
                    confidences.append(conf / 100.0)
                    
            if not confidences:
                return 0.0
                
            avg_confidence = np.mean(confidences)
            
            # Additional factors
            text_length_factor = min(len(text) / 10.0, 1.0)  # Longer text = more confident
            unique_chars_factor = len(set(text.lower())) / max(len(text), 1)  # Reasonable character diversity
            
            # Final confidence score
            final_confidence = avg_confidence * 0.7 + text_length_factor * 0.2 + unique_chars_factor * 0.1
            
            return min(final_confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {str(e)}")
            return 0.0
            
    # === PREPROCESSING STRATEGIES ===
    
    def _original_strategy(self, image: np.ndarray) -> np.ndarray:
        """Original image (no preprocessing)"""
        return image.copy()
        
    def _grayscale_strategy(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
        
    def _threshold_strategy(self, image: np.ndarray) -> np.ndarray:
        """Apply binary threshold"""
        gray = self._grayscale_strategy(image)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
        
    def _adaptive_threshold_strategy(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive threshold"""
        gray = self._grayscale_strategy(image)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return thresh
        
    def _denoise_strategy(self, image: np.ndarray) -> np.ndarray:
        """Apply noise reduction"""
        gray = self._grayscale_strategy(image)
        denoised = cv2.medianBlur(gray, 3)
        return denoised
        
    def _enhance_contrast_strategy(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast"""
        gray = self._grayscale_strategy(image)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        return enhanced
        
    def _sharpen_strategy(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpening filter"""
        gray = self._grayscale_strategy(image)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        return sharpened
        
    def _morphology_strategy(self, image: np.ndarray) -> np.ndarray:
        """Apply morphological operations"""
        gray = self._grayscale_strategy(image)
        
        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        # Apply morphological closing to connect text components
        morphed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        return morphed
        
    def _combined_strategy(self, image: np.ndarray) -> np.ndarray:
        """Combined preprocessing approach"""
        gray = self._grayscale_strategy(image)
        
        # Apply multiple enhancements
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Final threshold
        _, final = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return final
        
    def analyze_image_quality(self, image: np.ndarray) -> Dict[str, Union[float, str]]:
        """Analyze image quality untuk debugging"""
        analysis = {}
        
        try:
            # Basic image properties
            analysis['width'] = image.shape[1]
            analysis['height'] = image.shape[0]
            analysis['channels'] = image.shape[2] if len(image.shape) == 3 else 1
            
            # Convert to grayscale for analysis
            gray = self._grayscale_strategy(image)
            
            # Calculate statistics
            analysis['mean_brightness'] = float(np.mean(gray))
            analysis['std_brightness'] = float(np.std(gray))
            analysis['contrast'] = float(np.std(gray))
            
            # Noise estimation (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            analysis['sharpness'] = float(laplacian_var)
            
            # Text density estimation
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            white_pixels = np.sum(binary == 255)
            black_pixels = np.sum(binary == 0)
            total_pixels = binary.size
            
            analysis['text_density'] = float(black_pixels / total_pixels)
            
            # Quality assessment
            quality_score = 0.0
            
            # Brightness check
            if 50 <= analysis['mean_brightness'] <= 200:
                quality_score += 0.25
                
            # Contrast check
            if analysis['contrast'] > 30:
                quality_score += 0.25
                
            # Sharpness check
            if analysis['sharpness'] > 100:
                quality_score += 0.25
                
            # Text density check
            if 0.05 <= analysis['text_density'] <= 0.3:
                quality_score += 0.25
                
            analysis['quality_score'] = quality_score
            
            # Recommendations
            recommendations = []
            if analysis['mean_brightness'] < 50:
                recommendations.append("Increase brightness")
            if analysis['mean_brightness'] > 200:
                recommendations.append("Decrease brightness")
            if analysis['contrast'] < 30:
                recommendations.append("Increase contrast")
            if analysis['sharpness'] < 100:
                recommendations.append("Apply sharpening")
            if analysis['text_density'] < 0.05:
                recommendations.append("Image might be too light or blurry")
            if analysis['text_density'] > 0.3:
                recommendations.append("Image might be too dark")
                
            analysis['recommendations'] = recommendations
            
        except Exception as e:
            analysis['error'] = str(e)
            
        return analysis

def enhanced_ocr_extract(image: np.ndarray, languages: str = "eng+ind", debug: bool = False) -> Dict[str, Union[str, float]]:
    """
    Convenience function untuk enhanced OCR extraction
    
    Args:
        image: Input image (OpenCV format)
        languages: Tesseract languages
        debug: Enable debug logging
        
    Returns:
        Dictionary dengan hasil OCR dan metadata
    """
    ocr = EnhancedOCR(languages=languages)
    return ocr.extract_text(image, debug=debug)

def batch_enhanced_ocr(image_paths: List[str], languages: str = "eng+ind") -> List[Dict[str, Union[str, float]]]:
    """
    Process multiple images dengan enhanced OCR
    
    Args:
        image_paths: List of image file paths
        languages: Tesseract languages
        
    Returns:
        List of OCR results
    """
    results = []
    ocr = EnhancedOCR(languages=languages)
    
    for path in image_paths:
        try:
            image = cv2.imread(path)
            if image is not None:
                result = ocr.extract_text(image, debug=False)
                result['file_path'] = path
                result['file_name'] = os.path.basename(path)
                results.append(result)
            else:
                results.append({
                    'text': '',
                    'confidence': 0.0,
                    'strategy_used': 'none',
                    'error': f'Could not load image: {path}',
                    'file_path': path,
                    'file_name': os.path.basename(path)
                })
        except Exception as e:
            results.append({
                'text': '',
                'confidence': 0.0,
                'strategy_used': 'none',
                'error': str(e),
                'file_path': path,
                'file_name': os.path.basename(path)
            })
            
    return results

# === BACKWARD COMPATIBILITY FUNCTIONS ===

def extract_text_with_fallback(image: np.ndarray, languages: str = "eng+ind") -> Tuple[str, float]:
    """
    Backward compatibility function - extract text dengan fallback strategies
    
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    result = enhanced_ocr_extract(image, languages=languages, debug=False)
    return result['text'], result['confidence']

def preprocess_image_for_ocr(image: np.ndarray, strategy: str = "auto") -> np.ndarray:
    """
    Preprocess image untuk OCR dengan strategy tertentu
    
    Args:
        image: Input image
        strategy: Preprocessing strategy ('auto', 'grayscale', 'threshold', etc.)
        
    Returns:
        Preprocessed image
    """
    ocr = EnhancedOCR()
    
    if strategy == "auto":
        # Analyze image and choose best strategy
        analysis = ocr.analyze_image_quality(image)
        quality_score = analysis.get('quality_score', 0.0)
        
        if quality_score > 0.7:
            return image  # Good quality, no preprocessing needed
        elif quality_score > 0.4:
            return ocr._enhance_contrast_strategy(image)
        else:
            return ocr._combined_strategy(image)
    else:
        # Apply specific strategy
        strategies = {
            'grayscale': ocr._grayscale_strategy,
            'threshold': ocr._threshold_strategy,
            'adaptive': ocr._adaptive_threshold_strategy,
            'denoise': ocr._denoise_strategy,
            'contrast': ocr._enhance_contrast_strategy,
            'sharpen': ocr._sharpen_strategy,
            'morphology': ocr._morphology_strategy,
            'combined': ocr._combined_strategy
        }
        
        strategy_func = strategies.get(strategy, ocr._original_strategy)
        return strategy_func(image)

if __name__ == "__main__":
    # Test the enhanced OCR
    import os
    
    print("🧪 Testing Enhanced OCR...")
    
    # Create a simple test image
    test_img = np.ones((100, 300, 3), dtype=np.uint8) * 255
    
    # Add some text-like patterns
    cv2.rectangle(test_img, (20, 20), (280, 60), (0, 0, 0), -1)
    cv2.putText(test_img, "TEST", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Test OCR
    ocr = EnhancedOCR()
    
    print("\n📊 Image Quality Analysis:")
    analysis = ocr.analyze_image_quality(test_img)
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 OCR Extraction Test:")
    result = ocr.extract_text(test_img, debug=True)
    
    print(f"\n✅ Final Result:")
    print(f"  Text: '{result['text']}'")
    print(f"  Confidence: {result['confidence']:.3f}")
    print(f"  Strategy: {result['strategy_used']}")
    print(f"  Time: {result['preprocessing_time']:.3f}s")
