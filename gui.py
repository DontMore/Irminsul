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
        
        self.setup_ui()

    def setup_ui(self):
        # Main container with modern padding
        main_container = create_modern_frame(self.parent_frame, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Paned window for split layout
        self.paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, bg='white', sashrelief=tk.RAISED, sashwidth=2)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Left side: Canvas with modern frame
        self.canvas_frame = create_modern_frame(self.paned, padding=0)
        self.paned.add(self.canvas_frame, minsize=600)

        # Modern canvas with border
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            cursor="cross", 
            bg="white",
            highlightthickness=1,
            highlightbackground="#e2e8f0"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Right side: Sidebar with modern styling
        self.sidebar = create_modern_frame(self.paned, padding=15)
        self.paned.add(self.sidebar, minsize=350)

        # Sidebar header
        header_frame = create_modern_frame(self.sidebar, padding=0)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        create_modern_label(
            header_frame, 
            "📊 Extraction Preview", 
            style='Modern.TLabel'
        ).pack(anchor="w")
        
        # Modern preview text widget
        preview_frame = create_modern_frame(self.sidebar, padding=0)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create modern text widget with scrollbar
        text_frame = tk.Frame(preview_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            height=20,
            font=('Consolas', 9),
            bg='#f8fafc',
            fg='#1e293b',
            insertbackground='#2563eb',
            selectbackground='#2563eb',
            selectforeground='white',
            relief='solid',
            borderwidth=1
        )
        
        # Modern scrollbar
        preview_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, style='Modern.Vertical.TScrollbar')
        self.preview_text.config(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.config(command=self.preview_text.yview)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status label with modern styling
        self.status_label = create_modern_label(
            self.canvas_frame, 
            "Pilih 'Open Image' untuk memulai", 
            style='Modern.TLabel'
        )
        self.status_label.pack(side=tk.BOTTOM, pady=15)

        # Modern buttons frame
        button_frame = create_modern_frame(main_container, padding=15)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Create modern buttons
        create_modern_button(
            button_frame, 
            "📁 Open Image", 
            self.open_image, 
            style='Modern.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))

        create_modern_button(
            button_frame, 
            "👁️ Preview Extractions", 
            self.preview_extractions, 
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))

        create_modern_button(
            button_frame, 
            "💾 Save Template", 
            self.save_template, 
            style='Accent.TButton'
        ).pack(side=tk.LEFT)

        # Events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def update_status(self, message, color="#64748b"):
        """Update status with modern styling"""
        self.status_label.config(text=message, foreground=color)

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
            
            # Resize image if too large for screen
            max_width, max_height = 1200, 800
            if self.original_image.width > max_width or self.original_image.height > max_height:
                scale_w = max_width / self.original_image.width
                scale_h = max_height / self.original_image.height
                scale = min(scale_w, scale_h)
                
                new_width = int(self.original_image.width * scale)
                new_height = int(self.original_image.height * scale)
                
                self.image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.update_status(f"Image resized from {self.original_image.width}x{self.original_image.height} to {new_width}x{new_height}", "#10b981")
            else:
                self.image = self.original_image.copy()
                self.update_status(f"Image loaded: {self.image.width}x{self.image.height}", "#10b981")
            
            # Store PhotoImage as instance variable to prevent garbage collection
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            # Clear canvas and reset rectangles
            self.canvas.delete("all")
            self.rectangles = []
            
            # Calculate center position for image
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 600, 400
            
            x = max(0, (canvas_width - self.image.width) // 2)
            y = max(0, (canvas_height - self.image.height) // 2)
            
            # Display image on canvas
            self.canvas.create_image(x, y, anchor="nw", image=self.tk_image)
            
            # Update canvas scroll region
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
            
            # Clear preview text
            if self.preview_text:
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "Pilih area dengan drag mouse untuk ekstraksi teks...\n\n💡 Tips:\n• Drag mouse untuk memilih area\n• Area minimum 5x5 pixels\n• Gunakan Preview untuk melihat hasil OCR")
                self.preview_text.config(state=tk.DISABLED)
                
            messagebox.showinfo("✅ Success", f"Image loaded successfully!\nSize: {self.image.width}x{self.image.height}")
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}\n\nTips:\n• Pastikan file gambar tidak corrupt\n• Format yang didukung: PNG, JPG, JPEG"
            messagebox.showerror("❌ Error", error_msg)
            print(f"Error loading image: {e}")

    def on_mouse_down(self, event):
        """Handle mouse press for rectangle selection"""
        if not self.image:
            messagebox.showwarning("⚠️ Warning", "Buka gambar terlebih dahulu!")
            return
            
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline="#2563eb", width=3, tags="selection_rect"
        )

    def on_mouse_drag(self, event):
        """Handle mouse drag for rectangle selection"""
        if self.current_rect:
            self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        """Handle mouse release for rectangle selection"""
        if self.current_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.current_rect)
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)

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
                self.update_status(f"✅ Added {field_name}: x={x}, y={y}, w={w}, h={h}", "#10b981")
            else:
                self.canvas.delete(self.current_rect)
                self.update_status("❌ Rectangle too small, deleted", "#ef4444")
                
            self.current_rect = None

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

            # Clear previous preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "📋 Extraction Preview:\n\n")

            for i, field in enumerate(self.rectangles):
                x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                crop = cv_image[y:y+h, x:x+w]
                text = pytesseract.image_to_string(crop, lang="eng+ind").strip()
                
                # Modern preview with better formatting
                self.preview_text.insert(tk.END, f"🔹 {field['name'].upper()}:\n")
                if text:
                    self.preview_text.insert(tk.END, f"   {text}\n\n")
                else:
                    self.preview_text.insert(tk.END, "   [No text detected]\n\n")

            self.preview_text.config(state=tk.DISABLED)
            self.update_status("👁️ Extraction preview generated!", "#10b981")
            messagebox.showinfo("✅ Preview", "Extraction preview generated!")
        except pytesseract.TesseractNotFoundError:
            error_msg = """❌ Tesseract OCR tidak terinstall!

Untuk menggunakan fitur preview OCR, install Tesseract:

🔧 Ubuntu/Debian:
   sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-ind

🔧 macOS:
   brew install tesseract tesseract-lang

🔧 Windows:
   Download dari: https://github.com/UB-Mannheim/tesseract/wiki
   Kemudian tambahkan ke PATH

💡 Alternatif: Gunakan Docker OCR untuk memproses gambar."""
            messagebox.showerror("❌ Tesseract Not Found", error_msg)
            self.update_status("❌ Install Tesseract untuk OCR preview", "#ef4444")
        except Exception as e:
            error_msg = f"Failed to preview extractions: {str(e)}\n\nTips:\n• Pastikan Tesseract sudah terinstall\n• Restart aplikasi setelah install Tesseract\n• Check PATH environment variable"
            messagebox.showerror("❌ Error", error_msg)

