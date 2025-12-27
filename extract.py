import os
import json
import cv2
import pytesseract
import pandas as pd
import sys
import base64
import numpy as np
from PIL import Image
import io


def decode_base64_image(base64_string):
    """Decode base64 string ke PIL Image"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    # Convert to OpenCV format
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def run_ocr_preview(input_data):
    """Jalankan OCR preview untuk single image"""
    print("=== OCR PREVIEW START ===")

    image_b64 = input_data.get("image")
    fields = input_data.get("fields", [])

    if not image_b64:
        raise ValueError("No image data provided")

    # Decode gambar dari base64
    image = decode_base64_image(image_b64)

    results = {}

    for field in fields:
        try:
            x = field["x"]
            y = field["y"]
            w = field["w"]
            h = field["h"]

            # Crop area
            crop = image[y:y + h, x:x + w]

            # OCR
            text = pytesseract.image_to_string(
                crop,
                lang="eng+ind"
            ).strip()

            results[field["name"]] = text

        except Exception as e:
            print(f"  [ERROR] Field {field.get('name', '?')}: {e}")
            results[field["name"]] = ""

    return results


def run_ocr(template_path, image_folder, output_dir="/data", output_format="csv"):
    print("=== OCR BATCH START ===")
    print(f"Template path : {template_path}")
    print(f"Image folder  : {image_folder}")
    print(f"Output dir    : {output_dir}")
    print(f"Output format : {output_format}")
=======
class OCRGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Template Extractor")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
>>>>>>> origin/main

    # --- Validasi path ---
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template tidak ditemukan: {template_path}")

    if not os.path.isdir(image_folder):
        raise NotADirectoryError(f"Folder gambar tidak ditemukan: {image_folder}")

    # --- Load template ---
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)

    if "fields" not in template:
        raise KeyError("Template JSON tidak memiliki key 'fields'")

<<<<<<< HEAD
    fields = template["fields"]
    rows = []

    images = os.listdir(image_folder)
    print(f"Jumlah file di folder gambar: {len(images)}")

    for filename in images:
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
=======
        # --- LOG AREA ---
        tk.Label(root, text="Log:").pack()
        self.log_area = scrolledtext.ScrolledText(root, width=60, height=10)
        self.log_area.pack(padx=10, pady=5)

        # --- PREVIEW AREA ---
        tk.Label(root, text="Preview Hasil Ekstraksi:").pack()
        self.preview_area = scrolledtext.ScrolledText(root, width=60, height=10)
        self.preview_area.pack(padx=10, pady=5)

    def log(self, text):
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def preview(self, text):
        self.preview_area.insert(tk.END, text + "\n")
        self.preview_area.see(tk.END)

    def load_template(self):
        path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Pilih Template JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if path:
            self.template_path = path
            self.log(f"Template dipilih: {path}")
>>>>>>> origin/main

        img_path = os.path.join(image_folder, filename)
        print(f"Processing: {filename}")

        image = cv2.imread(img_path)
        if image is None:
            print(f"  [SKIP] Tidak bisa membaca gambar")
            continue

        data = {"filename": filename}

        for field in fields:
            try:
                x = field["x"]
                y = field["y"]
                w = field["w"]
                h = field["h"]

                crop = image[y:y + h, x:x + w]

                text = pytesseract.image_to_string(
                    crop,
                    lang="eng+ind"
                ).strip()

                data[field["name"]] = text

<<<<<<< HEAD
            except Exception as e:
                print(f"  [ERROR] Field {field.get('name', '?')}: {e}")
                data[field["name"]] = ""
=======
        self.log("\n=== Mulai proses OCR ===")
        self.preview_area.delete(1.0, tk.END)  # Clear preview area
>>>>>>> origin/main

        rows.append(data)

    if not rows:
        print("⚠️ Tidak ada data OCR yang dihasilkan")

    # --- Simpan output berdasarkan format ---
    df = pd.DataFrame(rows)

    if output_format.lower() == "excel":
        output_path = os.path.join(output_dir, "hasil_ocr.xlsx")
        df.to_excel(output_path, index=False, engine='openpyxl')
    else:  # default to csv
        output_path = os.path.join(output_dir, "hasil_ocr.csv")
        df.to_csv(output_path, index=False, encoding="utf-8")

<<<<<<< HEAD
    print(f"=== OCR SELESAI ===")
    print(f"Output file: {output_path}")
=======
                # Crop + OCR tiap field
                for field in fields:
                    try:
                        x, y, w, h = field["x"], field["y"], field["w"], field["h"]
                        crop = image[y:y+h, x:x+w]
                        text = pytesseract.image_to_string(crop, lang="eng+ind").strip()
                        data[field["name"]] = text
                    except Exception as e:
                        self.log(f"[ERROR] Field {field['name']} gagal diambil: {e}")
                        data[field["name"]] = ""

                rows.append(data)
                self.log(f"[OK] Extracted: {filename}")

                # Preview hasil ekstraksi
                preview_text = f"--- {filename} ---\n"
                for field in fields:
                    preview_text += f"{field['name']}: {data[field['name']]}\n"
                self.preview(preview_text)

        # Save CSV
        df = pd.DataFrame(rows)
        df.to_csv("hasil_ocr.csv", index=False, encoding="utf-8")

        self.log("\nSelesai! Data disimpan ke hasil_ocr.csv")
        messagebox.showinfo("Selesai", "OCR selesai!\nFile: hasil_ocr.csv")
>>>>>>> origin/main


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python extract.py template.json image_folder output_dir output_format")
        print("output_format: csv or excel")
        sys.exit(1)

    template = sys.argv[1]
    folder = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "/data"
    output_format = sys.argv[4] if len(sys.argv) > 4 else "csv"

    run_ocr(template, folder, output_dir=output_dir, output_format=output_format)
