<<<<<<< HEAD
# TODO: Penggabungan GUI.py dan Template.py

## Status: Dalam Progress

## Informasi yang Dikumpulkan:
- `gui.py`: OCRGui class dengan fitur screenshot, pilih template, dan jalankan OCR via Docker
- `template.py`: TemplateGUI class dengan fitur drag & select area untuk membuat template JSON
- Kedua aplikasi menggunakan tkinter dan perlu digabungkan dalam satu interface

## Plan: Penggabungan dengan Tab-Based Interface
1. **Integrasi TemplateGUI ke OCRGui** - Menambahkan TemplateGUI functionality ke dalam OCRGui
2. **Membuat Tab Interface** - Menggunakan tkinter Notebook untuk 3 tab: Screenshot, Template Creator, OCR Process
3. **Update Requirements** - Menambahkan dependencies yang diperlukan
4. **Testing & Validation** - Memastikan semua fitur terintegrasi dengan baik

## Dependent Files to be Edited:
- `gui.py` - Mengintegrasikan TemplateGUI dan membuat tab interface
- `requirements.txt` - Menambahkan dependencies (cv2, pytesseract, PIL)

## Followup Steps:
1. Install dependencies baru jika diperlukan
2. Test semua fitur terintegrasi
3. Validasi workflow dari template creation hingga OCR processing

## Steps Completed:
- [x] Analisis file existing (gui.py dan template.py)
- [x] Buat plan penggabungan
- [x] Buat TODO.md untuk tracking


## Next Steps:
- [x] Implementasi tab-based interface di gui.py
- [x] Integrasi TemplateGUI class
- [x] Update requirements.txt
- [ ] Testing integrasi
=======
- [x] Add OCR imports (cv2, pytesseract) to template.py
- [x] Set pytesseract path for Windows
- [x] Add "Preview Extractions" button to the GUI
- [x] Implement preview_extractions method to perform OCR on selected areas and display in a popup
- [x] Test the preview functionality
- [x] Change preview display to sidebar instead of popup
>>>>>>> origin/main
