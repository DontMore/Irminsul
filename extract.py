import os
import json
import cv2
import pytesseract
import pandas as pd
import sys


def run_ocr(template_path, image_folder, output_dir="/data"):
    print("=== OCR START ===")
    print(f"Template path : {template_path}")
    print(f"Image folder  : {image_folder}")
    print(f"Output dir    : {output_dir}")

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

    fields = template["fields"]
    rows = []

    images = os.listdir(image_folder)
    print(f"Jumlah file di folder gambar: {len(images)}")

    for filename in images:
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

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

            except Exception as e:
                print(f"  [ERROR] Field {field.get('name', '?')}: {e}")
                data[field["name"]] = ""

        rows.append(data)

    if not rows:
        print("⚠️ Tidak ada data OCR yang dihasilkan")

    # --- Simpan CSV ke volume ---
    output_path = os.path.join(output_dir, "hasil_ocr.csv")
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"=== OCR SELESAI ===")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract.py template.json image_folder")
        sys.exit(1)

    template = sys.argv[1]
    folder = sys.argv[2]

    run_ocr(template, folder)
