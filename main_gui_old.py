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
        if self.template_tab.template_gui:
            self.template_tab.template_gui.on_template_created_callback = self._on_template_created
    
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
        self.notebook.select(self.ocr_tab.parent_frame)
        
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

    # ============================================================================
    # SCREENSHOT TAB METHODS / METODE TAB SCREENSHOT
    # ============================================================================
    
    def setup_screenshot_tab(self):
        """
        Setup the screenshot tab with controls and log area
        Siapkan tab screenshot dengan kontrol dan area log
        
        This tab contains:
        - Folder selection / Pemilihan folder
        - Screenshot button / Tombol screenshot
        - Log area / Area log
        """
        # Create header frame / Buat frame header
        header_frame = create_modern_frame(self.screenshot_frame)
        header_frame.pack(fill=tk.X, pady=(20, 20))
        create_modern_label(header_frame, "📸 Screenshot Tools", style='Modern.TLabel').pack()
        
        # Create folder selection section / Buat bagian pemilihan folder
        folder_section = create_modern_frame(self.screenshot_frame, padding=20)
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
        screenshot_section = create_modern_frame(self.screenshot_frame, padding=20)
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
        Open directory browser to select screenshot output folder
        Buka browser direktori untuk memilih folder output screenshot
        
        When user selects a folder:
        - Updates the folder path / Memperbarui path folder
        - Creates folder if it doesn't exist / Membuat folder jika belum ada
        - Updates the log / Memperbarui log
        """
        folder_path = filedialog.askdirectory(
            title="Pilih Folder Output Screenshot",  # Select Screenshot Output Folder
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

    # ============================================================================
    # TEMPLATE TAB METHODS / METODE TAB TEMPLATE
    # ============================================================================
    
    def setup_template_tab(self):
        """
        Setup the template creator tab
        Siapkan tab pembuat template
        
        This tab contains:
        - Template editing interface / Antarmuka editing template
        - Field selection tools / Alat pemilihan field
        - Template save/load functionality / Fungsi simpan/muat template
        """
        # Create header / Buat header
        header_frame = create_modern_frame(self.template_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        create_modern_label(header_frame, "📐 Template Creator", style='Modern.TLabel').pack()
        
        # Initialize template GUI component / Inisialisasi komponen GUI template
        self.template_gui = ModernTemplateGUI(self.template_frame)

    # ============================================================================
    # OCR TAB METHODS / METODE TAB OCR
    # ============================================================================
    
    def setup_ocr_tab(self):
        """
        Setup the OCR processing tab
        Siapkan tab pemrosesan OCR
        
        This tab contains:
        - Template selection / Pemilihan template
        - Input/output folder selection / Pemilihan folder input/output
        - Export format options / Opsi format export
        - Process log / Log proses
        - Folder structure treeview / Treeview struktur folder
        """
        # Create header / Buat header
        header_frame = create_modern_frame(self.ocr_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        create_modern_label(header_frame, "🔍 OCR Processing", style='Modern.TLabel').pack()
        
        # Content area with left (controls) and right (preview) panels
        # Area konten dengan panel kiri (kontrol) dan kanan (pratinjau)
        content_frame = tk.Frame(self.ocr_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # ========================================
        # Left Panel: Controls / Panel Kiri: Kontrol
        # ========================================
        left_panel = create_modern_frame(content_frame, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # --- Template Selection Section ---
        # Bagian Pemilihan Template
        template_row = create_modern_frame(left_panel, padding=5)
        template_row.pack(fill=tk.X, pady=(0, 8))
        
        create_modern_label(template_row, "📄 Template JSON:", style='Modern.TLabel').pack(side=tk.LEFT)
        
        # Label to show selected template / Label untuk menampilkan template yang dipilih
        self.template_label = create_modern_label(template_row, "Belum dipilih", style='Modern.TLabel')
        self.template_label.pack(side=tk.LEFT, padx=10)
        
        # Combobox for template selection / Combobox untuk pemilihan template
        self.templates_combobox = ttk.Combobox(template_row, state='readonly', width=30)
        self.templates_combobox.pack(side=tk.RIGHT, padx=(0, 10))
        self.templates_combobox.bind('<<ComboboxSelected>>', self.on_template_select)
        
        # Refresh button to update template list / Tombol refresh untuk memperbarui daftar template
        refresh_btn = create_modern_button(
            template_row,
            "🔄 Refresh",
            lambda: self.refresh_templates(),
            style='Secondary.TButton'
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Button to manually select template / Tombol untuk memilih template secara manual
        self.template_btn = create_modern_button(
            template_row,
            "📁 Pilih Template",
            self.pick_template,
            style='Secondary.TButton'
        )
        self.template_btn.pack(side=tk.RIGHT)
        
        # Button to open template in creator / Tombol untuk membuka template di pembuat
        open_creator_btn = create_modern_button(
            template_row,
            "✏️ Buka di Template Creator",
            lambda: self.open_template_in_creator(),
            style='Secondary.TButton'
        )
        open_creator_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Load available templates on startup / Muat template yang tersedia saat startup
        try:
            self.refresh_templates()
        except Exception:
            pass
        
        # --- Input Mode Selection Section ---
        # Bagian Pemilihan Mode Input
        mode_row = create_modern_frame(left_panel, padding=5)
        mode_row.pack(fill=tk.X, pady=(6, 6))
        create_modern_label(mode_row, "Mode Input:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.input_mode_var = tk.StringVar(value="folder")  # Default: folder mode / Default: mode folder
        
        # Radio buttons for input mode selection / Tombol radio untuk pemilihan mode input
        rb1 = tk.Radiobutton(
            mode_row, 
            text="Folder (Batch)", 
            variable=self.input_mode_var, 
            value="folder",
            indicatoron=0, 
            width=12
        )
        rb2 = tk.Radiobutton(
            mode_row, 
            text="Single File", 
            variable=self.input_mode_var, 
            value="file",
            indicatoron=0, 
            width=12
        )
        rb1.pack(side=tk.LEFT, padx=6)
        rb2.pack(side=tk.LEFT, padx=6)
        
        # --- Input Folder Selection Section ---
        # Bagian Pemilihan Folder Input
        input_row = create_modern_frame(left_panel, padding=5)
        input_row.pack(fill=tk.X, pady=(0, 8))
        create_modern_label(input_row, "📁 Folder Input:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.input_folder_label = create_modern_label(input_row, "Belum dipilih", style='Modern.TLabel')
        self.input_folder_label.pack(side=tk.LEFT, padx=10)
        self.input_btn = create_modern_button(
            input_row, 
            "📂 Pilih", 
            self.pick_input_folder, 
            style='Secondary.TButton'
        )
        self.input_btn.pack(side=tk.RIGHT)
        
        # --- Input File Selection Section ---
        # Bagian Pemilihan File Input
        file_row = create_modern_frame(left_panel, padding=5)
        file_row.pack(fill=tk.X, pady=(0, 8))
        create_modern_label(file_row, "📄 File Input:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.input_file_label = create_modern_label(file_row, "Belum dipilih", style='Modern.TLabel')
        self.input_file_label.pack(side=tk.LEFT, padx=10)
        self.input_file_btn = create_modern_button(
            file_row, 
            "📄 Pilih File", 
            self.pick_input_file, 
            style='Secondary.TButton'
        )
        self.input_file_btn.pack(side=tk.RIGHT)
        
        # --- Output Folder Selection Section ---
        # Bagian Pemilihan Folder Output
        output_row = create_modern_frame(left_panel, padding=5)
        output_row.pack(fill=tk.X, pady=(0, 8))
        create_modern_label(output_row, "📁 Folder Output:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.output_folder_label = create_modern_label(output_row, "Belum dipilih", style='Modern.TLabel')
        self.output_folder_label.pack(side=tk.LEFT, padx=10)
        self.output_btn = create_modern_button(
            output_row, 
            "📂 Pilih", 
            self.pick_output_folder, 
            style='Secondary.TButton'
        )
        self.output_btn.pack(side=tk.RIGHT)
        
        # --- Export Format Selection Section ---
        # Bagian Pemilihan Format Export
        export_row = create_modern_frame(left_panel, padding=5)
        export_row.pack(fill=tk.X, pady=(0, 8))
        create_modern_label(export_row, "📊 Export:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.export_format_var = tk.StringVar(value="CSV")
        self.export_format_combo = ttk.Combobox(
            export_row,
            textvariable=self.export_format_var,
            values=["CSV", "Excel"],
            state="readonly",
            font=('Consolas', 9),
            width=10
        )
        self.export_format_combo.pack(side=tk.LEFT, padx=10)
        
        # --- Action Button Section ---
        # Bagian Tombol Aksi
        action_row = create_modern_frame(left_panel, padding=5)
        action_row.pack(fill=tk.X, pady=(10, 0))
        self.start_btn = create_modern_button(
            action_row, 
            "🚀 Mulai OCR", 
            self.run_ocr, 
            style='Accent.TButton'
        )
        self.start_btn.pack(fill=tk.X)
        
        # Timer and loading indicator / Timer dan indikator loading
        self.ocr_timer_label = create_modern_label(left_panel, "Waktu: 00:00", style='Modern.TLabel')
        self.ocr_timer_label.pack(pady=(8, 0))
        
        self.ocr_loading_label = create_modern_label(left_panel, "", style='Modern.TLabel')
        self.ocr_loading_label.pack()
        
        # ========================================
        # Right Panel: Preview & Log / Panel Kanan: Pratinjau & Log
        # ========================================
        right_panel = create_modern_frame(content_frame, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- Folder Structure Treeview ---
        # Treeview Struktur Folder
        tree_section = create_modern_frame(right_panel, padding=5)
        tree_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        create_modern_label(tree_section, "🗂️ Struktur Folder Input:", style='Modern.TLabel').pack(anchor='w')
        tree_frame = tk.Frame(tree_section, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        
        self.input_tree = ttk.Treeview(tree_frame, show='tree')
        tree_v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.input_tree.yview)
        self.input_tree.configure(yscrollcommand=tree_v_scroll.set)
        self.input_tree.grid(row=0, column=0, sticky="nsew")
        tree_v_scroll.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # --- Process Log Section ---
        # Bagian Log Proses
        log_section = create_modern_frame(right_panel, padding=5)
        log_section.pack(fill=tk.BOTH, expand=True)
        create_modern_label(log_section, "📊 Process Log:", style='Modern.TLabel').pack(anchor='w', pady=(0, 8))
        log_frame = tk.Frame(log_section, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b'
        )
        self.log.pack(fill=tk.BOTH, expand=True)

    # ============================================================================
    # SCREENSHOT METHODS / METODE SCREENSHOT
    # ============================================================================
    
    def open_screenshot(self):
        """
        Open screenshot capture window
        Buka jendela pengambilan screenshot
        
        Creates a new Toplevel window with ScreenshotMiniGUI
        that allows user to capture screenshots with F9 hotkey
        """
        win = tk.Toplevel(self.root)
        ScreenshotMiniGUI(
            win, 
            callback=self.after_screenshot, 
            save_dir=self.image_folder, 
            hotkey="F9"
        )

    def after_screenshot(self, path):
        """
        Handle screenshot completion callback
        Tangani callback penyelesaian screenshot
        
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
            
            # Update main log if available / Perbarui log utama jika tersedia
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"✅ Screenshot baru: {os.path.basename(path)}\n")
                self.log.see(tk.END)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Gagal memproses screenshot: {str(e)}")

    # ============================================================================
    # TEMPLATE METHODS / METODE TEMPLATE
    # ============================================================================
    
    def on_template_created(self, template_path):
        """
        Callback when a new template is created
        Callback ketika template baru dibuat
        
        Args:
            template_path: Path to the new template / Path ke template baru
        """
        self.current_template_path = template_path
        self.template_label.config(text=os.path.basename(template_path), foreground="#10b981")
        
        if hasattr(self, 'log'):
            self.log.insert(tk.END, f"✅ Template baru dibuat: {template_path}\n")
            self.log.see(tk.END)
        
        # Switch to OCR tab / Beralih ke tab OCR
        self.notebook.select(self.ocr_frame)

    def pick_template(self):
        """
        Open file dialog to select existing template
        Buka dialog file untuk memilih template yang ada
        """
        self.template = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if self.template:
            self.current_template_path = self.template
            self.template_label.config(text=os.path.basename(self.template), foreground="#10b981")
            
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📁 Template dipilih: {self.template}\n")
                self.log.see(tk.END)

    def list_templates(self):
        """
        Scan template directory and return list of template paths
        Pindai direktori template dan kembalikan daftar path template
        
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

    def refresh_templates(self):
        """
        Refresh the templates combobox with available templates
        Segarkan combobox template dengan template yang tersedia
        """
        templates = self.list_templates()
        display = [os.path.basename(p) for p in templates]
        self.template_map = {os.path.basename(p): p for p in templates}
        
        self.templates_combobox['values'] = display
        
        if display:
            try:
                self.templates_combobox.current(0)
            except Exception:
                pass
            self.on_template_select()
        else:
            self.templates_combobox.set('')

    def on_template_select(self, event=None):
        """
        Handle template selection from combobox
        Tangani pemilihan template dari combobox
        
        Args:
            event: Combobox selection event / Event pemilihan combobox
        """
        name = self.templates_combobox.get()
        if not name:
            return
        
        path = self.template_map.get(name)
        if path:
            self.current_template_path = path
            self.template_label.config(text=name, foreground="#10b981")
            
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📁 Template dipilih: {path}\n")
                self.log.see(tk.END)

    def open_template_in_creator(self):
        """
        Open selected template in the Template Creator tab
        Buka template yang dipilih di tab Pembuat Template
        """
        if not self.current_template_path:
            messagebox.showwarning(
                "⚠️ Warning", 
                "Pilih template terlebih dahulu dari daftar atau gunakan 'Pilih Template'."
            )
            return

        try:
            if hasattr(self, 'template_gui') and self.template_gui:
                ok = self.template_gui.load_template(self.current_template_path)
                if ok:
                    self.notebook.select(self.template_frame)
                    
                    if hasattr(self, 'log'):
                        self.log.insert(
                            tk.END, 
                            f"✏️ Membuka template di Template Creator: {self.current_template_path}\n"
                        )
                        self.log.see(tk.END)
            else:
                messagebox.showinfo("Info", "Template Creator tidak tersedia saat ini.")
        except Exception as e:
            messagebox.showerror(
                "❌ Error", 
                f"Gagal membuka template di Template Creator: {e}"
            )

    # ============================================================================
    # INPUT/OUTPUT METHODS / METODE INPUT/OUTPUT
    # ============================================================================
    
    def pick_input_folder(self):
        """
        Open directory browser to select input folder
        Buka browser direktori untuk memilih folder input
        """
        folder_path = filedialog.askdirectory(title="Pilih Folder Input Gambar")
        if folder_path:
            self.input_folder_path = folder_path
            self.input_folder_label.config(
                text=os.path.basename(folder_path), 
                foreground="#10b981"
            )
            
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📁 Folder input dipilih: {folder_path}\n")
                self.log.see(tk.END)
            
            # Display folder structure / Tampilkan struktur folder
            try:
                self.display_folder_structure(folder_path)
            except Exception as e:
                print(f"Gagal menampilkan struktur folder: {e}")

    def pick_input_file(self):
        """
        Open file browser to select single input file
        Buka browser file untuk memilih file input tunggal
        """
        file_path = filedialog.askopenfilename(
            title="Pilih File Input Gambar",
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg")
            ]
        )
        if file_path:
            self.input_file_path = file_path
            self.input_file_label.config(
                text=os.path.basename(file_path), 
                foreground="#10b981"
            )
            
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📄 File input dipilih: {file_path}\n")
                self.log.see(tk.END)

    def pick_output_folder(self):
        """
        Open directory browser to select output folder
        Buka browser direktori untuk memilih folder output
        """
        folder_path = filedialog.askdirectory(title="Pilih Folder Output Hasil OCR")
        if folder_path:
            self.output_folder_path = folder_path
            self.output_folder_label.config(
                text=os.path.basename(folder_path), 
                foreground="#10b981"
            )
            
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📁 Folder output dipilih: {folder_path}\n")
                self.log.see(tk.END)

    def clear_input_tree(self):
        """
        Clear all items from the input folder treeview
        Hapus semua item dari treeview folder input
        """
        try:
            for item in self.input_tree.get_children():
                self.input_tree.delete(item)
        except Exception:
            pass

    def display_folder_structure(self, folder_path):
        """
        Display folder structure in the treeview
        Tampilkan struktur folder di treeview
        
        Args:
            folder_path: Path to the folder to display / Path ke folder yang akan ditampilkan
        """
        if not folder_path:
            return

        # Normalize and verify path / Normalisasi dan verifikasi path
        base_path = os.path.normpath(os.path.abspath(folder_path))
        if not os.path.isdir(base_path):
            return

        self.clear_input_tree()

        # Insert root folder / Masukkan folder root
        root_name = os.path.basename(base_path) or base_path
        root_id = self.input_tree.insert('', 'end', text=root_name, open=True)

        nodes = {base_path: root_id}

        # Walk through directory / Jelajahi direktori
        for current_root, dirs, files in os.walk(base_path):
            current_root_norm = os.path.normpath(os.path.abspath(current_root))
            
            if not current_root_norm.startswith(base_path):
                continue

            parent_id = nodes.get(current_root_norm, root_id)

            # Sort for consistent display / Urutkan untuk tampilan konsisten
            dirs.sort()
            files.sort()

            # Add directories / Tambahkan direktori
            for d in dirs:
                full_d = os.path.normpath(os.path.join(current_root_norm, d))
                try:
                    nid = self.input_tree.insert(parent_id, 'end', text=d, open=False)
                    nodes[full_d] = nid
                except Exception:
                    continue

            # Add files / Tambahkan file
            for f in files:
                try:
                    self.input_tree.insert(parent_id, 'end', text=f, open=False)
                except Exception:
                    continue

    # ============================================================================
    # OCR PROCESSING METHODS / METODE PEMROSESAN OCR
    # ============================================================================
    
    def _update_ocr_timer(self):
        """
        Update the elapsed time display during OCR processing
        Perbarui tampilan waktu yang telah berlalu selama pemrosesan OCR
        """
        if not getattr(self, '_ocr_running', False):
            return
        
        elapsed = int(time.time() - getattr(self, '_ocr_start_time', time.time()))
        mins, secs = divmod(elapsed, 60)
        self.ocr_timer_label.config(text=f"Waktu: {mins:02d}:{secs:02d}")
        
        # Schedule next update / Jadwalkan pembaruan berikutnya
        self._ocr_timer_job = self.root.after(1000, self._update_ocr_timer)

    def _animate_ocr_loading(self):
        """
        Animate loading indicator during OCR processing
        Animasi indikator loading selama pemrosesan OCR
        """
        if not getattr(self, '_ocr_running', False):
            self.ocr_loading_label.config(text="")
            return
        
        self._loading_dots = (getattr(self, '_loading_dots', 0) + 1) % 4
        dots = '.' * self._loading_dots
        self.ocr_loading_label.config(text=f"Status: Running{dots}")
        
        # Schedule next animation frame / Jadwalkan frame animasi berikutnya
        self._ocr_anim_job = self.root.after(500, self._animate_ocr_loading)

    def _stop_ocr_ui(self):
        """
        Stop OCR processing UI indicators and re-enable controls
        Hentikan indikator UI pemrosesan OCR dan aktifkan kembali kontrol
        """
        self._ocr_running = False
        
        # Cancel timer / Batalkan timer
        try:
            if hasattr(self, '_ocr_timer_job'):
                self.root.after_cancel(self._ocr_timer_job)
        except Exception:
            pass
        
        # Cancel animation / Batalkan animasi
        try:
            if hasattr(self, '_ocr_anim_job'):
                self.root.after_cancel(self._ocr_anim_job)
        except Exception:
            pass
        
        # Re-enable controls / Aktifkan kembali kontrol
        try:
            self.template_btn.config(state=tk.NORMAL)
            self.input_btn.config(state=tk.NORMAL)
            try:
                self.input_file_btn.config(state=tk.NORMAL)
            except Exception:
                pass
            self.output_btn.config(state=tk.NORMAL)
            self.start_btn.config(state=tk.NORMAL)
        except Exception:
            pass

    def run_ocr(self):
        """
        Start OCR processing with selected options
        Mulai pemrosesan OCR dengan opsi yang dipilih
        
        This method:
        - Validates input parameters / Validasi parameter input
        - Disables UI controls during processing / Nonaktifkan kontrol UI selama pemrosesan
        - Starts background worker thread / Mulai thread worker latar belakang
        - Shows timer and loading indicator / Tampilkan timer dan indikator loading
        """
        # Validate template selection / Validasi pemilihan template
        if not self.current_template_path:
            messagebox.showerror(
                "❌ Error", 
                "Template belum dipilih. Buat template di tab Template Creator atau pilih template existing."
            )
            return

        # Validate input according to selected mode / Validasi input sesuai mode yang dipilih
        mode = getattr(self, 'input_mode_var', tk.StringVar(value="folder")).get()
        
        if mode == "folder":
            if not self.input_folder_path:
                messagebox.showerror(
                    "❌ Error", 
                    "Folder input belum dipilih untuk mode batch."
                )
                return
        else:
            if not getattr(self, 'input_file_path', ""):
                messagebox.showerror(
                    "❌ Error", 
                    "File input belum dipilih untuk mode single-file."
                )
                return

        # Disable controls during processing / Nonaktifkan kontrol selama pemrosesan
        try:
            self.template_btn.config(state=tk.DISABLED)
            self.input_btn.config(state=tk.DISABLED)
            try:
                self.input_file_btn.config(state=tk.DISABLED)
            except Exception:
                pass
            self.output_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.DISABLED)
        except Exception:
            pass

        # Initialize timer/animation state / Inisialisasi state timer/animasi
        self._ocr_running = True
        self._ocr_start_time = time.time()
        self._loading_dots = 0

        # Start UI timers / Mulai timer UI
        self._update_ocr_timer()
        self._animate_ocr_loading()

        # Start worker thread / Mulai thread worker
        thread = threading.Thread(target=self._ocr_worker, daemon=True)
        thread.start()

