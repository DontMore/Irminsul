"""
Template Creator GUI Module

This module provides the Template Creator interface for creating and managing
OCR templates. Users can load images, select regions of interest (fields),
and save them as JSON templates for OCR processing.

Features:
- Image loading and display with zoom/pan capabilities
- Rectangle selection for defining extraction regions
- Template save/load functionality
- Enhanced OCR preview with confidence scores
- Field management (edit, delete, statistics)
- Mini-map navigation for large images
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # Pillow for image handling
import json  # JSON for template file format
import os
import time
import shutil
import cv2  # OpenCV for image processing
from modern_styles import create_modern_frame, create_modern_button, create_modern_label, create_modern_notebook
from enhanced_ocr import EnhancedOCR


class ModernTemplateGUI:
    """
    Template Creator GUI Class
    
    Provides a complete interface for creating OCR templates.
    Users can load images, select rectangular regions (fields),
    and save them as templates for later OCR extraction.
    
    Attributes:
        parent_frame: Parent tkinter frame to embed this GUI
        image: PIL Image object for current loaded image
        rectangles: List of dicts containing field selections
        zoom_factor: Current zoom level (1.0 = 100%)
        fields_tree: Treeview widget showing selected fields
    """
    
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

        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.viewport_width = 600
        self.viewport_height = 400

        self.minimap_canvas = None

        self.setup_ui()

    # ==========================================================================
    # UI SETUP METHODS
    # ==========================================================================

    def setup_ui(self):
        """
        Initialize and layout the main UI components.
        
        Creates the complete Template Creator interface including:
        - Control panel with buttons for file operations and zoom
        - Content frame with image viewport and fields panel
        - Status bar with usage instructions
        """

        main_container = create_modern_frame(self.parent_frame, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        control_panel = create_modern_frame(main_container, padding=10)
        control_panel.pack(fill=tk.X, pady=(0, 15))

        left_controls = create_modern_frame(control_panel, padding=0)
        left_controls.pack(side=tk.LEFT)

        create_modern_button(left_controls, "📁 Open Image", self.open_image, style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        create_modern_button(left_controls, "📂 Open Template", self.open_template_file, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))

        center_controls = create_modern_frame(control_panel, padding=0)
        center_controls.pack(side=tk.LEFT, expand=True)

        self.zoom_label = create_modern_label(center_controls, "Zoom: 100%", style='Modern.TLabel')
        self.zoom_label.pack(side=tk.LEFT, padx=(20, 10))

        create_modern_button(center_controls, "🔍+", lambda: self.zoom_in(), style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        create_modern_button(center_controls, "🔍-", lambda: self.zoom_out(), style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        create_modern_button(center_controls, "📐 Fit", lambda: self.fit_to_screen(), style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))

        right_controls = create_modern_frame(control_panel, padding=0)
        right_controls.pack(side=tk.RIGHT)

        create_modern_button(right_controls, "⛶ Full Screen", self.toggle_fullscreen, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        create_modern_button(right_controls, "👁️ Preview", self.preview_extractions, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        create_modern_button(right_controls, "💾 Save Template", self.save_template, style='Accent.TButton').pack(side=tk.LEFT)

        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        content_frame.grid_columnconfigure(0, weight=8)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        self.viewport_frame = create_modern_frame(content_frame, padding=0)
        self.viewport_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.fields_panel = create_modern_frame(content_frame, padding=8)
        self.fields_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.setup_image_viewport()
        self.setup_fields_panel()

        self.status_label = create_modern_label(main_container, "Pilih 'Open Image' untuk memulai • Drag untuk memilih area • Scroll untuk zoom", style='Modern.TLabel')
        self.status_label.pack(side=tk.BOTTOM, pady=(10, 0))

        self.bind_canvas_events()

    # ==========================================================================
    # EVENT BINDINGS AND INTERACTION METHODS
    # ==========================================================================

    def bind_canvas_events(self):
        """
        Bind all mouse and keyboard events to the canvas for interaction.
        
        Events handled:
        - Left click and drag: Rectangle selection
        - Mouse wheel: Zoom in/out
        - Keyboard +/-/f: Zoom controls
        - Escape: Exit fullscreen mode
        """
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<KeyPress-plus>", lambda e: self.zoom_in())
        self.canvas.bind("<KeyPress-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<KeyPress-f>", lambda e: self.fit_to_screen())
        self.parent_frame.winfo_toplevel().bind("<Escape>", lambda e: self.exit_fullscreen())
        self.canvas.focus_set()

    def on_mousewheel(self, event):
        """
        Handle mouse wheel scrolling for zoom control.
        
        Args:
            event: Tkinter mouse wheel event with delta attribute
        """
        if not self.image:
            return
        if getattr(event, 'delta', 0) > 0 or getattr(event, 'num', None) == 4:
            self.zoom_in()
        elif getattr(event, 'delta', 0) < 0 or getattr(event, 'num', None) == 5:
            self.zoom_out()

    # ==========================================================================
    # UI SETUP HELPER METHODS
    # ==========================================================================

    def setup_image_viewport(self):
        """
        Create the image display area with canvas and scrollbars.
        
        Components:
        - Canvas: Main drawing area for images and rectangles
        - Scrollbars: Vertical and horizontal scrolling
        - Mini-map: Navigation aid for large images
        """
        canvas_frame = tk.Frame(self.viewport_frame, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, cursor="cross", bg="white", highlightthickness=0, highlightbackground="white")
        self.canvas.configure(scrollregion=(0, 0, 1000, 800))

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        minimap_frame = create_modern_frame(self.viewport_frame, padding=5)
        minimap_frame.pack(fill=tk.X, side=tk.BOTTOM)
        create_modern_label(minimap_frame, "🗺️ Mini-map", style='Modern.TLabel').pack(anchor="w")
        self.minimap_canvas = tk.Canvas(minimap_frame, height=60, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        self.minimap_canvas.pack(fill=tk.X, pady=(5, 0))

    def setup_fields_panel(self):
        """
        Create the right-side panel for field management.
        
        This panel contains a notebook with three tabs:
        - Fields List: Table showing all selected field regions
        - Extracted Text: Preview of OCR results
        - Statistics: Summary statistics for all fields
        """
        header_frame = create_modern_frame(self.fields_panel, padding=0)
        header_frame.pack(fill=tk.X, pady=(0, 6))
        create_modern_label(header_frame, "📊 Fields", style='Modern.TLabel').pack(anchor="w")
        self.fields_notebook = create_modern_notebook(self.fields_panel)
        self.fields_notebook.pack(fill=tk.BOTH, expand=True)
        self.setup_field_list_tab()
        self.setup_extracted_text_tab()
        self.setup_field_stats_tab()

    def setup_field_list_tab(self):
        """
        Create the 'Fields List' tab with a treeview table.
        
        Displays all selected fields with their coordinates.
        Supports selection, context menu, and double-click editing.
        """
        field_list_frame = create_modern_frame(self.fields_notebook, padding=5)
        self.fields_notebook.add(field_list_frame, text="📋 Fields")
        self.field_count_label = create_modern_label(field_list_frame, "No fields selected", style='Modern.TLabel')
        self.field_count_label.pack(anchor="w", pady=(0, 5))

        tree_frame = tk.Frame(field_list_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Name", "X", "Y", "W", "H")
        self.fields_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        for col, text, width in [("Name", "Name", 60), ("X", "X", 25), ("Y", "Y", 25), ("W", "W", 35), ("H", "H", 35)]:
            self.fields_tree.heading(col, text=text)
            self.fields_tree.column(col, width=width)

        tree_v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.fields_tree.yview)
        tree_h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.fields_tree.xview)
        self.fields_tree.configure(yscrollcommand=tree_v_scroll.set, xscrollcommand=tree_h_scroll.set)
        self.fields_tree.grid(row=0, column=0, sticky="nsew")
        tree_v_scroll.grid(row=0, column=1, sticky="ns")
        tree_h_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.fields_tree.bind("<<TreeviewSelect>>", self.on_field_select)
        self.fields_tree.bind("<Button-3>", self.show_context_menu)
        self.fields_tree.bind("<Double-1>", self.edit_field_name)

    def setup_extracted_text_tab(self):
        """
        Create the 'Extracted Text' tab for OCR preview.
        
        Displays OCR results for each selected field with
        confidence scores and extracted text content.
        """
        text_frame = create_modern_frame(self.fields_notebook, padding=5)
        self.fields_notebook.add(text_frame, text="👁️ Text")
        text_widget_frame = tk.Frame(text_frame, bg='white')
        text_widget_frame.pack(fill=tk.BOTH, expand=True)
        self.preview_text = tk.Text(text_widget_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9), bg='#f8fafc', fg='#1e293b')
        text_scrollbar = ttk.Scrollbar(text_widget_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=text_scrollbar.set)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_field_stats_tab(self):
        """
        Create the 'Statistics' tab showing field metrics.
        
        Displays:
        - Total number of fields
        - Position bounds (X and Y ranges)
        - Size statistics (average width/height)
        - Total area coverage
        """
        stats_frame = create_modern_frame(self.fields_notebook, padding=5)
        self.fields_notebook.add(stats_frame, text="📈 Stats")
        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9), bg='#f8fafc', fg='#1e293b')
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_field_stats()

    # ==========================================================================
    # STATUS AND HELPER METHODS
    # ==========================================================================

    def update_status(self, message, color="#64748b"):
        """
        Update the status bar message.
        
        Args:
            message: Text to display in the status bar
            color: Hex color code for the message text (default: #64748b)
        """
        self.status_label.config(text=message, foreground=color)

    def toggle_fullscreen(self):
        """
        Toggle fullscreen mode for the application window.
        """
        root = self.parent_frame.winfo_toplevel()
        is_fullscreen = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not is_fullscreen)

    def exit_fullscreen(self):
        """
        Exit fullscreen mode and return to normal windowed view.
        """
        root = self.parent_frame.winfo_toplevel()
        root.attributes("-fullscreen", False)

    # ==========================================================================
    # ZOOM AND IMAGE DISPLAY METHODS
    # ==========================================================================

    def zoom_in(self):
        """Increase zoom level by 20%, up to max_zoom limit."""
        if self.image:
            self.zoom_factor = min(self.zoom_factor * 1.2, self.max_zoom)
            self.update_zoom_display(); self.redraw_image(); self.update_minimap()

    def zoom_out(self):
        """Decrease zoom level by 20%, down to min_zoom limit."""
        if self.image:
            self.zoom_factor = max(self.zoom_factor / 1.2, self.min_zoom)
            self.update_zoom_display(); self.redraw_image(); self.update_minimap()

    def fit_to_screen(self):
        """Automatically adjust zoom to fit the entire image on screen."""
        if self.image and self.canvas:
            canvas_width = self.canvas.winfo_width(); canvas_height = self.canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                zoom_x = (canvas_width - 40) / self.image.width
                zoom_y = (canvas_height - 40) / self.image.height
                self.zoom_factor = min(zoom_x, zoom_y, 1.0)
                self.update_zoom_display(); self.redraw_image(); self.update_minimap()

    def update_zoom_display(self):
        """Update the zoom percentage label in the control panel."""
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"Zoom: {zoom_percent}%")

    def redraw_image(self):
        """
        Redraw the current image on the canvas with current zoom level.
        
        Handles:
        - Image resizing based on zoom factor
        - Centering the image on canvas
        - Setting up scroll region for large images
        - Drawing field rectangles on top
        """
        if not self.image:
            return
        self.canvas.delete("all")
        new_width = int(self.image.width * self.zoom_factor)
        new_height = int(self.image.height * self.zoom_factor)
        display_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(display_image)
        self.canvas.update_idletasks()
        try:
            canvas_width = self.canvas.winfo_width(); canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = self.viewport_frame.winfo_width(); canvas_height = self.viewport_frame.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
        except Exception:
            canvas_width, canvas_height = 800, 600
        self.image_offset_x = max(0, (canvas_width - new_width) // 2)
        self.image_offset_y = max(0, (canvas_height - new_height) // 2)
        image_id = self.canvas.create_image(self.image_offset_x, self.image_offset_y, anchor="nw", image=self.tk_image, tags="main_image")
        self.redraw_rectangles()
        padding = 20
        scroll_width = max(canvas_width, new_width + 2 * padding)
        scroll_height = max(canvas_height, new_height + 2 * padding)
        self.canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

    def redraw_rectangles(self):
        """
        Redraw all field selection rectangles on the canvas.
        
        Each rectangle is scaled according to current zoom level
        and displayed with a blue outline.
        """
        if not self.rectangles:
            return
        for rect in self.rectangles:
            x = int(rect["x"] * self.zoom_factor + self.image_offset_x)
            y = int(rect["y"] * self.zoom_factor + self.image_offset_y)
            w = int(rect["w"] * self.zoom_factor)
            h = int(rect["h"] * self.zoom_factor)
            self.canvas.create_rectangle(x, y, x + w, y + h, outline="#2563eb", width=2, tags="field_rect")

    def update_minimap(self):
        if not self.minimap_canvas or not self.image:
            return
        self.minimap_canvas.delete("all")
        minimap_width = self.minimap_canvas.winfo_width(); minimap_height = self.minimap_canvas.winfo_height()
        if minimap_width <= 1 or minimap_height <= 1:
            return
        scale_x = minimap_width / self.image.width; scale_y = minimap_height / self.image.height
        minimap_scale = min(scale_x, scale_y)
        scaled_width = int(self.image.width * minimap_scale); scaled_height = int(self.image.height * minimap_scale)
        x = (minimap_width - scaled_width) // 2; y = (minimap_height - scaled_height) // 2
        self.minimap_canvas.create_rectangle(x, y, x + scaled_width, y + scaled_height, outline="#2563eb", width=2, tags="minimap_border")
        for rect in self.rectangles:
            mx = x + int(rect["x"] * minimap_scale); my = y + int(rect["y"] * minimap_scale)
            mw = int(rect["w"] * minimap_scale); mh = int(rect["h"] * minimap_scale)
            self.minimap_canvas.create_rectangle(mx, my, mx + mw, my + mh, outline="#ef4444", width=1, tags="minimap_rect")

    # ==========================================================================
    # TREEVIEW/CONTEXT/EDIT/DELETE METHODS
    # ==========================================================================

    def on_field_select(self, event):
        """
        Handle field selection from the treeview.
        
        When a field is selected, highlight its rectangle on the canvas
        with a yellow outline for visual feedback.
        """
        selection = self.fields_tree.selection()
        if selection:
            item = self.fields_tree.item(selection[0])
            field_name = item['values'][0]
            for i, rect in enumerate(self.rectangles):
                if rect["name"] == field_name:
                    self.canvas.delete("highlight")
                    x = int(rect["x"] * self.zoom_factor + self.image_offset_x)
                    y = int(rect["y"] * self.zoom_factor + self.image_offset_y)
                    w = int(rect["w"] * self.zoom_factor); h = int(rect["h"] * self.zoom_factor)
                    self.canvas.create_rectangle(x, y, x + w, y + h, outline="#fbbf24", width=4, tags="highlight")
                    break

    def show_context_menu(self, event):
        """
        Display context menu for right-click on treeview items.
        
        Provides options to edit or delete the selected field.
        """
        item_id = self.fields_tree.identify_row(event.y)
        if not item_id:
            return
        self.fields_tree.selection_set(item_id)
        menu = tk.Menu(self.fields_tree, tearoff=0)
        menu.add_command(label="✏️ Edit Name", command=self.edit_field_name)
        menu.add_command(label="🗑️ Delete Field", command=self.delete_field)
        menu.post(event.x_root, event.y_root)

    def edit_field_name(self, event=None):
        """
        Open a dialog to rename the selected field.
        
        Validates that the new name doesn't already exist
        and updates both the internal rectangle data and UI.
        """
        selection = self.fields_tree.selection()
        if not selection:
            return
        item = self.fields_tree.item(selection[0])
        current_name = item['values'][0]
        dialog = tk.Toplevel(self.fields_tree)
        dialog.title("Edit Field Name")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self.fields_tree.winfo_toplevel())
        dialog.grab_set()
        dialog.geometry("+{}+{}".format(self.fields_tree.winfo_rootx() + 50, self.fields_tree.winfo_rooty() + 50))
        tk.Label(dialog, text="Enter new field name:", font=('Arial', 10)).pack(pady=(20, 5))
        name_var = tk.StringVar(value=current_name)
        entry = tk.Entry(dialog, textvariable=name_var, font=('Arial', 10))
        entry.pack(pady=(0, 10), padx=20, fill=tk.X)
        entry.select_range(0, tk.END); entry.focus()

        def save_name():
            new_name = name_var.get().strip()
            if new_name and new_name != current_name:
                if any(rect["name"] == new_name for rect in self.rectangles):
                    messagebox.showerror("Error", f"Field name '{new_name}' already exists!")
                    return
                for rect in self.rectangles:
                    if rect["name"] == current_name:
                        rect["name"] = new_name; break
                self.update_field_list(); self.update_status(f"✅ Field renamed: {current_name} → {new_name}", "#10b981")
            dialog.destroy()

        def cancel(): dialog.destroy()

        button_frame = tk.Frame(dialog); button_frame.pack(pady=(0, 10))
        tk.Button(button_frame, text="Save", command=save_name, bg="#10b981", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT)
        dialog.bind('<Return>', lambda e: save_name()); dialog.bind('<Escape>', lambda e: cancel())

    def delete_field(self):
        """
        Remove the selected field from the template.
        
        Shows a confirmation dialog before deletion.
        Updates canvas, field list, statistics, and minimap.
        """
        selection = self.fields_tree.selection()
        if not selection:
            return
        item = self.fields_tree.item(selection[0])
        field_name = item['values'][0]
        if not messagebox.askyesno("Delete Field", f"Are you sure you want to delete field '{field_name}'?"):
            return
        self.rectangles = [rect for rect in self.rectangles if rect["name"] != field_name]
        self.redraw_image(); self.update_field_list(); self.update_field_stats(); self.update_minimap(); self.update_status(f"🗑️ Field deleted: {field_name}", "#ef4444")

    def update_field_list(self):
        """
        Refresh the treeview with current field data.
        
        Clears and repopulates the fields table with all
        rectangles. Also updates the count label.
        """
        for item in self.fields_tree.get_children():
            self.fields_tree.delete(item)
        for rect in self.rectangles:
            self.fields_tree.insert("", tk.END, values=(rect["name"], rect["x"], rect["y"], rect["w"], rect["h"]))
        count = len(self.rectangles)
        if count == 0: self.field_count_label.config(text="No fields selected")
        elif count == 1: self.field_count_label.config(text="1 field selected")
        else: self.field_count_label.config(text=f"{count} fields selected")

    def update_field_stats(self):
        """
        Calculate and display statistics for all selected fields.
        
        Shows:
        - Total number of fields
        - X and Y position ranges
        - Average width and height
        - Total area coverage
        """
        self.stats_text.config(state=tk.NORMAL); self.stats_text.delete(1.0, tk.END)
        if not self.rectangles:
            self.stats_text.insert(tk.END, "No fields selected yet.\n\nSelect areas on the image to see statistics.")
        else:
            stats = []
            stats.append(f"📊 FIELD STATISTICS")
            stats.append("=" * 30)
            stats.append(f"Total Fields: {len(self.rectangles)}")
            stats.append("")
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
            self.stats_text.insert(tk.END, "\n".join(stats))
        self.stats_text.config(state=tk.DISABLED)

    # ==========================================================================
    # IMAGE & TEMPLATE OPERATIONS
    # ==========================================================================

    def open_image(self):
        """
        Open an image file for template creation.
        
        Supported formats: PNG, JPG, JPEG
        Resets zoom, clears existing rectangles, and displays the image.
        """
        path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if not path: return
        try:
            self.original_image = Image.open(path)
            self.image = self.original_image.copy()
            self.zoom_factor = 1.0; self.image_offset_x = 0; self.image_offset_y = 0
            self.rectangles = []
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.update_idletasks()
            self.update_zoom_display(); self.redraw_image(); self.update_minimap(); self.update_field_list(); self.update_field_stats()
            if self.preview_text:
                self.preview_text.config(state=tk.NORMAL); self.preview_text.delete(1.0, tk.END); self.preview_text.insert(1.0, "Pilih area dengan drag mouse untuk ekstraksi teks...\n\n💡 Tips:\n• Drag mouse untuk memilih area\n• Area minimum 5x5 pixels\n• Gunakan Preview untuk melihat hasil OCR\n• Scroll untuk zoom in/out\n• Pilih field dari tabel untuk highlight"); self.preview_text.config(state=tk.DISABLED)
            self.update_status(f"✅ Image loaded: {self.image.width}x{self.image.height} • Zoom: 100%", "#10b981")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to load image: {str(e)}")
            self.image = None; self.tk_image = None

    # ==========================================================================
    # MOUSE EVENT HANDLERS FOR RECTANGLE SELECTION
    # ==========================================================================

    def on_mouse_down(self, event):
        """
        Handle mouse button press to start rectangle selection.
        
        Records the starting position and creates a temporary
        rectangle outline for visual feedback during drag.
        """
        if not self.image:
            messagebox.showwarning("⚠️ Warning", "Buka gambar terlebih dahulu!")
            return
        canvas_x = self.canvas.canvasx(event.x); canvas_y = self.canvas.canvasy(event.y)
        image_x = (canvas_x - self.image_offset_x) / self.zoom_factor; image_y = (canvas_y - self.image_offset_y) / self.zoom_factor
        self.start_x = image_x; self.start_y = image_y
        self.current_rect = self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x, canvas_y, outline="#2563eb", width=3, tags="selection_rect")

    def on_mouse_drag(self, event):
        """
        Handle mouse drag to resize the selection rectangle.
        
        Updates the rectangle dimensions in real-time as the user
        drags the mouse to define the field region.
        """
        if self.current_rect:
            canvas_x = self.canvas.canvasx(event.x); canvas_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.current_rect, self.start_x * self.zoom_factor + self.image_offset_x, self.start_y * self.zoom_factor + self.image_offset_y, canvas_x, canvas_y)

    def on_mouse_up(self, event):
        """
        Handle mouse button release to finalize rectangle selection.
        
        If the rectangle is valid (minimum 5x5 pixels), adds it as
        a new field. Otherwise, deletes the temporary selection.
        """
        if self.current_rect:
            canvas_x = self.canvas.canvasx(event.x); canvas_y = self.canvas.canvasy(event.y)
            image_x = (canvas_x - self.image_offset_x) / self.zoom_factor; image_y = (canvas_y - self.image_offset_y) / self.zoom_factor
            x, y = min(self.start_x, image_x), min(self.start_y, image_y)
            w, h = abs(image_x - self.start_x), abs(image_y - self.start_y)
            self.canvas.delete(self.current_rect); self.current_rect = None
            if w > 5 and h > 5:
                field_name = f"field_{len(self.rectangles)+1}"
                self.rectangles.append({"name": field_name, "x": int(x), "y": int(y), "w": int(w), "h": int(h)})
                self.redraw_rectangles(); self.update_field_list(); self.update_field_stats(); self.update_minimap(); self.update_status(f"✅ Added {field_name}: x={x}, y={y}, w={w}, h={h}", "#10b981")
            else:
                self.update_status("❌ Rectangle too small, deleted", "#ef4444")

    def save_template(self):
        """
        Save the current field selections as a JSON template file.
        
        Prompts user for file location and saves rectangle data
        in JSON format. Also copies to Template/ directory.
        """
        if not self.rectangles:
            messagebox.showwarning("⚠️ Warning", "No areas selected.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not save_path: return
        try:
            with open(save_path, "w") as f: json.dump({"fields": self.rectangles}, f, indent=4)
            templates_dir = getattr(self.parent_frame, 'templates_dir', None)
            final_path = save_path
            if templates_dir:
                try:
                    os.makedirs(templates_dir, exist_ok=True)
                    dest = os.path.join(templates_dir, os.path.basename(save_path))
                    if os.path.abspath(save_path) != os.path.abspath(dest):
                        if os.path.exists(dest):
                            overwrite = messagebox.askyesno("Overwrite?", f"Template {os.path.basename(dest)} already exists in Template/. Overwrite?")
                            if not overwrite:
                                base, ext = os.path.splitext(os.path.basename(save_path))
                                dest = os.path.join(templates_dir, f"{base}_{int(time.time())}{ext}")
                        shutil.copy(save_path, dest); final_path = dest
                except Exception:
                    pass
            messagebox.showinfo("✅ Success", f"Template saved to: {final_path}")
            if hasattr(self.parent_frame, 'on_template_created'):
                try: self.parent_frame.on_template_created(final_path)
                except Exception: pass
            if hasattr(self.parent_frame, 'refresh_templates'):
                try: self.parent_frame.refresh_templates()
                except Exception: pass
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to save template: {str(e)}")

    def load_template(self, path):
        """
        Load a template JSON file and restore field selections.
        
        Args:
            path: Path to the JSON template file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(path, "r") as f: data = json.load(f)
            fields = data.get("fields", [])
            if not isinstance(fields, list): raise ValueError("Invalid template format: 'fields' should be a list")
            self.rectangles = fields
            try: self.canvas.delete("all")
            except Exception: pass
            if hasattr(self, 'tk_image') and self.tk_image:
                try:
                    canvas_width = self.canvas.winfo_width() or self.viewport_frame.winfo_width() or 800
                    canvas_height = self.canvas.winfo_height() or self.viewport_frame.winfo_height() or 600
                    x = max(0, (canvas_width - self.image.width) // 2)
                    y = max(0, (canvas_height - self.image.height) // 2)
                    self.canvas.create_image(x, y, anchor="nw", image=self.tk_image, tags="main_image")
                    self.zoom_factor = getattr(self, 'zoom_factor', 1.0)
                    self.image_offset_x = getattr(self, 'image_offset_x', x)
                    self.image_offset_y = getattr(self, 'image_offset_y', y)
                except Exception:
                    pass
            try: self.redraw_rectangles()
            except Exception:
                try:
                    for rect in self.rectangles:
                        x, y, w, h = rect.get('x', 0), rect.get('y', 0), rect.get('w', 0), rect.get('h', 0)
                        self.canvas.create_rectangle(x, y, x + w, y + h, outline="#2563eb", width=2, tags='field_rect')
                except Exception: pass
            try: self.update_field_list()
            except Exception: pass
            try: self.update_minimap()
            except Exception: pass
            return True
        except Exception as e:
            messagebox.showerror("❌ Error", f"Gagal memuat template: {e}")
            return False

    def open_template_file(self):
        """
        Open a file dialog to load an existing template.
        
        Calls load_template() and updates status on success.
        """
        initial = getattr(self.parent_frame, 'templates_dir', 'Template')
        path = filedialog.askopenfilename(title="Open Template JSON", initialdir=initial, filetypes=[("JSON", "*.json")])
        if not path: return
        ok = self.load_template(path)
        if ok:
            try:
                if hasattr(self.parent_frame, 'on_template_created'):
                    self.parent_frame.on_template_created(path)
            except Exception: pass
            self.update_status(f"📂 Template dimuat: {os.path.basename(path)}", "#10b981")

    def preview_extractions(self):
        """
        Run OCR on all selected field regions for preview.
        
        Uses EnhancedOCR to extract text with confidence scores.
        Displays results in the Extracted Text tab with summary.
        Shows processing time and improvement tips if needed.
        """
        if not self.image:
            messagebox.showwarning("⚠️ Warning", "Open an image first!")
            return
        if not self.rectangles:
            messagebox.showwarning("⚠️ Warning", "Select at least one area first!")
            return
        try:
            if self.original_image:
                cv_image = cv2.cvtColor(cv2.imread(self.original_image.filename), cv2.COLOR_RGB2BGR)
            else:
                messagebox.showerror("❌ Error", "No original image file available")
                return
            self.fields_notebook.select(self.fields_notebook.tabs()[1])
            self.preview_text.config(state=tk.NORMAL); self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "🚀 ENHANCED OCR PREVIEW\n")
            self.preview_text.insert(tk.END, "=" * 50 + "\n")
            ocr = EnhancedOCR(languages="eng+ind", confidence_threshold=0.6)
            extracted_count = 0; high_confidence_count = 0; total_processing_time = 0
            for i, field in enumerate(self.rectangles):
                x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                crop = cv_image[y:y+h, x:x+w]
                if crop.size == 0:
                    self.preview_text.insert(tk.END, f"🔹 {field['name'].upper()}\n   ❌ Error: Empty crop region\n\n")
                    continue
                start_time = time.time(); ocr_result = ocr.extract_text(crop, debug=False); processing_time = time.time() - start_time; total_processing_time += processing_time
                self.preview_text.insert(tk.END, f"🔹 {field['name'].upper()}\n   Position: ({x}, {y}) Size: {w}x{h}\n   Strategy: {ocr_result['strategy_used']}\n   Processing time: {processing_time:.3f}s\n")
                if ocr_result['text']:
                    confidence_color = "🟢" if ocr_result['confidence'] >= 0.8 else "🟡" if ocr_result['confidence'] >= 0.6 else "🔴"
                    self.preview_text.insert(tk.END, f"   Text: {ocr_result['text']}\n   Confidence: {confidence_color} {ocr_result['confidence']:.3f}\n")
                    extracted_count += 1
                    if ocr_result['confidence'] >= 0.8: high_confidence_count += 1
                else:
                    self.preview_text.insert(tk.END, "   Text: [No text detected]\n   Confidence: 🔴 {ocr_result['confidence']:.3f}\n")
                self.preview_text.insert(tk.END, "\n")
            self.preview_text.insert(tk.END, f"📊 ENHANCED OCR SUMMARY:\n   Total fields: {len(self.rectangles)}\n   Text extracted: {extracted_count}\n   High confidence (≥0.8): {high_confidence_count}\n   Success rate: {(extracted_count/len(self.rectangles)*100):.1f}%\n   Average time per field: {(total_processing_time/len(self.rectangles)*1000):.1f}ms\n")
            if high_confidence_count < len(self.rectangles) * 0.5:
                self.preview_text.insert(tk.END, "\n💡 IMPROVEMENT TIPS:\n   • Increase image quality/resolution\n   • Adjust field boundaries to exclude background\n   • Ensure good contrast between text and background\n")
            self.preview_text.config(state=tk.DISABLED)
            self.update_status(f"🚀 Enhanced OCR completed! {extracted_count}/{len(self.rectangles)} fields extracted", "#10b981")
            message = f"Enhanced OCR completed!\n\n📊 Results:\n• Total fields: {len(self.rectangles)}\n• Successfully extracted: {extracted_count}\n• High confidence: {high_confidence_count}\n• Success rate: {(extracted_count/len(self.rectangles)*100):.1f}%\n• Average processing time: {(total_processing_time/len(self.rectangles)*1000):.1f}ms"
            messagebox.showinfo("✅ Enhanced OCR Complete", message)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to preview extractions: {str(e)}")
            self.update_status("❌ Enhanced OCR failed", "#ef4444")
