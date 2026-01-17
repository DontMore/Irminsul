"""Thin wrappers around `modern_styles` to centralize UI creation.

Keep imports lightweight here; UI modules import these helpers instead of
directly depending on `modern_styles` everywhere.
"""
from modern_styles import create_modern_frame, create_modern_button, create_modern_label, create_modern_notebook

__all__ = [
    "create_modern_frame",
    "create_modern_button",
    "create_modern_label",
    "create_modern_notebook",
]
