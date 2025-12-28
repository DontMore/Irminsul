# Irminsul - Modern OCR Template Extractor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](dockerfile)

**Irminsul** is a modern OCR (Optical Character Recognition) application with a user-friendly interface for text extraction from images using customizable templates. The application supports batch processing and can run in Docker containers for environment consistency.

## 🎯 Key Features

### 🔍 OCR Engine
- **Tesseract Integration**: Text extraction using Tesseract OCR engine
- **Multi-language Support**: Supports English and Indonesian languages (`eng+ind`)
- **Template-based**: Uses JSON templates for precise extraction areas
- **Batch Processing**: Processes multiple images simultaneously

### 📐 Template Creator
- **Visual Template Designer**: Create templates with drag & drop interface
- **Real-time Preview**: Real-time text extraction preview
- **Field Management**: Manage multiple field extraction easily
- **JSON Export**: Export templates to JSON format for reusability

### 📸 Screenshot Tools
- **Interactive Screenshot**: Screenshot with overlay for selection
- **Custom Output Directory**: Choose output folder according to needs
- **Multiple Format Support**: PNG, JPG, JPEG support

### 🎨 Modern GUI
- **Tkinter-based Interface**: Modern interface with tkinter
- **Responsive Design**: Responsive and user-friendly layout
- **Tabbed Interface**: Organize workflow with tab interface
- **Real-time Logging**: Real-time activity and progress logging

### 🐳 Docker Support
- **Containerized OCR**: Run OCR in consistent environment
- **Volume Mounting**: Mount directory for input/output files
- **Cross-platform**: Runs on Windows, macOS, and Linux

## 📋 System Requirements

### Python Dependencies
```
opencv-python-headless
pandas
numpy
Pillow
tkinter
```

### System Dependencies
- **Python**: 3.8 or newer
- **Tesseract OCR**: Must be installed on system
- **Docker**: (Optional) for containerized version

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
1. Download Tesseract from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Install language packs (eng, ind)

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Irminsul
```

### 2. Setup Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Tesseract
Make sure Tesseract is installed and accessible from command line:
```bash
tesseract --version
```

### 5. Build Docker Image (Optional)
```bash
docker build -t ocr-app .
```

## 📖 Usage

### Running GUI
```bash
python gui_modern.py
```

### Command Line Interface
```bash
python extract.py template.json /path/to/image/folder
```

### Operational Modes

#### 1. Screenshot Mode
1. Open "📸 Screenshot" tab
2. Select output folder
3. Click "🎯 Take Screenshot"
4. Select area for screenshot

#### 2. Template Creator Mode
1. Open "📐 Template Creator" tab
2. Click "📁 Open Image"
3. Drag to select extraction area
4. Click "💾 Save Template" to save

#### 3. OCR Process Mode
1. Open "🔍 OCR Process" tab
2. Select JSON template
3. Click "🚀 Start OCR"
4. View results in `hasil_ocr.csv`

## 📁 Project Structure

```
Irminsul/
├── gui_modern.py          # Modern GUI application
├── extract.py             # Core OCR functionality
├── screenshot.py          # Screenshot tools
├── template.py            # Template management
├── modern_styles.py       # GUI styling
├── dockerfile            # Docker container definition
├── requirements.txt      # template.json         # Python dependencies
├── Template example
└── README.md            # Documentation
```

## 🎛️ Template Configuration

Templates use JSON format with the following structure:

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

### Field Parameters
- **name**: Unique identifier for field
- **x, y**: Pixel coordinates of top-left corner
- **w, h**: Width and height of extraction area (pixels)

## 🐳 Docker Usage

### Build Image
```bash
docker build -t ocr-app .
```

### Run OCR with Docker
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

OCR generates CSV file with columns:
- **filename**: Image file name
- **field_name**: Extraction value for each field

Example CSV output:
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

#### 4. Memory Issues with Large Images
- Reduce image size before processing
- Increase system memory/virtual memory
- Process images in smaller batches

### Debug Mode
Add logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 Development Notes

### Modern GUI Features
- **Tabbed Interface**: Screenshot, Template Creator, OCR Process
- **Real-time Preview**: Live OCR preview
- **Zoom Controls**: Zoom in/out for detailed selection
- **Mini-map**: Overview of image with field highlights
- **Field Statistics**: Real-time field analysis

### Performance Optimizations
- **Lazy Loading**: Load images only when needed
- **Efficient OCR**: Batch processing for multiple images
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

For support and questions:
1. Open [Issues](../../issues) for bug reports
2. Read [Troubleshooting](#-troubleshooting) section
3. Check [Documentation](#-usage) for usage examples

---

**Irminsul** - Making OCR accessible, one template at a time! 🎯
