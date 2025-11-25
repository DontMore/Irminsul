import pyautogui
import os
from datetime import datetime

# Folder tempat menyimpan screenshot
SAVE_DIR = "images"

# Buat folder jika belum ada
os.makedirs(SAVE_DIR, exist_ok=True)

# Nama file berdasarkan waktu
filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
filepath = os.path.join(SAVE_DIR, filename)

# Ambil screenshot
shot = pyautogui.screenshot()

# Simpan
shot.save(filepath)

print("Screenshot saved to:", filepath)