class OCRGui:
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
        ScreenshotMiniGUI(win, callback=self.after_screenshot)

    def after_screenshot(self, path):
        self.screenshot_log.insert(tk.END, f"✅ Screenshot tersimpan: {path}\n")
        self.screenshot_log.see(tk.END)

    def on_template_created(self, template_path):
        """Callback when a new template is created"""
        self.current_template_path = template_path
        self.template_label.config(text=os.path.basename(template_path), foreground="#10b981")
        self.log.insert(tk.END, f"✅ Template baru dibuat: {template_path}\n")
        self.log.see(tk.END)
        
        # Switch to OCR tab
        self.notebook.select(self.ocr_frame)

    def pick_template(self):
        self.template = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if self.template:
            self.current_template_path = self.template
            self.template_label.config(text=os.path.basename(self.template), foreground="#10b981")
            self.log.insert(tk.END, f"📁 Template dipilih: {self.template}\n")
            self.log.see(tk.END)

    def run_ocr(self):
        if not self.current_template_path:
            messagebox.showerror("❌ Error", "Template belum dipilih. Buat template di tab Template Creator atau pilih template existing.")
            return

        try:
            base_dir = os.path.dirname(self.current_template_path)

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{base_dir}:/data",
                "ocr-app",
                "/data/" + os.path.basename(self.current_template_path),
                "/data/" + self.image_folder
            ]

            self.log.insert(tk.END, "🚀 Menjalankan OCR di Docker...\n")
            self.log.see(tk.END)
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log.insert(tk.END, "✅ Selesai! Hasil OCR tersimpan di hasil_ocr.csv\n")
                self.log.see(tk.END)
                messagebox.showinfo("✅ Selesai", "OCR selesai!")
            else:
                self.log.insert(tk.END, f"❌ Error: {result.stderr}\n")
                self.log.see(tk.END)
                messagebox.showerror("❌ Error", f"OCR gagal: {result.stderr}")
                
        except FileNotFoundError:
            messagebox.showerror("❌ Error", "Docker tidak ditemukan. Pastikan Docker sudah terinstall dan running.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRGui(root)
    root.mainloop()
