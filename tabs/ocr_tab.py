"""
OCR Tab Module / Modul Tab OCR
===============================
Handles OCR tab interface and template/input/output selection.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os

from modern_styles import create_modern_frame, create_modern_button, create_modern_label


class OCRTab:
    """
    Manages the OCR Process tab interface and file selection functionality.
    Mengelola antarmuka tab Proses OCR dan fungsionalitas pemilihan file.
    """
    
    def __init__(self, parent_frame):
        """
        Initialize the OCR Tab.
        
        Args:
            parent_frame: Parent tkinter frame / Frame induk tkinter
        """
        self.parent_frame = parent_frame
        self.template_label = None
        self.templates_combobox = None
        self.input_mode_var = None
        self.input_folder_label = None
        self.input_folder_path = ""
        self.input_file_path = ""
        self.input_file_label = None
        self.output_folder_path = ""
        self.output_folder_label = None
        self.export_format_var = None
        self.log = None
        self.input_tree = None
        self.template_map = {}
        self.input_btn = None
        self.input_file_btn = None
        self.output_btn = None
        self.start_btn = None
        self.ocr_timer_label = None
        self.ocr_loading_label = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Setup the OCR tab UI components.
        Siapkan komponen UI tab OCR.
        """
        # Create header / Buat header
        header_frame = create_modern_frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        create_modern_label(header_frame, "🔍 OCR Processing", style='Modern.TLabel').pack()
        
        # Content area with left (controls) and right (preview) panels
        content_frame = tk.Frame(self.parent_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # ========================================
        # Left Panel: Controls / Panel Kiri: Kontrol
        # ========================================
        left_panel = create_modern_frame(content_frame, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # --- Template Selection Section ---
        template_row = create_modern_frame(left_panel, padding=5)
        template_row.pack(fill=tk.X, pady=(0, 8))
        
        create_modern_label(template_row, "📄 Template JSON:", style='Modern.TLabel').pack(side=tk.LEFT)
        
        # Label to show selected template / Label untuk menampilkan template yang dipilih
        self.template_label = create_modern_label(template_row, "Belum dipilih", style='Modern.TLabel')
        self.template_label.pack(side=tk.LEFT, padx=10)
        
        # Combobox for template selection / Combobox untuk pemilihan template
        self.templates_combobox = ttk.Combobox(template_row, state='readonly', width=30)
        self.templates_combobox.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Refresh button to update template list / Tombol refresh untuk memperbarui daftar template
        refresh_btn = create_modern_button(
            template_row,
            "🔄 Refresh",
            lambda: self.refresh_templates_ui(),
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
            lambda: None,  # Will be set by main GUI
            style='Secondary.TButton'
        )
        open_creator_btn.pack(side=tk.RIGHT, padx=(0, 10))
        self.open_creator_btn = open_creator_btn
        
        # --- Input Mode Selection Section ---
        mode_row = create_modern_frame(left_panel, padding=5)
        mode_row.pack(fill=tk.X, pady=(6, 6))
        create_modern_label(mode_row, "Mode Input:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.input_mode_var = tk.StringVar(value="folder")
        
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
        action_row = create_modern_frame(left_panel, padding=5)
        action_row.pack(fill=tk.X, pady=(10, 0))
        self.start_btn = create_modern_button(
            action_row, 
            "🚀 Mulai OCR", 
            lambda: None,  # Will be set by main GUI
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
    
    def pick_template(self):
        """
        Open file dialog to select existing template.
        Buka dialog file untuk memilih template yang ada.
        """
        template = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if template:
            self.template_label.config(text=os.path.basename(template), foreground="#10b981")
            if self.log:
                self.log.insert(tk.END, f"📁 Template dipilih: {template}\n")
                self.log.see(tk.END)
    
    def refresh_templates_ui(self):
        """
        Refresh the templates combobox UI.
        Segarkan UI combobox template.
        """
        pass  # Will be implemented by main GUI
    
    def pick_input_folder(self):
        """
        Open directory browser to select input folder.
        Buka browser direktori untuk memilih folder input.
        """
        folder_path = filedialog.askdirectory(title="Pilih Folder Input Gambar")
        if folder_path:
            self.input_folder_path = folder_path
            self.input_folder_label.config(
                text=os.path.basename(folder_path), 
                foreground="#10b981"
            )
            
            if self.log:
                self.log.insert(tk.END, f"📁 Folder input dipilih: {folder_path}\n")
                self.log.see(tk.END)
            
            # Display folder structure / Tampilkan struktur folder
            try:
                self.display_folder_structure(folder_path)
            except Exception as e:
                print(f"Gagal menampilkan struktur folder: {e}")
    
    def pick_input_file(self):
        """
        Open file browser to select single input file.
        Buka browser file untuk memilih file input tunggal.
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
            
            if self.log:
                self.log.insert(tk.END, f"📄 File input dipilih: {file_path}\n")
                self.log.see(tk.END)
    
    def pick_output_folder(self):
        """
        Open directory browser to select output folder.
        Buka browser direktori untuk memilih folder output.
        """
        folder_path = filedialog.askdirectory(title="Pilih Folder Output Hasil OCR")
        if folder_path:
            self.output_folder_path = folder_path
            self.output_folder_label.config(
                text=os.path.basename(folder_path), 
                foreground="#10b981"
            )
            
            if self.log:
                self.log.insert(tk.END, f"📁 Folder output dipilih: {folder_path}\n")
                self.log.see(tk.END)
    
    def clear_input_tree(self):
        """
        Clear all items from the input folder treeview.
        Hapus semua item dari treeview folder input.
        """
        try:
            for item in self.input_tree.get_children():
                self.input_tree.delete(item)
        except Exception:
            pass
    
    def display_folder_structure(self, folder_path):
        """
        Display folder structure in the treeview.
        Tampilkan struktur folder di treeview.
        
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
