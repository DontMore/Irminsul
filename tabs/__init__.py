"""
Tabs Package / Paket Tabs
=========================
Contains modular tab components for the Modern OCR GUI application.
"""

from .screenshot_tab import ScreenshotTab
from .template_tab import TemplateTab
from .ocr_tab import OCRTab
from .ocr_processing import OCRProcessing

__all__ = [
    'ScreenshotTab',
    'TemplateTab',
    'OCRTab',
    'OCRProcessing'
]
