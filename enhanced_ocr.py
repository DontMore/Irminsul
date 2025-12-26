import cv2
import numpy as np
import pytesseract
from PIL import Image
import time

class EnhancedOCR:
    def __init__(self, languages="eng", confidence_threshold=0.5):
        self.languages = languages
        self.confidence_threshold = confidence_threshold
        self.strategies = [
            "original",
            "grayscale",
            "binary",
            "denoise",
            "morphology",
            "contrast_enhancement"
        ]

    def extract_text(self, image, debug=False):
        """Extract text using multiple preprocessing strategies"""
        if isinstance(image, np.ndarray):
            # Convert OpenCV BGR to RGB PIL Image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            raise ValueError("Image must be numpy array or PIL Image")

        best_result = {
            'text': '',
            'confidence': 0.0,
            'strategy_used': 'none'
        }

        # Try different preprocessing strategies
        for strategy in self.strategies:
            try:
                processed_image = self._apply_preprocessing(pil_image, strategy)
                text, confidence = self._ocr_with_confidence(processed_image)

                if debug:
                    print(f"Strategy: {strategy}, Confidence: {confidence:.3f}, Text: '{text[:50]}...'")

                if confidence > best_result['confidence']:
                    best_result = {
                        'text': text.strip(),
                        'confidence': confidence,
                        'strategy_used': strategy
                    }

                    # Early exit if we have high confidence
                    if confidence >= 0.9:
                        break

            except Exception as e:
                if debug:
                    print(f"Error with strategy {strategy}: {e}")
                continue

        return best_result

    def _apply_preprocessing(self, image, strategy):
        """Apply different preprocessing strategies"""
        # Convert PIL to OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        if strategy == "original":
            return image
        elif strategy == "grayscale":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            return Image.fromarray(gray)
        elif strategy == "binary":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return Image.fromarray(binary)
        elif strategy == "denoise":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray)
            return Image.fromarray(denoised)
        elif strategy == "morphology":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((2, 2), np.uint8)
            morphed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            return Image.fromarray(morphed)
        elif strategy == "contrast_enhancement":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            return Image.fromarray(enhanced)
        else:
            return image

    def _ocr_with_confidence(self, image):
        """Perform OCR and calculate confidence score"""
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                lang=self.languages,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'
            )

            # Extract text and confidences
            texts = []
            confidences = []

            for i, conf in enumerate(data['conf']):
                if int(conf) > 0:  # Filter out negative confidences
                    text = data['text'][i].strip()
                    if text:
                        texts.append(text)
                        confidences.append(int(conf) / 100.0)

            # Combine text
            full_text = ' '.join(texts)

            # Calculate average confidence
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
            else:
                avg_confidence = 0.0

            return full_text, avg_confidence

        except Exception as e:
            print(f"OCR Error: {e}")
            return "", 0.0

def enhanced_ocr_extract(image, languages="eng", confidence_threshold=0.5):
    """Standalone function for enhanced OCR extraction"""
    ocr = EnhancedOCR(languages=languages, confidence_threshold=confidence_threshold)
    return ocr.extract_text(image)
