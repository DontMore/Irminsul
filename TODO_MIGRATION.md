# Rencana Migrasi dan Perbaikan GUI

## Informasi yang Dikumpulkan:
- gui_modern.py berisi kode modern lengkap dengan class ModernOCRGui
- gui.py saat ini hampir kosong, hanya beberapa import
- Dependencies utama: tkinter, PIL, cv2, pytesseract, modern_styles, screenshot

## Plan Migrasi:
1. **Backup gui.py existing** (jika ada konten penting)
2. **Salin seluruh kode dari gui_modern.py ke gui.py**
3. **Tambahkan fitur pengaturan folder output screenshot:**
   - Tambahkan entry field untuk path folder output
   - Tambahkan tombol "Browse" untuk memilih folder
   - Modifikasi screenshot saving logic
   - Update default folder path handling

## Files yang akan diedit:
- gui.py (target utama)

## Fitur Baru yang Ditambahkan:
- Folder output picker untuk screenshot
- Validasi folder path
- Default folder settings
- Updated screenshot saving mechanism

## Testing yang diperlukan:
- Verify UI still works correctly
- Test folder selection functionality  
- Test screenshot saving to custom folder
- Verify OCR process still works




## Steps:
1. [x] Backup existing gui.py
2. [x] Copy entire gui_modern.py content to gui.py
3. [x] Add folder selection UI components
4. [x] Modify screenshot saving logic
5. [x] Add folder validation
6. [x] Test functionality
