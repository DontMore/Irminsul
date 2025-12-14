# Panduan Virtual Environment untuk Project OCR

## 1. Membuat Virtual Environment

### Menggunakan venv (Built-in Python)
```bash
# Di direktori project Anda
python3 -m venv venv

# atau untuk Python 2 (jika diperlukan)
python -m virtualenv venv
```

### Menggunakan virtualenv (alternatif)
```bash
# Install virtualenv terlebih dahulu
pip install virtualenv

# Buat virtual environment
virtualenv venv
```

## 2. Mengaktifkan Virtual Environment

### Di Linux/macOS:
```bash
source venv/bin/activate
```

### Di Windows:
```bash
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

### Di Git Bash (Windows):
```bash
source venv/Scripts/activate
```

## 3. Menginstall Dependencies

Setelah virtual environment aktif, install dependencies dari requirements.txt:

```bash
pip install -r requirements.txt
```

Atau install satu per satu:
```bash
pip install opencv-python-headless pytesseract pandas numpy Pillow
```

## 4. Verifikasi Installation

Cek apakah packages terinstall dengan benar:
```bash
pip list
```

## 5. Menjalankan Aplikasi

Setelah semua terinstall, Anda bisa menjalankan aplikasi GUI:
```bash
python gui.py
```

Atau aplikasi GUI modern:
```bash
python gui_modern.py
```

## 6. Menonaktifkan Virtual Environment

Ketika selesai bekerja:
```bash
deactivate
```

## 7. Tips Tambahan

### Membuat requirements.txt
```bash
pip freeze > requirements.txt
```

### Menghapus Virtual Environment
```bash
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

### Menggunakan .gitignore
Pastikan folder `venv/` ditambahkan ke .gitignore:
```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
```

## Troubleshooting

### Error "python: command not found"
```bash
# Gunakan python3 sebagai gantinya
python3 -m venv venv
python3 -m pip install -r requirements.txt
python3 gui.py
```

### Error permission di Linux/macOS
```bash
# Buat executable script
chmod +x venv/bin/activate
```

### Error Tesseract
Pastikan Tesseract OCR terinstall di sistem:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows - download dari https://github.com/UB-Mannheim/tesseract/wiki
```

## Perbedaan dengan Docker

Jika Anda menggunakan Docker (terlihat ada dockerfile), Anda bisa juga menjalankan aplikasi tanpa virtual environment dengan:
```bash
docker build -t ocr-app .
docker run -it ocr-app
```

Tapi untuk development lokal, virtual environment lebih disarankan.
