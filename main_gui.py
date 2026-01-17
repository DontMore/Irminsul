"""
Modern OCR GUI Application / Aplikasi GUI OCR Modern
=====================================================
Main application entry point that orchestrates all GUI tabs and components.

This module provides:
- Main application window management / Manajemen jendela aplikasi utama
- Tab orchestration / Orkestrasi tab
- Inter-tab communication / Komunikasi antar tab

Tab modules are located in the 'tabs' package:
- screenshot_tab.py / ocr_tab.py / template_tab.py / ocr_processing.py

Author: [Your Name]
Version: 1.0.0
"""

import tkinter as tk
from tkinter import messagebox
import os

# Import styling / Impor styling
from modern_styles import apply_modern_styling, create_modern_notebook

# Import tab modules / Impor modul tab
from tabs import ScreenshotTab, TemplateTab, OCRTab, OCRProcessing


class ModernOCRGui:
    """
    Main GUI class for Modern OCR Application.
    Kelas GUI utama untuk Aplikasi OCR Modern.
    
    This class manages:
    - Main application window / Jendela aplikasi utama
    - Tab instantiation and setup / Instansiasi dan setup tab
    - Inter-tab communication / Komunikasi antar tab
    - Template selection and template-related operations / Pemilihan template dan operasi terkait
    """
    
    def __init__(self, root):
        """
        Initialize the main GUI window.
        Menginisialisasi jendela GUI utama.
        
        Args:
            root: tkinter Tk instance / Instansi Tkinter Tk
        """
        self.root = root
        self.root.title("🚀 Modern OCR GUI - Screenshot + Template Creator + Docker")
        self.root.geometry("1200x800")
        
        # Apply modern styling to the root window / Terapkan styling modern ke jendela utama
        self.modern_styles = apply_modern_styling(root)
        
        # Initialize template-related variables / Inisialisasi variabel terkait template
        self.current_template_path = ""
        self.templates_dir = "Template"
        self.template_map = {}
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Create tabbed interface using modern notebook / Buat antarmuka tab menggunakan notebook modern
        self.notebook = create_modern_notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Initialize tabs / Inisialisasi tab
        self._init_screenshot_tab()
        self._init_template_tab()
        self._init_ocr_tab()
    
    def _init_screenshot_tab(self):
        """
        Initialize the Screenshot tab.
        Inisialisasi tab Screenshot.
        """
        screenshot_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(screenshot_frame, text="📸 Screenshot")
        
        # Create screenshot tab instance / Buat instance tab screenshot
        self.screenshot_tab = ScreenshotTab(screenshot_frame)
    
    def _init_template_tab(self):
        """
        Initialize the Template Creator tab.
        Inisialisasi tab Pembuat Template.
        """
        template_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(template_frame, text="📐 Template Creator")
        
        # Create template tab instance / Buat instance tab template
        self.template_tab = TemplateTab(template_frame, self.templates_dir)
        
        # Connect template creation callback / Hubungkan callback pembuatan template
        # Attach callback to parent frame so template_gui can find it
        template_frame.on_template_created = self._on_template_created
        
        # Also set parent callback on template_tab / Juga atur parent callback pada template_tab
        self.template_tab.set_parent_callback(self._on_template_created)
    
    def _init_ocr_tab(self):
        """
        Initialize the OCR Process tab.
        Inisialisasi tab Proses OCR.
        """
        ocr_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ocr_frame, text="🔍 OCR Process")
        
        # Create OCR tab instance / Buat instance tab OCR
        self.ocr_tab = OCRTab(ocr_frame)
        
        # Create OCR processing handler / Buat handler pemrosesan OCR
        self.ocr_processing = OCRProcessing(self.ocr_tab, self.root)
        
        # Connect OCR start button / Hubungkan tombol mulai OCR
        self.ocr_tab.start_btn.config(command=self.ocr_processing.run_ocr)
        
        # Connect template selection callback / Hubungkan callback pemilihan template
        self.ocr_tab.templates_combobox.bind('<<ComboboxSelected>>', self._on_ocr_template_select)
        
        # Connect open template in creator button / Hubungkan tombol buka template di pembuat
        self.ocr_tab.open_creator_btn.config(command=self._open_template_in_creator)
        
        # Connect refresh button / Hubungkan tombol refresh
        # Find and connect the refresh button if it exists in ocr_tab
        try:
            # The refresh button should have been created in ocr_tab setup
            pass
        except Exception:
            pass
        
        # Load available templates on startup / Muat template yang tersedia saat startup
        try:
            self._refresh_templates()
        except Exception:
            pass
    
    def _refresh_templates(self):
        """
        Refresh the templates combobox with available templates.
        Segarkan combobox template dengan template yang tersedia.
        """
        templates = self.template_tab.list_templates()
        display = [os.path.basename(p) for p in templates]
        self.template_map = {os.path.basename(p): p for p in templates}
        
        self.ocr_tab.templates_combobox['values'] = display
        
        if display:
            try:
                self.ocr_tab.templates_combobox.current(0)
                self._on_ocr_template_select()
            except Exception:
                pass
        else:
            self.ocr_tab.templates_combobox.set('')
    
    def _on_ocr_template_select(self, event=None):
        """
        Handle template selection from OCR tab combobox.
        Tangani pemilihan template dari combobox tab OCR.
        
        Args:
            event: Combobox selection event / Event pemilihan combobox
        """
        name = self.ocr_tab.templates_combobox.get()
        if not name:
            return
        
        path = self.template_map.get(name)
        if path:
            self.current_template_path = path
            self.ocr_tab.template_label.config(text=name, foreground="#10b981")
            self.ocr_processing.set_current_template(path)
            
            if self.ocr_tab.log:
                self.ocr_tab.log.insert(tk.END, f"📁 Template dipilih: {path}\n")
                self.ocr_tab.log.see(tk.END)
    
    def _on_template_created(self, template_path):
        """
        Callback when a new template is created in the Template Creator tab.
        Callback ketika template baru dibuat di tab Pembuat Template.
        
        Args:
            template_path: Path to the newly created template / Path ke template yang baru dibuat
        """
        self.current_template_path = template_path
        self._refresh_templates()
        
        # Switch to OCR tab / Beralih ke tab OCR
        self.notebook.select(2)
        
        if self.ocr_tab.log:
            self.ocr_tab.log.insert(tk.END, f"✅ Template baru dibuat: {template_path}\n")
            self.ocr_tab.log.see(tk.END)
    
    def _open_template_in_creator(self):
        """
        Open selected template in the Template Creator tab.
        Buka template yang dipilih di tab Pembuat Template.
        """
        if not self.current_template_path:
            messagebox.showwarning(
                "⚠️ Warning", 
                "Pilih template terlebih dahulu dari daftar atau gunakan 'Pilih Template'."
            )
            return

        try:
            template_gui = self.template_tab.get_template_gui()
            if template_gui:
                ok = template_gui.load_template(self.current_template_path)
                if ok:
                    self.notebook.select(1)  # Select template tab / Pilih tab template
                    
                    if self.ocr_tab.log:
                        self.ocr_tab.log.insert(
                            tk.END, 
                            f"✏️ Membuka template di Template Creator: {self.current_template_path}\n"
                        )
                        self.ocr_tab.log.see(tk.END)
            else:
                messagebox.showinfo("Info", "Template Creator tidak tersedia saat ini.")
        except Exception as e:
            messagebox.showerror(
                "❌ Error", 
                f"Gagal membuka template di Template Creator: {e}"
            )


def main():
    """
    Main entry point for the application.
    Titik masuk utama untuk aplikasi.
    """
    root = tk.Tk()
    app = ModernOCRGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
