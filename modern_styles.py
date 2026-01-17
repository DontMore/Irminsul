"""
Modern styling configuration for GUI application
"""
import tkinter as tk
from tkinter import ttk
import os

class ModernStyles:
    def __init__(self):
        self.colors = {
            # Modern Color Palette
            'primary': '#2563eb',      # Modern blue
            'primary_dark': '#1d4ed8', # Darker blue
            'secondary': '#64748b',    # Slate gray
            'accent': '#10b981',       # Emerald green
            'danger': '#ef4444',       # Red
            'warning': '#f59e0b',      # Amber
            'light': '#f8fafc',        # Light gray
            'dark': '#1e293b',         # Dark gray
            'white': '#ffffff',
            'border': '#e2e8f0',       # Light border
            'hover': '#f1f5f9',        # Hover state
            'success': '#22c55e',      # Success green
            'text_primary': '#0f172a', # Primary text
            'text_secondary': '#64748b', # Secondary text
        }
        
        self.setup_styles()
    
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')  # Modern base theme
        
        # Modern Button Style
        style.configure(
            'Modern.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10),
            background=self.colors['primary'],
            foreground=self.colors['white'],
            borderwidth=0,
            focuscolor='none'
        )
        
        style.map(
            'Modern.TButton',
            background=[('active', self.colors['primary_dark']), 
                       ('pressed', self.colors['primary_dark'])],
            foreground=[('disabled', self.colors['text_secondary'])]
        )
        
        # Modern Secondary Button
        style.configure(
            'Secondary.TButton',
            font=('Segoe UI', 10),
            padding=(15, 8),
            background=self.colors['light'],
            foreground=self.colors['text_primary'],
            borderwidth=1,
            bordercolor=self.colors['border'],
            focuscolor='none'
        )
        
        style.map(
            'Secondary.TButton',
            background=[('active', self.colors['hover'])],
            bordercolor=[('focus', self.colors['primary'])]
        )
        
        # Modern Accent Button (for important actions)
        style.configure(
            'Accent.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10),
            background=self.colors['accent'],
            foreground=self.colors['white'],
            borderwidth=0,
            focuscolor='none'
        )
        
        style.map(
            'Accent.TButton',
            background=[('active', '#059669'), ('pressed', '#059669')]
        )
        
        # Modern Frame Style
        style.configure(
            'Modern.TFrame',
            background=self.colors['white'],
            borderwidth=1,
            bordercolor=self.colors['border'],
            relief='solid'
        )
        
        # Modern LabelFrame Style
        style.configure(
            'Modern.TLabelframe',
            background=self.colors['white'],
            borderwidth=1,
            bordercolor=self.colors['border'],
            relief='solid',
            labelanchor='n'
        )
        
        style.configure(
            'Modern.TLabelframe.Label',
            font=('Segoe UI', 10, 'bold'),
            background=self.colors['white'],
            foreground=self.colors['text_primary']
        )
        
        # Modern Notebook Style
        style.configure(
            'Modern.TNotebook',
            background=self.colors['white'],
            borderwidth=1,
            bordercolor=self.colors['border']
        )
        
        style.configure(
            'Modern.TNotebook.Tab',
            font=('Segoe UI', 9),
            padding=(10, 5),
            background=self.colors['light'],
            foreground=self.colors['text_secondary']
        )
        
        style.map(
            'Modern.TNotebook.Tab',
            background=[('selected', self.colors['primary'])],
            foreground=[('selected', self.colors['white'])]
        )
        
        # Modern Entry Style
        style.configure(
            'Modern.TEntry',
            font=('Segoe UI', 10),
            padding=(10, 8),
            borderwidth=1,
            bordercolor=self.colors['border'],
            focuscolor=self.colors['primary']
        )
        
        style.map(
            'Modern.TEntry',
            bordercolor=[('focus', self.colors['primary'])],
            focuscolor=[('focus', self.colors['primary'])]
        )
        
        # Modern Text Widget Style
        style.configure(
            'Modern.TText',
            font=('Consolas', 9),
            background=self.colors['white'],
            borderwidth=1,
            bordercolor=self.colors['border']
        )
        
        # Modern Scrollbar Style
        style.configure(
            'Modern.Horizontal.TScrollbar',
            background=self.colors['light'],
            borderwidth=1,
            arrowcolor=self.colors['text_secondary']
        )
        
        style.configure(
            'Modern.Vertical.TScrollbar',
            background=self.colors['light'],
            borderwidth=1,
            arrowcolor=self.colors['text_secondary']
        )

def apply_modern_styling(root):
    """Apply modern styling to root window"""
    modern_styles = ModernStyles()
    modern_styles.setup_styles()
    return modern_styles

def create_modern_frame(parent, style='Modern.TFrame', padding=10):
    """Create a modern styled frame"""
    return ttk.Frame(parent, style=style, padding=padding)

def create_modern_button(parent, text, command, style='Modern.TButton', width=None):
    """Create a modern styled button"""
    return ttk.Button(parent, text=text, command=command, style=style, width=width)

def create_modern_label(parent, text, style='Modern.TLabel'):
    """Create a modern styled label"""
    label = ttk.Label(parent, text=text, style=style)
    return label

def create_modern_notebook(parent):
    """Create a modern styled notebook (tabbed interface)"""
    return ttk.Notebook(parent, style='Modern.TNotebook')

