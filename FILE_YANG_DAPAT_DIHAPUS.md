# List File yang Dapat Dihapus

## 🚫 File yang TIDAK DIPERLUKAN:

### 1. **Duplicate Files (Duplikat)**
- `gui_fixed.py` - Ini adalah versi intermediate dari `gui.py`. File `gui.py` sudah final dan digunakan.

### 2. **Batch Files (Tidak diperlukan)**
- `extract.bat` - Sudah ada `extract.py`
- `screenshot.bat` - Sudah ada `screenshot.py`  
- `template.bat` - Sudah ada `template.py` (jika ada)

### 3. **Debug & Testing Files**
- `debug_image_loading.py` - Debug script yang sudah selesai digunakan
- `test_gui_fix.py` - Test script untuk validasi fix GUI
- `test_image.png` - Test image yang hanya untuk testing

### 4. **Output Files**
- `hasil_ocr.csv` - Output file yang bisa di-generate lagi saat menjalankan OCR

### 5. **Documentation Files yang sudah tidak relevan**
- `ANALISIS_MASALAH.md` - Sudah ada `PERBAIKAN_RINGKASAN.md` yang lebih lengkap

### 6. **Git Files (Opsional)**
- `.gitattributes` - Git attributes (bisa di-hapus jika tidak menggunakan git)
- `.gitignore` - Git ignore (bisa di-hapus jika tidak menggunakan git)

---

## ✅ File yang HARUS DIPERTAHANKAN:

### Core Application Files:
- `gui.py` - Main GUI application (FINAL VERSION)
- `screenshot.py` - Screenshot functionality
- `extract.py` - OCR extraction logic
- `template.py` - Template system
- `dockerfile` - Docker configuration

### Configuration & Dependencies:
- `requirements.txt` - Python dependencies
- `template.json` - Template file

### Documentation:
- `README.md` - Project documentation
- `TODO.md` - Task tracking
- `PERBAIKAN_RINGKASAN.md` - Fix documentation

---

## 📝 Total File yang Bisa Dihapus: **10-12 files**

### Command untuk menghapus file:
```bash
# Hapus file duplikat dan debug
rm gui_fixed.py debug_image_loading.py test_gui_fix.py test_image.png

# Hapus batch files
rm *.bat

# Hapus output files
rm hasil_ocr.csv

# Hapus documentation yang sudah tidak relevan
rm ANALISIS_MASALAH.md

# Hapus git files (opsional)
rm .gitattributes .gitignore
```

---

## ⚠️ PERHATIAN:
- Backup dulu sebelum menghapus
- Pastikan `gui.py` adalah versi yang sudah final dan working
- File `requirements.txt` harus dicek apakah sudah sesuai dengan dependencies yang dibutuhkan
