import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import os
from PIL import Image, ImageTk
import json
import cv2
import pytesseract
from screenshot import ScreenshotMiniGUI
from modern_styles import apply_modern_styling, create_modern_frame, create_modern_button, create_modern_label, create_modern_notebook


class ModernTemplateGUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.image = None
        self.tk_image = None
        self.original_image = None
        self.rectangles = []
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.preview_text = None
        
        # Zoom and navigation variables
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.image_x = 0
        self.image_y = 0
        self.viewport_width = 600
        self.viewport_height = 400
        
        # Mini-map variables
        self.minimap_ratio = 0.15  # 15% of viewport
        self.minimap_canvas = None
        
        self.setup_ui()


    def setup_ui(self):
        # Main container with modern padding
        main_container = create_modern_frame(self.parent_frame, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top control panel with zoom controls
        control_panel = create_modern_frame(main_container, padding=10)
        control_panel.pack(fill=tk.X, pady=(0, 15))
        
        # Left controls: Open Image
        left_controls = create_modern_frame(control_panel, padding=0)
        left_controls.pack(side=tk.LEFT)
        
        create_modern_button(
            left_controls, 
            "📁 Open Image", 
            self.open_image, 
            style='Modern.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Center controls: Zoom controls
        center_controls = create_modern_frame(control_panel, padding=0)
        center_controls.pack(side=tk.LEFT, expand=True)
        
        # Zoom level label
        self.zoom_label = create_modern_label(
            center_controls, 
            "Zoom: 100%", 
            style='Modern.TLabel'
        )
        self.zoom_label.pack(side=tk.LEFT, padx=(20, 10))
        
        # Zoom controls
        create_modern_button(
            center_controls, 
            "🔍+", 
            lambda: self.zoom_in(), 
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_modern_button(
            center_controls, 
            "🔍-", 
            lambda: self.zoom_out(), 
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_modern_button(
            center_controls, 
            "📐 Fit", 
            lambda: self.fit_to_screen(), 
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Right controls: Action buttons
        right_controls = create_modern_frame(control_panel, padding=0)
        right_controls.pack(side=tk.RIGHT)
        
        create_modern_button(
            right_controls, 
            "👁️ Preview", 
            self.preview_extractions, 
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))

        create_modern_button(
            right_controls, 
            "💾 Save Template", 
            self.save_template, 
            style='Accent.TButton'
        ).pack(side=tk.LEFT)

        # Main content area: Paned window for image and fields
        self.paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, bg='white', sashrelief=tk.RAISED, sashwidth=2)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Left side: Image viewport with scrollbars
        self.viewport_frame = create_modern_frame(self.paned, padding=0)
        self.paned.add(self.viewport_frame, minsize=500)

        # Image canvas with scrollbars
        self.setup_image_viewport()

        # Right side: Fields panel with tabs
        self.fields_panel = create_modern_frame(self.paned, padding=15)
        self.paned.add(self.fields_panel, minsize=350)
        
        self.setup_fields_panel()


        # Status bar
        self.status_label = create_modern_label(
            main_container, 
            "Pilih 'Open Image' untuk memulai • Drag untuk memilih area • Scroll untuk zoom", 
            style='Modern.TLabel'
        )
        self.status_label.pack(side=tk.BOTTOM, pady=(10, 0))

        # Bind events
        self.bind_canvas_events()

    def bind_canvas_events(self):
        """Bind all canvas events"""
        # Mouse events for rectangle selection
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Mouse wheel for zoom
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        
        # Keyboard events
        self.canvas.bind("<KeyPress-plus>", lambda e: self.zoom_in())
        self.canvas.bind("<KeyPress-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<KeyPress-f>", lambda e: self.fit_to_screen())
        
        # Focus canvas to receive keyboard events
        self.canvas.focus_set()

    def on_mousewheel(self, event):
        """Handle mouse wheel for zoom"""
        if not self.image:
            return
            
        if event.delta > 0 or event.num == 4:  # Scroll up
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:  # Scroll down
            self.zoom_out()

    def setup_image_viewport(self):
        """Setup image viewport with scrollbars and mini-map"""
        # Main canvas frame
        canvas_frame = tk.Frame(self.viewport_frame, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        

        # Canvas with scrollbars - FIXED: Remove border interference
        self.canvas = tk.Canvas(
            canvas_frame,
            cursor="cross",
            bg="white",
            highlightthickness=0,  # Remove border to prevent interference
            highlightbackground="white"
        )
        
        # Configure canvas scrollregion immediately
        self.canvas.configure(scrollregion=(0, 0, 1000, 800))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Mini-map frame
        minimap_frame = create_modern_frame(self.viewport_frame, padding=5)
        minimap_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        create_modern_label(
            minimap_frame, 
            "🗺️ Mini-map", 
            style='Modern.TLabel'
        ).pack(anchor="w")
        
        self.minimap_canvas = tk.Canvas(
            minimap_frame,
            height=60,
            bg="white",
            highlightthickness=1,
            highlightbackground="#e2e8f0"
        )
        self.minimap_canvas.pack(fill=tk.X, pady=(5, 0))

    def setup_fields_panel(self):
        """Setup fields panel with tabs for extracted text and field information"""
        # Header
        header_frame = create_modern_frame(self.fields_panel, padding=0)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        create_modern_label(
            header_frame, 
            "📊 Template Fields", 
            style='Modern.TLabel'
        ).pack(anchor="w")
        
        # Tabbed interface for different views
        self.fields_notebook = create_modern_notebook(self.fields_panel)
        self.fields_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Field List (Table)
        self.setup_field_list_tab()
        
        # Tab 2: Extracted Text Preview
        self.setup_extracted_text_tab()
        
        # Tab 3: Field Statistics
        self.setup_field_stats_tab()

    def setup_field_list_tab(self):
        """Setup field list as table"""
        field_list_frame = create_modern_frame(self.fields_notebook, padding=10)
        self.fields_notebook.add(field_list_frame, text="📋 Fields List")
        
        # Field count label
        self.field_count_label = create_modern_label(
            field_list_frame, 
            "No fields selected", 
            style='Modern.TLabel'
        )
        self.field_count_label.pack(anchor="w", pady=(0, 10))
        
        # Treeview for field information
        tree_frame = tk.Frame(field_list_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbars
        columns = ("Name", "X", "Y", "W", "H")
        self.fields_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.fields_tree.heading("Name", text="Field Name")
        self.fields_tree.heading("X", text="X")
        self.fields_tree.heading("Y", text="Y")
        self.fields_tree.heading("W", text="Width")
        self.fields_tree.heading("H", text="Height")
        
        # Column widths
        self.fields_tree.column("Name", width=80)
        self.fields_tree.column("X", width=40)
        self.fields_tree.column("Y", width=40)
        self.fields_tree.column("W", width=50)
        self.fields_tree.column("H", width=50)
        
        # Scrollbars for treeview
        tree_v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.fields_tree.yview)
        tree_h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.fields_tree.xview)
        self.fields_tree.configure(yscrollcommand=tree_v_scroll.set, xscrollcommand=tree_h_scroll.set)
        
        # Grid layout
        self.fields_tree.grid(row=0, column=0, sticky="nsew")
        tree_v_scroll.grid(row=0, column=1, sticky="ns")
        tree_h_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.fields_tree.bind("<<TreeviewSelect>>", self.on_field_select)

    def setup_extracted_text_tab(self):
        """Setup extracted text preview tab"""
        text_frame = create_modern_frame(self.fields_notebook, padding=10)
        self.fields_notebook.add(text_frame, text="👁️ Extracted Text")
        
        # Create text widget with scrollbar
        text_widget_frame = tk.Frame(text_frame, bg='white')
        text_widget_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            text_widget_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b',
            insertbackground='#2563eb',
            selectbackground='#2563eb',
            selectforeground='white',
            relief='solid',
            borderwidth=1
        )
        
        text_scrollbar = ttk.Scrollbar(text_widget_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=text_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_field_stats_tab(self):
        """Setup field statistics tab"""
        stats_frame = create_modern_frame(self.fields_notebook, padding=10)
        self.fields_notebook.add(stats_frame, text="📈 Statistics")
        
        # Statistics content
        self.stats_text = tk.Text(
            stats_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b',
            relief='solid',
            borderwidth=1
        )
        
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initialize stats display
        self.update_field_stats()


    def update_status(self, message, color="#64748b"):
        """Update status with modern styling"""
        self.status_label.config(text=message, foreground=color)

    def zoom_in(self):
        """Zoom in the image"""
        if self.image:
            self.zoom_factor = min(self.zoom_factor * 1.2, self.max_zoom)
            self.update_zoom_display()
            self.redraw_image()
            self.update_minimap()

    def zoom_out(self):
        """Zoom out the image"""
        if self.image:
            self.zoom_factor = max(self.zoom_factor / 1.2, self.min_zoom)
            self.update_zoom_display()
            self.redraw_image()
            self.update_minimap()

    def fit_to_screen(self):
        """Fit image to screen"""
        if self.image and self.canvas:
            # Calculate fit zoom based on canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                zoom_x = (canvas_width - 40) / self.image.width  # -40 for padding
                zoom_y = (canvas_height - 40) / self.image.height  # -40 for padding
                self.zoom_factor = min(zoom_x, zoom_y, 1.0)  # Don't zoom in beyond 1.0
                
                self.update_zoom_display()
                self.redraw_image()
                self.update_minimap()

    def update_zoom_display(self):
        """Update zoom level display"""
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"Zoom: {zoom_percent}%")


    def redraw_image(self):
        """Redraw image with current zoom level"""
        if not self.image:
            return
            
        self.canvas.delete("all")
        
        # Calculate new size based on zoom
        new_width = int(self.image.width * self.zoom_factor)
        new_height = int(self.image.height * self.zoom_factor)
        
        # Resize image for display
        display_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # CRITICAL: Store PhotoImage as instance variable to prevent garbage collection
        self.tk_image = ImageTk.PhotoImage(display_image)
        
        # Force canvas to update before getting dimensions
        self.canvas.update_idletasks()
        
        # Calculate position to center image with robust fallback
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = self.viewport_frame.winfo_width()
                canvas_height = self.viewport_frame.winfo_height()
                
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
                
        except Exception as e:
            print(f"Warning: Could not get canvas dimensions in redraw: {e}")
            canvas_width, canvas_height = 800, 600
            
        x = max(0, (canvas_width - new_width) // 2)
        y = max(0, (canvas_height - new_height) // 2)
        
        # Draw image with proper anchoring and tags
        image_id = self.canvas.create_image(x, y, anchor="nw", image=self.tk_image, tags="main_image")
        
        # Redraw rectangles
        self.redraw_rectangles()
        
        # Update scroll region to include entire image
        padding = 20
        scroll_width = max(canvas_width, new_width + 2 * padding)
        scroll_height = max(canvas_height, new_height + 2 * padding)
        self.canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

    def redraw_rectangles(self):
        """Redraw all rectangles with current zoom"""
        if not self.rectangles:
            return
            
        for rect in self.rectangles:
            x = int(rect["x"] * self.zoom_factor)
            y = int(rect["y"] * self.zoom_factor)
            w = int(rect["w"] * self.zoom_factor)
            h = int(rect["h"] * self.zoom_factor)
            
            self.canvas.create_rectangle(
                x, y, x + w, y + h,
                outline="#2563eb", width=2, tags="field_rect"
            )

    def update_minimap(self):
        """Update mini-map display"""
        if not self.minimap_canvas or not self.image:
            return
            
        # Clear minimap
        self.minimap_canvas.delete("all")
        
        # Calculate minimap size
        minimap_width = self.minimap_canvas.winfo_width()
        minimap_height = self.minimap_canvas.winfo_height()
        
        if minimap_width <= 1 or minimap_height <= 1:
            return
            
        # Calculate scaling factor for minimap
        scale_x = minimap_width / self.image.width
        scale_y = minimap_height / self.image.height
        minimap_scale = min(scale_x, scale_y)
        
        # Draw scaled image outline
        scaled_width = int(self.image.width * minimap_scale)
        scaled_height = int(self.image.height * minimap_scale)
        
        x = (minimap_width - scaled_width) // 2
        y = (minimap_height - scaled_height) // 2
        
        # Draw image border
        self.minimap_canvas.create_rectangle(
            x, y, x + scaled_width, y + scaled_height,
            outline="#2563eb", width=2, tags="minimap_border"
        )
        
        # Draw rectangles
        for rect in self.rectangles:
            mx = x + int(rect["x"] * minimap_scale)
            my = y + int(rect["y"] * minimap_scale)
            mw = int(rect["w"] * minimap_scale)
            mh = int(rect["h"] * minimap_scale)
            
            self.minimap_canvas.create_rectangle(
                mx, my, mx + mw, my + mh,
                outline="#ef4444", width=1, tags="minimap_rect"
            )

    def on_field_select(self, event):
        """Handle field selection from tree"""
        selection = self.fields_tree.selection()
        if selection:
            item = self.fields_tree.item(selection[0])
            field_name = item['values'][0]
            
            # Find and highlight the corresponding rectangle
            for i, rect in enumerate(self.rectangles):
                if rect["name"] == field_name:
                    # Remove previous highlights
                    self.canvas.delete("highlight")
                    
                    # Draw highlight
                    x = int(rect["x"] * self.zoom_factor)
                    y = int(rect["y"] * self.zoom_factor)
                    w = int(rect["w"] * self.zoom_factor)
                    h = int(rect["h"] * self.zoom_factor)
                    
                    self.canvas.create_rectangle(
                        x, y, x + w, y + h,
                        outline="#fbbf24", width=4, tags="highlight"
                    )
                    break

    def update_field_list(self):
        """Update field list in tree view"""
        # Clear existing items
        for item in self.fields_tree.get_children():
            self.fields_tree.delete(item)
            
        # Add fields
        for rect in self.rectangles:
            self.fields_tree.insert("", tk.END, values=(
                rect["name"],
                rect["x"],
                rect["y"],
                rect["w"],
                rect["h"]
            ))
            
        # Update field count
        count = len(self.rectangles)
        if count == 0:
            self.field_count_label.config(text="No fields selected")
        elif count == 1:
            self.field_count_label.config(text="1 field selected")
        else:
            self.field_count_label.config(text=f"{count} fields selected")

    def update_field_stats(self):
        """Update field statistics display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        if not self.rectangles:
            self.stats_text.insert(tk.END, "No fields selected yet.\n\nSelect areas on the image to see statistics.")
        else:
            stats = []
            stats.append(f"📊 FIELD STATISTICS")
            stats.append("=" * 30)
            stats.append(f"Total Fields: {len(self.rectangles)}")
            stats.append("")
            
            # Calculate bounds
            all_x = [r["x"] for r in self.rectangles]
            all_y = [r["y"] for r in self.rectangles]
            all_w = [r["w"] for r in self.rectangles]
            all_h = [r["h"] for r in self.rectangles]
            
            stats.append(f"Bounds:")
            stats.append(f"  X range: {min(all_x)} - {max(all_x)}")
            stats.append(f"  Y range: {min(all_y)} - {max(all_y)}")
            stats.append("")
            
            stats.append(f"Size Statistics:")
            stats.append(f"  Avg width: {sum(all_w)/len(all_w):.1f}")
            stats.append(f"  Avg height: {sum(all_h)/len(all_h):.1f}")
            stats.append(f"  Total area: {sum(w*h for w,h in zip(all_w, all_h))}")
            
        self.stats_text.config(state=tk.DISABLED)



    def open_image(self):
        """Open and display an image with proper error handling and scaling"""
        path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png;*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg")
        ])
        
        if not path:
            return

        try:
            # Load image
            self.original_image = Image.open(path)
            
            # Keep original size for zoom functionality
            self.image = self.original_image.copy()
            
            # Reset zoom and position
            self.zoom_factor = 1.0
            self.image_x = 0
            self.image_y = 0
            
            # Clear previous rectangles
            self.rectangles = []
            
            # CRITICAL: Store PhotoImage as instance variable to prevent garbage collection
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            # Force canvas to update before getting dimensions
            self.canvas.update_idletasks()
            
            # Get canvas dimensions with multiple fallback strategies
            try:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # If canvas still has no size, try to get frame size
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = self.viewport_frame.winfo_width()
                    canvas_height = self.viewport_frame.winfo_height()
                    
                # Final fallback to reasonable defaults
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width, canvas_height = 800, 600
                    
            except Exception as e:
                print(f"Warning: Could not get canvas dimensions: {e}")
                canvas_width, canvas_height = 800, 600
            
            print(f"Canvas size: {canvas_width}x{canvas_height}")
            print(f"Image size: {self.image.width}x{self.image.height}")
            
            # Update display
            self.update_zoom_display()
            self.redraw_image()
            self.update_minimap()
            self.update_field_list()
            self.update_field_stats()
            
            # Clear preview text
            if self.preview_text:
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "Pilih area dengan drag mouse untuk ekstraksi teks...\n\n💡 Tips:\n• Drag mouse untuk memilih area\n• Area minimum 5x5 pixels\n• Gunakan Preview untuk melihat hasil OCR\n• Scroll untuk zoom in/out\n• Pilih field dari tabel untuk highlight")
                self.preview_text.config(state=tk.DISABLED)
                
            self.update_status(f"✅ Image loaded: {self.image.width}x{self.image.height} • Zoom: 100%", "#10b981")
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}\n\nTips:\n• Pastikan file gambar tidak corrupt\n• Format yang didukung: PNG, JPG, JPEG"
            messagebox.showerror("❌ Error", error_msg)
            print(f"Error loading image: {e}")
            # Reset image references on error
            self.image = None
            self.tk_image = None


    def on_mouse_down(self, event):
        """Handle mouse press for rectangle selection"""
        if not self.image:
            messagebox.showwarning("⚠️ Warning", "Buka gambar terlebih dahulu!")
            return
            
        # Convert screen coordinates to image coordinates
        image_x = event.x / self.zoom_factor
        image_y = event.y / self.zoom_factor
        
        self.start_x = image_x
        self.start_y = image_y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x * self.zoom_factor, 
            self.start_y * self.zoom_factor, 
            self.start_x * self.zoom_factor, 
            self.start_y * self.zoom_factor, 
            outline="#2563eb", 
            width=3, 
            tags="selection_rect"
        )

    def on_mouse_drag(self, event):
        """Handle mouse drag for rectangle selection"""
        if self.current_rect:
            # Convert screen coordinates to image coordinates
            image_x = event.x / self.zoom_factor
            image_y = event.y / self.zoom_factor
            
            self.canvas.coords(
                self.current_rect, 
                self.start_x * self.zoom_factor, 
                self.start_y * self.zoom_factor, 
                image_x * self.zoom_factor, 
                image_y * self.zoom_factor
            )

    def on_mouse_up(self, event):
        """Handle mouse release for rectangle selection"""
        if self.current_rect:
            # Convert screen coordinates to image coordinates
            image_x = event.x / self.zoom_factor
            image_y = event.y / self.zoom_factor
            
            x, y = min(self.start_x, image_x), min(self.start_y, image_y)
            w, h = abs(image_x - self.start_x), abs(image_y - self.start_y)

            # Remove the selection rectangle
            self.canvas.delete(self.current_rect)
            self.current_rect = None

            if w > 5 and h > 5:  # Only save if rectangle is large enough
                field_name = f"field_{len(self.rectangles)+1}"
                self.rectangles.append({
                    "name": field_name,
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h)
                })
                print("Added rectangle:", self.rectangles[-1])
                
                # Update displays
                self.redraw_rectangles()
                self.update_field_list()
                self.update_field_stats()
                self.update_minimap()
                
                self.update_status(f"✅ Added {field_name}: x={x}, y={y}, w={w}, h={h}", "#10b981")
            else:
                self.update_status("❌ Rectangle too small, deleted", "#ef4444")

    def save_template(self):
        if not self.rectangles:
            messagebox.showwarning("⚠️ Warning", "No areas selected.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not save_path:
            return

        try:
            with open(save_path, "w") as f:
                json.dump({"fields": self.rectangles}, f, indent=4)

            messagebox.showinfo("✅ Success", f"Template saved to: {save_path}")
            # Notify parent about new template
            if hasattr(self.parent_frame, 'on_template_created'):
                self.parent_frame.on_template_created(save_path)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to save template: {str(e)}")


    def preview_extractions(self):
        """Preview OCR extractions from selected areas"""
        if not self.image:
            messagebox.showwarning("⚠️ Warning", "Open an image first!")
            return

        if not self.rectangles:
            messagebox.showwarning("⚠️ Warning", "Select at least one area first!")
            return

        try:
            # Convert PIL image to OpenCV format
            if self.original_image:
                cv_image = cv2.cvtColor(cv2.imread(self.original_image.filename), cv2.COLOR_RGB2BGR)
            else:
                messagebox.showerror("❌ Error", "No original image file available")
                return

            # Switch to extracted text tab
            self.fields_notebook.select(self.fields_notebook.tabs()[1])  # Index 1 is extracted text tab

            # Clear previous preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "📋 EXTRACTION PREVIEW\n")
            self.preview_text.insert(tk.END, "=" * 50 + "\n\n")

            extracted_count = 0
            for i, field in enumerate(self.rectangles):
                x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                crop = cv_image[y:y+h, x:x+w]
                text = pytesseract.image_to_string(crop, lang="eng+ind").strip()
                
                # Modern preview with better formatting
                self.preview_text.insert(tk.END, f"🔹 {field['name'].upper()}\n")
                self.preview_text.insert(tk.END, f"   Position: ({x}, {y}) Size: {w}x{h}\n")
                
                if text:
                    self.preview_text.insert(tk.END, f"   Text: {text}\n")
                    extracted_count += 1
                else:
                    self.preview_text.insert(tk.END, "   Text: [No text detected]\n")
                    
                self.preview_text.insert(tk.END, "\n")

            # Add summary
            self.preview_text.insert(tk.END, f"📊 SUMMARY:\n")
            self.preview_text.insert(tk.END, f"   Total fields: {len(self.rectangles)}\n")
            self.preview_text.insert(tk.END, f"   Text extracted: {extracted_count}\n")
            self.preview_text.insert(tk.END, f"   Success rate: {(extracted_count/len(self.rectangles)*100):.1f}%\n")

            self.preview_text.config(state=tk.DISABLED)
            self.update_status("👁️ Extraction preview generated!", "#10b981")
            messagebox.showinfo("✅ Preview", f"Extraction preview generated!\n{extracted_count}/{len(self.rectangles)} fields extracted successfully.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to preview extractions: {str(e)}")

class ModernOCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Modern OCR GUI - Screenshot + Template Creator + Docker")
        self.root.geometry("1200x800")
        
        # Apply modern styling
        self.modern_styles = apply_modern_styling(root)
        
        self.template = ""
        self.image_folder = "screenshots"
        self.current_template_path = ""

        os.makedirs(self.image_folder, exist_ok=True)

        # Create modern notebook for tabs
        self.notebook = create_modern_notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Tab 1: Screenshot
        self.screenshot_frame = create_modern_frame(self.notebook)
        self.notebook.add(self.screenshot_frame, text="📸 Screenshot")
        self.setup_screenshot_tab()

        # Tab 2: Template Creator
        self.template_frame = create_modern_frame(self.notebook)
        self.notebook.add(self.template_frame, text="📐 Template Creator")
        self.setup_template_tab()

        # Tab 3: OCR Process
        self.ocr_frame = create_modern_frame(self.notebook)
        self.notebook.add(self.ocr_frame, text="🔍 OCR Process")
        self.setup_ocr_tab()

    def setup_screenshot_tab(self):
        # Header
        header_frame = create_modern_frame(self.screenshot_frame)
        header_frame.pack(fill=tk.X, pady=(20, 20))
        
        create_modern_label(
            header_frame, 
            "📸 Screenshot Tools", 
            style='Modern.TLabel'
        ).pack()
        
        # Folder selection section
        folder_section = create_modern_frame(self.screenshot_frame, padding=20)
        folder_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Folder selection row
        folder_row = create_modern_frame(folder_section, padding=0)
        folder_row.pack(fill=tk.X, pady=(0, 10))
        
        create_modern_label(
            folder_row, 
            "📁 Output Folder:", 
            style='Modern.TLabel'
        ).pack(side=tk.LEFT)
        
        # Folder path entry
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
        
        create_modern_button(
            folder_row, 
            "📂 Browse", 
            self.browse_output_folder, 
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT)

        # Main screenshot section
        screenshot_section = create_modern_frame(self.screenshot_frame, padding=20)
        screenshot_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Screenshot button with modern styling
        create_modern_button(
            screenshot_section, 
            "🎯 Take Screenshot", 
            self.open_screenshot, 
            style='Modern.TButton'
        ).pack(pady=20)

        # Modern log area
        log_frame = create_modern_frame(screenshot_section, padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        create_modern_label(
            log_frame, 
            "📝 Screenshot Log", 
            style='Modern.TLabel'
        ).pack(anchor="w", pady=(0, 10))
        
        # Modern scrolled text
        text_frame = tk.Frame(log_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.screenshot_log = scrolledtext.ScrolledText(
            text_frame, 
            width=50, 
            height=15,
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b',
            insertbackground='#2563eb',
            selectbackground='#2563eb',
            selectforeground='white',
            relief='solid',
            borderwidth=1
        )
        
        self.screenshot_log.pack(fill=tk.BOTH, expand=True)

    def browse_output_folder(self):
        """Browse and select output folder for screenshots"""
        folder_path = filedialog.askdirectory(
            title="Pilih Folder Output Screenshot",
            initialdir=self.image_folder
        )
        
        if folder_path:
            # Validate folder path
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.image_folder = folder_path
                self.folder_var.set(folder_path)
                self.screenshot_log.insert(tk.END, f"📁 Folder output diubah ke: {folder_path}\n")
                self.screenshot_log.see(tk.END)
            except Exception as e:
                messagebox.showerror("❌ Error", f"Gagal mengakses folder: {str(e)}")

    def setup_template_tab(self):
        # Header
        header_frame = create_modern_frame(self.template_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        create_modern_label(
            header_frame, 
            "📐 Template Creator", 
            style='Modern.TLabel'
        ).pack()

        # Template GUI
        self.template_gui = ModernTemplateGUI(self.template_frame)

    def setup_ocr_tab(self):
        # Header
        header_frame = create_modern_frame(self.ocr_frame)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        create_modern_label(
            header_frame, 
            "🔍 OCR Processing", 
            style='Modern.TLabel'
        ).pack()

        # Template selection section
        template_section = create_modern_frame(self.ocr_frame, padding=20)
        template_section.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Template selection row
        template_row = create_modern_frame(template_section, padding=0)
        template_row.pack(fill=tk.X, pady=(0, 10))
        
        create_modern_label(
            template_row, 
            "📄 Template JSON:", 
            style='Modern.TLabel'
        ).pack(side=tk.LEFT)
        
        self.template_label = create_modern_label(
            template_row, 
            "Belum dipilih", 
            style='Modern.TLabel'
        )
        self.template_label.pack(side=tk.LEFT, padx=15)
        
        create_modern_button(
            template_row, 
            "📁 Pilih Template", 
            self.pick_template, 
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT)

        # Action buttons section
        action_section = create_modern_frame(self.ocr_frame, padding=20)
        action_section.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        create_modern_button(
            action_section, 
            "🚀 Mulai OCR", 
            self.run_ocr, 
            style='Accent.TButton'
        ).pack(pady=10)

        # Log section
        log_section = create_modern_frame(self.ocr_frame, padding=20)
        log_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        create_modern_label(
            log_section, 
            "📊 Process Log:", 
            style='Modern.TLabel'
        ).pack(anchor="w", pady=(0, 10))
        
        # Modern log widget
        log_frame = tk.Frame(log_section, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log = scrolledtext.ScrolledText(
            log_frame, 
            width=60, 
            height=10,
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b',
            insertbackground='#2563eb',
            selectbackground='#2563eb',
            selectforeground='white',
            relief='solid',
            borderwidth=1
        )
        
        self.log.pack(fill=tk.BOTH, expand=True)


    def open_screenshot(self):
        win = tk.Toplevel(self.root)
        ScreenshotMiniGUI(win, callback=self.after_screenshot, save_dir=self.image_folder)

    def after_screenshot(self, path):
        """Handle screenshot completion with custom folder path"""
        try:
            # Ensure the output folder exists
            os.makedirs(self.image_folder, exist_ok=True)
            
            # Update screenshot log
            self.screenshot_log.insert(tk.END, f"✅ Screenshot tersimpan: {path}\n")
            self.screenshot_log.insert(tk.END, f"📁 Output folder: {self.image_folder}\n")
            self.screenshot_log.see(tk.END)
            
            # Also update main log if available
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"✅ Screenshot baru: {os.path.basename(path)}\n")
                self.log.see(tk.END)
                
        except Exception as e:
            error_msg = f"Gagal memproses screenshot: {str(e)}"
            messagebox.showerror("❌ Error", error_msg)
            print(f"Screenshot processing error: {e}")

    def on_template_created(self, template_path):
        """Callback when a new template is created"""
        self.current_template_path = template_path
        self.template_label.config(text=os.path.basename(template_path), foreground="#10b981")
        if hasattr(self, 'log'):
            self.log.insert(tk.END, f"✅ Template baru dibuat: {template_path}\n")
            self.log.see(tk.END)
        
        # Switch to OCR tab
        self.notebook.select(self.ocr_frame)

    def pick_template(self):
        self.template = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if self.template:
            self.current_template_path = self.template
            self.template_label.config(text=os.path.basename(self.template), foreground="#10b981")
            if hasattr(self, 'log'):
                self.log.insert(tk.END, f"📁 Template dipilih: {self.template}\n")
                self.log.see(tk.END)

    def run_ocr(self):
        if not self.current_template_path:
            messagebox.showerror("❌ Error", "Template belum dipilih. Buat template di tab Template Creator atau pilih template existing.")
            return

        try:
            # Get the directory of the template file
            template_dir = os.path.dirname(self.current_template_path)
            
            # Ensure output folder exists
            os.makedirs(self.image_folder, exist_ok=True)

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{template_dir}:/data",
                "ocr-app",
                "/data/" + os.path.basename(self.current_template_path),
                "/data/" + os.path.relpath(self.image_folder, template_dir)
            ]

            if hasattr(self, 'log'):
                self.log.insert(tk.END, "🚀 Menjalankan OCR di Docker...\n")
                self.log.insert(tk.END, f"📁 Template: {os.path.basename(self.current_template_path)}\n")
                self.log.insert(tk.END, f"📁 Output folder: {self.image_folder}\n")
                self.log.see(tk.END)
            
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if hasattr(self, 'log'):
                    self.log.insert(tk.END, "✅ Selesai! Hasil OCR tersimpan di hasil_ocr.csv\n")
                    self.log.see(tk.END)
                messagebox.showinfo("✅ Selesai", "OCR selesai!")
            else:
                if hasattr(self, 'log'):
                    self.log.insert(tk.END, f"❌ Error: {result.stderr}\n")
                    self.log.see(tk.END)
                messagebox.showerror("❌ Error", f"OCR gagal: {result.stderr}")
                
        except FileNotFoundError:
            messagebox.showerror("❌ Error", "Docker tidak ditemukan. Pastikan Docker sudah terinstall dan running.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernOCRGui(root)
    root.mainloop()
