
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import os
from PIL import Image, ImageTk
import json
import cv2
import pytesseract
from screenshot import ScreenshotMiniGUI

class TemplateGUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.image = None
        self.tk_image = None
        self.original_image = None  # Store original image for resizing
        self.rectangles = []
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.preview_text = None

        self.setup_ui()

    def setup_ui(self):
        # Paned window for split layout
        self.paned = tk.PanedWindow(self.parent_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Canvas
        self.canvas_frame = tk.Frame(self.paned)
        self.paned.add(self.canvas_frame)

        self.canvas = tk.Canvas(self.canvas_frame, cursor="cross", bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right side: Sidebar
        self.sidebar = tk.Frame(self.paned, width=300)
        self.paned.add(self.sidebar)


        tk.Label(self.sidebar, text="Extraction Preview:", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=5)
        self.preview_text = tk.Text(self.sidebar, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status label for user feedback
        self.status_label = tk.Label(self.canvas_frame, text="Pilih 'Open Image' untuk memulai", 
                                   font=("Arial", 10), fg="gray")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

        # Buttons frame
        frame = tk.Frame(self.parent_frame)
        frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        tk.Button(frame, text="Open Image", command=self.open_image, bg="lightblue").pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Preview Extractions", command=self.preview_extractions, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Save Template", command=self.save_template, bg="orange").pack(side=tk.LEFT, padx=5)

        # Events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)


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
            max_width, max_height = 1200, 800  # Reasonable limits
            if self.original_image.width > max_width or self.original_image.height > max_height:
                # Calculate scaling factor to fit within max dimensions
                scale_w = max_width / self.original_image.width
                scale_h = max_height / self.original_image.height
                scale = min(scale_w, scale_h)
                
                new_width = int(self.original_image.width * scale)
                new_height = int(self.original_image.height * scale)
                

                self.image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.status_label.config(text=f"Image resized from {self.original_image.width}x{self.original_image.height} to {new_width}x{new_height}")
            else:
                self.image = self.original_image.copy()
                self.status_label.config(text=f"Image loaded: {self.image.width}x{self.image.height}")
            
            # CRITICAL: Store PhotoImage as instance variable to prevent garbage collection
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            # Clear canvas and reset rectangles
            self.canvas.delete("all")
            self.rectangles = []
            
            # Calculate center position for image
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # If canvas not yet sized, use default values
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 600, 400
            
            x = max(0, (canvas_width - self.image.width) // 2)
            y = max(0, (canvas_height - self.image.height) // 2)
            
            # Display image on canvas
            self.canvas.create_image(x, y, anchor="nw", image=self.tk_image)
            
            # Update canvas scroll region to include entire image
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
            
            # Clear preview text
            if self.preview_text:
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, "Pilih area dengan drag mouse untuk ekstraksi teks...")
                self.preview_text.config(state=tk.DISABLED)
                
            messagebox.showinfo("Success", f"Image loaded successfully!\nSize: {self.image.width}x{self.image.height}")
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}\n\nTips:\n- Pastikan file gambar tidak corrupt\n- Format yang didukung: PNG, JPG, JPEG"
            messagebox.showerror("Error", error_msg)
            print(f"Error loading image: {e}")


    def on_mouse_down(self, event):
        """Handle mouse press for rectangle selection"""
        if not self.image:
            messagebox.showwarning("Warning", "Buka gambar terlebih dahulu!")
            return
            
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline="red", width=2, tags="selection_rect"
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
                self.status_label.config(text=f"Added {field_name}: x={x}, y={y}, w={w}, h={h}")
            else:
                self.canvas.delete(self.current_rect)
                self.status_label.config(text="Rectangle too small, deleted")
                
            self.current_rect = None

    def save_template(self):
        if not self.rectangles:
            messagebox.showwarning("Warning", "No areas selected.")
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

            messagebox.showinfo("Success", f"Template saved to: {save_path}")
            # Notify parent about new template
            if hasattr(self.parent_frame, 'on_template_created'):
                self.parent_frame.on_template_created(save_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")


    def preview_extractions(self):
        """Preview OCR extractions from selected areas"""
        if not self.image:
            messagebox.showwarning("Warning", "Open an image first!")
            return

        if not self.rectangles:
            messagebox.showwarning("Warning", "Select at least one area first!")
            return

        try:
            # Convert PIL image to OpenCV format
            if self.original_image:
                cv_image = cv2.cvtColor(cv2.imread(self.original_image.filename), cv2.COLOR_RGB2BGR)
            else:
                messagebox.showerror("Error", "No original image file available")
                return

            # Clear previous preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Extraction Preview:\n\n")

            for field in self.rectangles:
                x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                crop = cv_image[y:y+h, x:x+w]
                text = pytesseract.image_to_string(crop, lang="eng+ind").strip()
                self.preview_text.insert(tk.END, f"{field['name']}: {text}\n\n")

            self.preview_text.config(state=tk.DISABLED)
            messagebox.showinfo("Preview", "Extraction preview generated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview extractions: {str(e)}")

class OCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR GUI - Screenshot + Template Creator + Docker")
        self.template = ""
        self.image_folder = "screenshots"
        self.current_template_path = ""

        os.makedirs(self.image_folder, exist_ok=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Screenshot
        self.screenshot_frame = tk.Frame(self.notebook)
        self.notebook.add(self.screenshot_frame, text="📸 Screenshot")
        self.setup_screenshot_tab()

        # Tab 2: Template Creator
        self.template_frame = tk.Frame(self.notebook)
        self.notebook.add(self.template_frame, text="📐 Template Creator")
        self.setup_template_tab()

        # Tab 3: OCR Process
        self.ocr_frame = tk.Frame(self.notebook)
        self.notebook.add(self.ocr_frame, text="🔍 OCR Process")
        self.setup_ocr_tab()

    def setup_screenshot_tab(self):
        tk.Label(self.screenshot_frame, text="Screenshot Tools", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Button(self.screenshot_frame, text="Take Screenshot", command=self.open_screenshot, 
                 bg="lightblue", font=("Arial", 12)).pack(pady=10)
        
        self.screenshot_log = scrolledtext.ScrolledText(self.screenshot_frame, width=50, height=15)
        self.screenshot_log.pack(padx=10, pady=10)

    def setup_template_tab(self):
        tk.Label(self.template_frame, text="Template Creator", font=("Arial", 14, "bold")).pack(pady=5)
        self.template_gui = TemplateGUI(self.template_frame)

    def setup_ocr_tab(self):
        tk.Label(self.ocr_frame, text="OCR Processing", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Template selection
        template_frame = tk.Frame(self.ocr_frame)
        template_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(template_frame, text="Template JSON:").pack(side=tk.LEFT)
        self.template_label = tk.Label(template_frame, text="Belum dipilih", fg="red")
        self.template_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(template_frame, text="Pilih Template", command=self.pick_template, bg="lightgreen").pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = tk.Frame(self.ocr_frame)
        action_frame.pack(pady=20)
        
        tk.Button(action_frame, text="Mulai OCR", bg="green", fg="white", font=("Arial", 12),
                  command=self.run_ocr).pack(side=tk.LEFT, padx=10)
        
        # Log area
        tk.Label(self.ocr_frame, text="Process Log:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.log = scrolledtext.ScrolledText(self.ocr_frame, width=60, height=10)
        self.log.pack(padx=10, pady=5)

    def open_screenshot(self):
        win = tk.Toplevel(self.root)
        ScreenshotMiniGUI(win, callback=self.after_screenshot)

    def after_screenshot(self, path):
        self.screenshot_log.insert(tk.END, f"Screenshot tersimpan: {path}\n")
        self.screenshot_log.see(tk.END)

    def on_template_created(self, template_path):
        """Callback when a new template is created"""
        self.current_template_path = template_path
        self.template_label.config(text=os.path.basename(template_path), fg="green")
        self.log.insert(tk.END, f"Template baru dibuat: {template_path}\n")
        self.log.see(tk.END)
        
        # Switch to OCR tab
        self.notebook.select(self.ocr_frame)

    def pick_template(self):
        self.template = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if self.template:
            self.current_template_path = self.template
            self.template_label.config(text=os.path.basename(self.template), fg="green")
            self.log.insert(tk.END, f"Template dipilih: {self.template}\n")
            self.log.see(tk.END)

    def run_ocr(self):
        if not self.current_template_path:
            messagebox.showerror("Error", "Template belum dipilih. Buat template di tab Template Creator atau pilih template existing.")
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

            self.log.insert(tk.END, "Menjalankan OCR di Docker...\n")
            self.log.see(tk.END)
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log.insert(tk.END, "Selesai! Hasil OCR tersimpan di hasil_ocr.csv\n")
                self.log.see(tk.END)
                messagebox.showinfo("Selesai", "OCR selesai!")
            else:
                self.log.insert(tk.END, f"Error: {result.stderr}\n")
                self.log.see(tk.END)
                messagebox.showerror("Error", f"OCR gagal: {result.stderr}")
                
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker tidak ditemukan. Pastikan Docker sudah terinstall dan running.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRGui(root)
    root.mainloop()
