import os
import json
import cv2
import pytesseract
import pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Set Tesseract Path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCRGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Template Extractor")
        self.root.geometry("500x430")
        self.root.resizable(False, False)

        # --- VAR ---
        self.template_path = None
        self.image_folder = None

        # --- BUTTONS ---
        tk.Button(root, text="Pilih Template JSON", width=25, command=self.load_template)\
            .pack(pady=10)

        tk.Button(root, text="Pilih Folder Gambar", width=25, command=self.load_folder)\
            .pack(pady=5)

        tk.Button(root, text="Mulai OCR", width=25, bg="#4CAF50", fg="white",
                  command=self.start_ocr)\
            .pack(pady=10)

        # --- LOG AREA ---
        tk.Label(root, text="Log:").pack()
        self.log_area = scrolledtext.ScrolledText(root, width=60, height=17)
        self.log_area.pack(padx=10, pady=5)

    def log(self, text):
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def load_template(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Template", "*.json")])
        if path:
            self.template_path = path
            self.log(f"Template dipilih: {path}")

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder
            self.log(f"Folder gambar dipilih: {folder}")

    def start_ocr(self):
        if not self.template_path:
            messagebox.showwarning("Error", "Pilih file template JSON dulu!")
            return

        if not self.image_folder:
            messagebox.showwarning("Error", "Pilih folder gambar dulu!")
            return

        # Load template JSON
        with open(self.template_path, "r") as f:
            template = json.load(f)

        fields = template["fields"]
        rows = []

        self.log("\n=== Mulai proses OCR ===")

        # Loop semua file gambar
        for filename in os.listdir(self.image_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(self.image_folder, filename)

                image = cv2.imread(img_path)
                if image is None:
                    self.log(f"[SKIP] {filename} (gambar rusak)")
                    continue

                data = {"filename": filename}

                # Crop + OCR tiap field
                for field in fields:
                    x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                    crop = image[y:y+h, x:x+w]

                    text = pytesseract.image_to_string(crop, lang="eng+ind").strip()
                    data[field["name"]] = text

                rows.append(data)
                self.log(f"[OK] Extracted: {filename}")

        # Save CSV
        df = pd.DataFrame(rows)
        df.to_csv("hasil_ocr.csv", index=False, encoding="utf-8")

        self.log("\nSelesai! Data disimpan ke hasil_ocr.csv")
        messagebox.showinfo("Selesai", "OCR selesai!\nFile: hasil_ocr.csv")


# === RUN APP ===
if __name__ == "__main__":
    root = tk.Tk()
    app = OCRGuiApp(root)
    root.mainloop()
