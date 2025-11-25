import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import pyautogui
import os
from datetime import datetime
import time

SAVE_DIR = "screenshots"
os.makedirs(SAVE_DIR, exist_ok=True)

class ScreenshotMiniGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Screenshot")
        self.root.geometry("250x300")
        self.root.resizable(False, False)

        # Button Screenshot
        self.btn = Button(root, text="Capture", command=self.take_screenshot, 
                          font=("Arial", 12), width=12)
        self.btn.pack(pady=10)

        # Label preview kecil
        self.preview_label = Label(root, text="(Preview akan muncul di sini)", fg="gray")
        self.preview_label.pack(pady=10)

    def take_screenshot(self):
        # Sembunyikan window agar tidak terscreenshot
        self.root.withdraw()
        time.sleep(0.3)

        # Buat filename
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(SAVE_DIR, filename)

        # Screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(path)

        # Tampilkan kembali GUI
        self.root.deiconify()

        # Resize preview lebih kecil
        preview = screenshot.resize((200, 120))
        preview = ImageTk.PhotoImage(preview)

        # Update label preview
        self.preview_label.config(image=preview, text="")
        self.preview_label.image = preview

        print("Saved:", path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotMiniGUI(root)
    root.mainloop()
