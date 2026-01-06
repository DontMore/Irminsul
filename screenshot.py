
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk, ImageGrab
import pyautogui
import os
from datetime import datetime
import time
import subprocess
import sys

class ScreenshotMiniGUI:
    def __init__(self, root, callback=None, save_dir="screenshots", hotkey=None):
        self.root = root
        self.callback = callback
        self.save_dir = save_dir
        self.hotkey = hotkey
        self.root.title("Mini Screenshot")
        self.root.geometry("250x300")
        self.root.resizable(False, False)

        # Keep the window on top so user can reuse it easily
        try:
            self.root.attributes('-topmost', True)
        except Exception:
            pass

        # Ensure the save directory exists
        os.makedirs(self.save_dir, exist_ok=True)

        self.btn = Button(root, text="Capture", command=self.take_screenshot,
                          font=("Arial", 12), width=12)
        self.btn.pack(pady=10)

        self.preview_label = Label(root, text="(Preview akan muncul di sini)", fg="gray")
        self.preview_label.pack(pady=10)

        # Status label to show save notification without modal dialogs
        self.status_label = Label(root, text="", fg="#10b981")
        self.status_label.pack(pady=(6, 0))

        # Hotkey label
        self.hotkey_label = Label(root, text=(f"Hotkey: {self.hotkey}" if self.hotkey else "Hotkey: -"), fg="gray")
        self.hotkey_label.pack(pady=(4, 0))

        # Keep the window on top so user can reuse it easily
        try:
            self.root.attributes('-topmost', True)
            # remove topmost after a moment so it doesn't block user
            # self.root.after(800, lambda: self.root.attributes('-topmost', False))
            pass
        except Exception:
            pass
        
        # Close button to allow user to close mini GUI when finished
        try:
            self.close_btn = Button(root, text="Close", command=self.root.destroy, font=("Arial", 10), width=10)
            self.close_btn.pack(pady=(8, 6))
        except Exception:
            pass

        # Try to register global hotkey if provided. Fall back to Tk binding when global not available.
        if self.hotkey:
            try:
                import keyboard

                # Register global hotkey -> schedule screenshot on main thread
                try:
                    keyboard.add_hotkey(self.hotkey, lambda: self.root.after(0, self.take_screenshot))
                    self.hotkey_label.config(fg="#10b981")
                except Exception as e:
                    print(f"Failed to register global hotkey with keyboard: {e}")
                    # fallback to Tk binding
                    try:
                        tk_binding = self.hotkey if self.hotkey.startswith("<") else f"<{self.hotkey}>"
                        self.root.bind_all(tk_binding, lambda e: self.take_screenshot())
                        self.hotkey_label.config(fg="#10b981")
                    except Exception:
                        self.hotkey_label.config(fg="#ef4444")
            except Exception:
                # keyboard module unavailable; try Tk binding syntax
                try:
                    tk_binding = self.hotkey if self.hotkey.startswith("<") else f"<{self.hotkey}>"
                    self.root.bind_all(tk_binding, lambda e: self.take_screenshot())
                    self.hotkey_label.config(fg="#10b981")
                except Exception as e:
                    print(f"Tkinter bind for hotkey failed: {e}")
                    self.hotkey_label.config(fg="#ef4444")

        # Tambahkan di __init__
        self.pin_var = tk.BooleanVar(value=True)  # default: pinned

        # Tambahkan tombol pin/unpin
        self.pin_btn = Button(root, text="📌 Pin", command=self.toggle_pin, font=("Arial", 8), width=6)
        self.pin_btn.pack(pady=(4, 0))

    def toggle_pin(self):
        current = self.pin_var.get()
        self.pin_var.set(not current)
        self.root.attributes('-topmost', self.pin_var.get())
        # Perbarui teks tombol
        if self.pin_var.get():
            self.pin_btn.config(text="📌 Pin")
        else:
            self.pin_btn.config(text="🔓 Unpin")

    def take_screenshot(self):
        # Sembunyikan sementara (tanpa mengubah topmost) → jendela akan tetap di atas setelah muncul
        self.root.withdraw()
        time.sleep(0.3)

        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(self.save_dir, filename)

        try:
            # Method 1: Try pyautogui.screenshot() (primary method)
            screenshot = self._take_screenshot_pyautogui()
            
            if screenshot is None:
                # Method 2: Try PIL ImageGrab as fallback
                screenshot = self._take_screenshot_imagegrab()
                
            if screenshot is None:
                # Method 3: Try subprocess with scrot/gnome-screenshot
                screenshot = self._take_screenshot_subprocess()
                
            if screenshot is None:
                # All methods failed - show user-friendly error
                self.root.deiconify()
                self._show_screenshot_error()
                return

            # Save and display screenshot
            screenshot.save(path)
            self.root.deiconify()
            
            # Create preview
            preview = screenshot.resize((200, 120))
            preview = ImageTk.PhotoImage(preview)
            
            self.preview_label.config(image=preview, text="")
            self.preview_label.image = preview
            
            print("Saved:", path)
            
            # Send path to main GUI
            if self.callback:
                self.callback(path)
                
            # Show non-blocking notification
            try:
                self.status_label.config(text=f"Tersimpan: {os.path.basename(path)}", fg="#10b981")
                self.root.after(2500, lambda: self.status_label.config(text="", fg="#10b981"))
            except Exception:
                pass
                
        except Exception as e:
            self.root.deiconify()
            # Pastikan jendela tetap di atas setelah muncul kembali
            self.root.attributes('-topmost', True)
            print(f"Screenshot error: {e}")
            self._show_screenshot_error(str(e))

    def _take_screenshot_pyautogui(self):
        """Try to take screenshot using pyautogui"""
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"PyAutoGUI screenshot failed: {e}")
            return None

    def _take_screenshot_imagegrab(self):
        """Try to take screenshot using PIL ImageGrab (no system dependencies)"""
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"ImageGrab screenshot failed: {e}")
            return None

    def _take_screenshot_subprocess(self):
        """Try to take screenshot using system commands"""
        methods = [
            # Try scrot first (lightweight, doesn't require gnome)
            ["scrot", "/tmp/screenshot_temp.png"],
            # Try gnome-screenshot
            ["gnome-screenshot", "-f", "/tmp/screenshot_temp.png"],
            # Try flameshot
            ["flameshot", "full", "-p", "/tmp/screenshot_temp.png"],
            # Try spectacle (KDE)
            ["spectacle", "-b", "-o", "/tmp/screenshot_temp.png"]
        ]
        
        for method in methods:
            try:
                cmd = method
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and os.path.exists("/tmp/screenshot_temp.png"):
                    # Load the screenshot
                    screenshot = Image.open("/tmp/screenshot_temp.png")
                    # Clean up temporary file
                    os.remove("/tmp/screenshot_temp.png")
                    return screenshot
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                print(f"Subprocess method {method[0]} failed: {e}")
                continue
        
        return None

    def _show_screenshot_error(self, error_msg=None):
        """Show error message using status label instead of messagebox"""
        error_details = error_msg or "Unknown error"
        
        print(f"Screenshot failed: {error_details}")
        
        # Update status label
        try:
            self.status_label.config(text="Screenshot gagal", fg="#ef4444")
            self.root.after(3500, lambda: self.status_label.config(text="", fg="#10b981"))
        except Exception:
            pass

