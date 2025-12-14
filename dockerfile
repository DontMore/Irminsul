FROM python:3.10-slim

# Perbaiki typo: "tesseract-ocr"
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Salin dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin skrip utama
COPY extract.py .

# Jika ada file data Tesseract khusus, salin juga:
# COPY tessdata/ /usr/share/tesseract-ocr/4.00/tessdata/

ENTRYPOINT ["python", "extract.py"]