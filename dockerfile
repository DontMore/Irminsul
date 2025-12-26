FROM python:3.10-slim

# Install system dependencies for GUI and OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    python3-tk \
    xvfb \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy GUI application
COPY gui.py .
COPY modern_styles.py .
COPY enhanced_ocr.py .
COPY screenshot.py .

# Set entrypoint for GUI app with virtual display
ENTRYPOINT ["xvfb-run", "-a", "python", "gui.py"]
