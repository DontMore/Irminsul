# Irminsul - Modern OCR Template Extractor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](dockerfile)

**Irminsul** adalah aplikasi OCR (Optical Character Recognition) modern dengan antarmuka yang user-friendly untuk ekstraksi teks dari gambar menggunakan template yang dapat disesuaikan. Aplikasi ini mendukung batch processing dan dapat dijalankan dalam container Docker untuk konsistensi lingkungan.

## 🎯 Fitur Utama

### 🔍 OCR Engine
- **Tesseract Integration**: Ekstraksi teks menggunakan Tesseract OCR engine
- **Multi-language Support**: Mendukung bahasa Inggris dan Indonesia (`eng+ind`)
- **Template-based**: Menggunakan template JSON untuk area ekstraksi yang presisi
- **Batch Processing**: Memproses multiple gambar sekaligus

### 📐 Template Creator
- **Visual Template Designer**: Buat template dengan drag & drop interface
- **Real-time Preview**: Preview ekstraksi teks secara real-time
- **Field Management**: Kelola multiple field extraction dengan mudah
- **JSON Export**: Eksport template ke format JSON untuk reusability

### 📸 Screenshot Tools
- **Interactive Screenshot**: Screenshot dengan overlay untuk selection
- **Custom Output Directory**: Pilih folder output sesuai kebutuhan
- **Multiple Format Support**: PNG, JPG, JPEG support

### 🎨 Modern GUI
- **Tkinter-based Interface**: Interface modern dengan tkinter
- **Responsive Design**: Layout yang responsif dan user-friendly
- **Tabbed Interface**: Organisir workflow dengan tab interface
- **Real-time Logging**: Log aktivitas dan progress secara real-time

### 🐳 Docker Support
- **Containerized OCR**: Jalankan OCR dalam environment yang konsisten
- **Volume Mounting**: Mount directory untuk input/output files
- **Cross-platform**: Berjalan di Windows, macOS, dan Linux

## 📋 Persyaratan Sistem

### Python Dependencies
```
opencv-python-headless
pandas
numpy
Pillow
tkinter
```

### System Dependencies
- **Python**: 3.8 atau lebih baru
- **Tesseract OCR**: Harus terinstall di sistem
- **Docker**: (Opsional) untuk containerized version

### Install Tesseract

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-ind
```

#### macOS
```bash
brew install tesseract
```

#### Windows
1. Download Tesseract dari [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install dan tambahkan ke PATH
3. Install language packs (eng, ind)

## 🚀 Instalasi & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Irminsul
```

### 2. Setup Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Tesseract
Pastikan Tesseract terinstall dan dapat diakses dari command line:
```bash
tesseract --version
```

### 5. Build Docker Image (Opsional)
```bash
docker build -t ocr-app .
```

## 📖 Penggunaan

### Menjalankan GUI
```bash
python gui_modern.py
```

### Command Line Interface
```bash
python extract.py template.json /path/to/image/folder
```

### Mode Operasional

#### 1. Screenshot Mode
1. Buka tab "📸 Screenshot"
2. Pilih output folder
3. Klik "🎯 Take Screenshot"
4. Select area untuk screenshot

#### 2. Template Creator Mode
1. Buka tab "📐 Template Creator"
2. Klik "📁 Open Image"
3. Drag untuk select area ekstraksi
4. Klik "💾 Save Template" untuk menyimpan

#### 3. OCR Process Mode
1. Buka tab "🔍 OCR Process"
2. Pilih template JSON
3. Klik "🚀 Mulai OCR"
4. Lihat hasil di `hasil_ocr.csv`

## 📁 Struktur Project

```
Irminsul/
├── gui_modern.py          # Modern GUI application
├── extract.py             # Core OCR functionality
├── screenshot.py          # Screenshot tools
├── template.py            # Template management
├── modern_styles.py       # GUI styling
├── dockerfile            # Docker container definition
├── requirements.txt      # Python dependencies
├── template.json         # Template example
└── README.md            # Documentation
```

## 🎛️ Konfigurasi Template

Template menggunakan format JSON dengan struktur berikut:

```json
{
  "fields": [
    {
      "name": "field_name",
      "x": 100,
      "y": 200,
      "w": 150,
      "h": 30
    }
  ]
}
```

### Parameter Field
- **name**: Identifier unik untuk field
- **x, y**: Koordinat pixel左上角
- **w, h**: Lebar dan tinggi area ekstraksi (pixels)

## 🐳 Docker Usage

### Build Image
```bash
docker build -t ocr-app .
```

### Run OCR dengan Docker
```bash
docker run --rm \
  -v /path/to/data:/data \
  ocr-app \
  /data/template.json \
  /data/input_images \
  /data/output
```

### Docker GUI (Experimental)
```bash
docker run --rm -it \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  ocr-app \
  python gui_modern.py
```

## 📊 Output Format

OCR menghasilkan file CSV dengan kolom:
- **filename**: Nama file gambar
- **field_name**: Nilai ekstraksi untuk setiap field

Contoh output CSV:
```csv
filename,field_1,field_2,field_3
image1.png,Text Content,123.45,Data
image2.png,Other Text,678.90,More Data
```

## 🧪 Testing

### Unit Tests
```bash
python test_ocr.py
python test_image_display.py
python test_gui_image_display.py
```

### GUI Testing
```bash
python test_image_display.py
python test_gui_image_display.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```bash
# Check installation
tesseract --version

# Add to PATH (Linux/macOS)
export PATH=$PATH:/usr/local/bin

# Windows: Add to system PATH
```

#### 2. Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart session or run:
newgrp docker
```

#### 3. GUI Display Issues (Linux)
```bash
# For WSL or headless environments
export DISPLAY=:0

# Install X server (WSL)
sudo apt-get install xfce4-terminal
```

#### 4. Memory Issues dengan Large Images
- Reduce image size sebelum processing
- Increase system memory/virtual memory
- Process images in smaller batches

### Debug Mode
Tambahkan logging untuk debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Buka Pull Request

## 📝 Development Notes

### Modern GUI Features
- **Tabbed Interface**: Screenshot, Template Creator, OCR Process
- **Real-time Preview**: Live OCR preview
- **Zoom Controls**: Zoom in/out untuk detailed selection
- **Mini-map**: Overview of image dengan field highlights
- **Field Statistics**: Real-time field analysis

### Performance Optimizations
- **Lazy Loading**: Load images only when needed
- **Efficient OCR**: Batch processing untuk multiple images
- **Memory Management**: Proper cleanup of image resources
- **Responsive UI**: Non-blocking operations

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [OpenCV](https://opencv.org/) - Computer vision library
- [Pillow](https://pillow.readthedocs.io/) - Python imaging library
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [NumPy](https://numpy.org/) - Numerical computing

## 📞 Support

Untuk support dan вопросы:
1. Buka [Issues](../../issues) untuk bug reports
2. Baca [Troubleshooting](#-troubleshooting) section
3. Check [Documentation](#-penggunaan) untuk usage examples

---

**Irminsul** - Making OCR accessible, one template at a time! 🎯
