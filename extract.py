import os
import json
import cv2
import pytesseract
import pandas as pd
from PIL import Image

# Jika menggunakan Windows, set manual lokasi tesseract:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- LOAD TEMPLATE ---
with open("template.json", "r") as f:
    template = json.load(f)

FIELDS = template["fields"]

# --- FOLDER GAMBAR ---
IMAGE_DIR = "images"

# --- LIST OUTPUT ---
rows = []

# --- LOOP SEMUA GAMBAR DI FOLDER ---
for filename in os.listdir(IMAGE_DIR):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(IMAGE_DIR, filename)

        # Baca gambar
        image = cv2.imread(img_path)

        data = {"filename": filename}

        # --- EXTRACT BERDASARKAN TEMPLATE ---
        for field in FIELDS:
            x, y, w, h = field["x"], field["y"], field["w"], field["h"]

            crop = image[y:y+h, x:x+w]  # crop area

            text = pytesseract.image_to_string(crop, lang="eng+ind")
            text = text.strip()

            data[field["name"]] = text

        rows.append(data)
        print(f"Extracted from {filename}")

# --- SIMPAN KE CSV ---
df = pd.DataFrame(rows)
df.to_csv("hasil_ocr.csv", index=False, encoding="utf-8")

print("\nSelesai! Data tersimpan ke hasil_ocr.csv")
