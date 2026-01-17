"""
Template Tab Module / Modul Tab Template
=========================================
Handles template creation and selection functionality.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import os

from modern_styles import create_modern_frame, create_modern_button, create_modern_label
from template_gui import ModernTemplateGUI


class TemplateTab:
    """
    Manages the Template Creator tab interface and functionality.
    Mengelola antarmuka dan fungsionalitas tab Pembuat Template.
    """
    
    def __init__(self, parent_frame, templates_dir="Template"):
        """
        Initialize the Template Tab.
        
        Args:
            parent_frame: Parent tkinter frame / Frame induk tkinter
            templates_dir: Directory for storing templates / Direktori untuk menyimpan template
        """
        self.parent_frame = parent_frame
        self.templates_dir = templates_dir
        self.template_gui = None
        self.template_map = {}
        self.current_template_path = ""
        self.parent_callback = None
        
        # Ensure template directory exists / Pastikan direktori template ada
        os.makedirs(self.templates_dir, exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Setup the template tab UI components.
        Siapkan komponen UI tab template.
        """
        # Create header / Buat header
        header_frame = create_modern_frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        create_modern_label(header_frame, "📐 Template Creator", style='Modern.TLabel').pack()
        
        # Initialize template GUI component / Inisialisasi komponen GUI template
        self.template_gui = ModernTemplateGUI(self.parent_frame)
    
    def on_template_created(self, template_path):
        """
        Callback when a new template is created.
        Callback ketika template baru dibuat.
        
        Args:
            template_path: Path to the new template / Path ke template baru
        """
        self.current_template_path = template_path
        
        # Call parent callback if set / Panggil callback parent jika diatur
        if hasattr(self, 'parent_callback') and self.parent_callback:
            self.parent_callback(template_path)
    
    def set_parent_callback(self, callback):
        """
        Set callback to be called when template is created.
        Atur callback untuk dipanggil ketika template dibuat.
        
        Args:
            callback: Callback function to call / Fungsi callback untuk dipanggil
        """
        self.parent_callback = callback
    
    def list_templates(self):
        """
        Scan template directory and return list of template paths.
        Pindai direktori template dan kembalikan daftar path template.
        
        Returns:
            list: Sorted list of template file paths / Daftar terurut path file template
        """
        results = []
        try:
            for fname in os.listdir(self.templates_dir):
                if fname.lower().endswith('.json'):
                    results.append(os.path.join(self.templates_dir, fname))
        except Exception:
            pass
        return sorted(results)
    
    def get_template_gui(self):
        """
        Get the template GUI instance.
        Dapatkan instance GUI template.
        
        Returns:
            ModernTemplateGUI: The template GUI instance / Instance GUI template
        """
        return self.template_gui
