"""
Screenshot Tab Module / Modul Tab Screenshot
=============================================
Handles screenshot capture functionality and UI for the Screenshot tab.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

from modern_styles import create_modern_frame, create_modern_button, create_modern_label
from screenshot import ScreenshotMiniGUI


class ScreenshotTab:
    """
    Manages the Screenshot tab interface and functionality.
    Mengelola antarmuka dan fungsionalitas tab Screenshot.
    """
    
    def __init__(self, parent_frame, image_folder="screenshots"):
        """
        Initialize the Screenshot Tab.
        
        Args:
            parent_frame: Parent tkinter frame / Frame induk tkinter
            image_folder: Default folder for screenshots / Folder default untuk screenshot
        """
        self.parent_frame = parent_frame
        self.image_folder = image_folder
        self.screenshot_log = None
        self.folder_entry = None
        self.folder_var = None
        
        # Ensure screenshot folder exists / Pastikan folder screenshot ada
        os.makedirs(self.image_folder, exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Setup the screenshot tab UI components.
        Siapkan komponen UI tab screenshot.
        """
        # Create header frame / Buat frame header
        header_frame = create_modern_frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(20, 20))
        create_modern_label(header_frame, "📸 Screenshot Tools", style='Modern.TLabel').pack()
        
        # Create folder selection section / Buat bagian pemilihan folder
        folder_section = create_modern_frame(self.parent_frame, padding=20)
        folder_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Row for folder selection / Baris untuk pemilihan folder
        folder_row = create_modern_frame(folder_section, padding=0)
        folder_row.pack(fill=tk.X, pady=(0, 10))
        
        # Label for folder selection / Label untuk pemilihan folder
        create_modern_label(folder_row, "📁 Output Folder:", style='Modern.TLabel').pack(side=tk.LEFT)
        
        # Entry field for folder path / Field entry untuk path folder
        self.folder_var = tk.StringVar(value=self.image_folder)
        self.folder_entry = tk.Entry(
            folder_row, 
            textvariable=self.folder_var,
            font=('Consolas', 9),
            bg='white',
            fg='#1e293b',
            relief='solid',
            borderwidth=1
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15, 10))
        
        # Browse button for folder selection / Tombol browse untuk pemilihan folder
        create_modern_button(
            folder_row, 
            "📂 Browse", 
            self.browse_output_folder, 
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT)

        # Main screenshot section / Bagian utama screenshot
        screenshot_section = create_modern_frame(self.parent_frame, padding=20)
        screenshot_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Button to take screenshot / Tombol untuk mengambil screenshot
        create_modern_button(
            screenshot_section, 
            "🎯 Take Screenshot", 
            self.open_screenshot, 
            style='Modern.TButton'
        ).pack(pady=20)

        # Log area for screenshot activity / Area log untuk aktivitas screenshot
        log_frame = create_modern_frame(screenshot_section, padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        create_modern_label(log_frame, "📝 Screenshot Log", style='Modern.TLabel').pack(anchor="w", pady=(0, 10))
        
        # Text frame for log / Frame text untuk log
        text_frame = tk.Frame(log_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrolled text widget for logging / Widget text dengan scroll untuk logging
        self.screenshot_log = scrolledtext.ScrolledText(
            text_frame, 
            width=50, 
            height=15,
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b'
        )
        self.screenshot_log.pack(fill=tk.BOTH, expand=True)
    
    def browse_output_folder(self):
        """
        Open directory browser to select screenshot output folder.
        Buka browser direktori untuk memilih folder output screenshot.
        """
        folder_path = filedialog.askdirectory(
            title="Pilih Folder Output Screenshot",
            initialdir=self.image_folder
        )
        
        if folder_path:
            try:
                # Create folder if it doesn't exist / Buat folder jika belum ada
                os.makedirs(folder_path, exist_ok=True)
                
                # Update instance variables / Perbarui variabel instance
                self.image_folder = folder_path
                self.folder_var.set(folder_path)
                
                # Log the action / Catat aksi
                self.screenshot_log.insert(tk.END, f"📁 Folder output diubah ke: {folder_path}\n")
                self.screenshot_log.see(tk.END)
            except Exception as e:
                messagebox.showerror("❌ Error", f"Gagal mengakses folder: {str(e)}")
    
    def open_screenshot(self):
        """
        Open screenshot capture window.
        Buka jendela pengambilan screenshot.
        """
        # Create a new Toplevel window with ScreenshotMiniGUI
        win = tk.Toplevel()
        ScreenshotMiniGUI(
            win, 
            callback=self.after_screenshot, 
            save_dir=self.image_folder, 
            hotkey="F9"
        )
    
    def after_screenshot(self, path):
        """
        Handle screenshot completion callback.
        Tangani callback penyelesaian screenshot.
        
        Args:
            path: Path where screenshot was saved / Path tempat screenshot disimpan
        """
        try:
            # Ensure output folder exists / Pastikan folder output ada
            os.makedirs(self.image_folder, exist_ok=True)
            
            # Log screenshot saved / Catat screenshot yang disimpan
            self.screenshot_log.insert(tk.END, f"✅ Screenshot tersimpan: {path}\n")
            self.screenshot_log.insert(tk.END, f"📁 Output folder: {self.image_folder}\n")
            self.screenshot_log.see(tk.END)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Gagal memproses screenshot: {str(e)}")
    
    def get_output_folder(self):
        """
        Get the current output folder path.
        Dapatkan path folder output saat ini.
        
        Returns:
            str: Path to the output folder / Path ke folder output
        """
        return self.image_folder
