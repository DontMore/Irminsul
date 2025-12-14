#!/usr/bin/env python3
"""
Script untuk preview OCR menggunakan Docker
"""

import os
import json
import cv2
import tempfile
import subprocess
import sys
import base64
import numpy as np
from PIL import Image


def encode_image_to_base64(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def run_docker_ocr_preview(image_path, rectangles):
    """
    Jalankan OCR preview menggunakan Docker container

    Args:
        image_path (str): Path ke gambar
        rectangles (list): List of rectangles dengan format [{"name": str, "x": int, "y": int, "w": int, "h": int}, ...]

    Returns:
        dict: Hasil OCR untuk setiap field
    """
    try:
        # Encode gambar ke base64
        image_b64 = encode_image_to_base64(image_path)

        # Buat temporary file untuk input JSON
        temp_input = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_input_data = {
            "image": image_b64,
            "fields": rectangles
        }
        json.dump(temp_input_data, temp_input)
        temp_input.close()

        # Buat temporary file untuk output
        temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_output.close()

        # Jalankan Docker container
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{temp_input.name}:/data/input.json:ro",
            "-v", f"{temp_output.name}:/data/output.json",
            "ocr-app",
            "preview",
            "/data/input.json",
            "/data/output.json"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise Exception(f"Docker command failed: {result.stderr}")

        # Baca hasil output
        with open(temp_output.name, 'r') as f:
            output_data = json.load(f)

        # Cleanup temporary files
        os.unlink(temp_input.name)
        os.unlink(temp_output.name)

        return output_data

    except subprocess.TimeoutExpired:
        raise Exception("OCR preview timeout - Docker container took too long")
    except Exception as e:
        # Cleanup pada error
        try:
            os.unlink(temp_input.name)
        except:
            pass
        try:
            os.unlink(temp_output.name)
        except:
            pass
        raise e


def main():
    """Main function untuk testing"""
    if len(sys.argv) < 3:
        print("Usage: python preview_ocr.py <image_path> <template_json>")
        sys.exit(1)

    image_path = sys.argv[1]
    template_path = sys.argv[2]

    # Load template
    with open(template_path, 'r') as f:
        template = json.load(f)

    rectangles = template.get('fields', [])

    print(f"🖼️  Processing image: {image_path}")
    print(f"📋 Template fields: {len(rectangles)}")

    try:
        results = run_docker_ocr_preview(image_path, rectangles)

        print("\n📊 OCR Results:")
        for field_name, text in results.items():
            print(f"🔹 {field_name}: '{text}'")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
