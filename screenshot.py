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
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
        self.root.title("Mini Screenshot")
        self.root.geometry("250x300")
        self.root.resizable(False, False)

        self.btn = Button(root, text="Capture", command=self.take_screenshot,
                          font=("Arial", 12), width=12)
        self.btn.pack(pady=10)

        self.preview_label = Label(root, text="(Preview akan muncul di sini)", fg="gray")
        self.preview_label.pack(pady=10)

    def take_screenshot(self):
        self.root.withdraw()
        time.sleep(0.3)

        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(SAVE_DIR, filename)

        screenshot = pyautogui.screenshot()
        screenshot.save(path)

        self.root.deiconify()

        preview = screenshot.resize((200, 120))
        preview = ImageTk.PhotoImage(preview)

        self.preview_label.config(image=preview, text="")
        self.preview_label.image = preview

        print("Saved:", path)

        # ⬇️ kirim path ke GUI utama
        if self.callback:
            self.callback(path)
