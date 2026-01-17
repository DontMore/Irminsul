"""
GUI Launcher for Modern OCR Application
Peluncur GUI untuk Aplikasi OCR Modern
========================================

Module Description / Deskripsi Modul:
This module serves as the main entry point for the Modern OCR GUI application.
It is a lightweight launcher that initializes the tkinter environment and
starts the main application by importing the ModernOCRGui class from main_gui.py.

Modul ini berfungsi sebagai titik masuk utama untuk aplikasi GUI OCR Modern.
Ini adalah peluncur ringan yang menginisialisasi lingkungan tkinter dan
memulai aplikasi utama dengan mengimpor kelas ModernOCRGui dari main_gui.py.

Design Notes / Catatan Desain:
- The original large gui.py was refactored into multiple files for better maintainability
- gui.py now only contains the startup logic
- main_gui.py contains the main GUI implementation
- template_gui.py contains template creation functionality

- gui.py asli yang besar di-refactor menjadi beberapa file untuk maintainability yang lebih baik
- gui.py sekarang hanya berisi logika startup
- main_gui.py berisi implementasi GUI utama
- template_gui.py berisi fungsionalitas pembuatan template

Author: [Your Name]
Version: 1.0.0
Last Updated: 2024
"""

# ============================================================================
# IMPORT SECTION / BAGIAN IMPOR
# ============================================================================

# Import tkinter module / Mengimpor modul tkinter
# Tkinter is Python's standard GUI library / Tkinter adalah library GUI standar Python
import tkinter as tk

# Import main GUI class from main_gui module / Mengimpor kelas GUI utama dari modul main_gui
# This class contains all the GUI logic and UI components / Kelas ini berisi semua logika GUI dan komponen UI
from main_gui import ModernOCRGui


# ============================================================================
# MAIN FUNCTION / FUNGSI UTAMA
# ============================================================================

def main():
    """
    Main entry point for the Modern OCR GUI application
    Titik masuk utama untuk aplikasi GUI OCR Modern
    
    This function performs the following steps:
    1. Creates the main tkinter root window (the application's main window)
    2. Initializes the ModernOCRGui application with the root window
    3. Starts the tkinter main event loop (keeps the application running)
    
    Fungsi ini melakukan langkah-langkah berikut:
    1. Membuat jendela root tkinter utama (jendela utama aplikasi)
    2. Menginisialisasi aplikasi ModernOCRGui dengan jendela root
    3. Memulai main event loop tkinter (menjaga aplikasi tetap berjalan)
    
    Process Flow / Alur Proses:
    ┌─────────────────────────────────────┐
    │         tk.Tk()                     │  Create root window / Buat jendela root
    │              ↓                      │
    │   ModernOCRGui(root)                │  Initialize GUI / Inisialisasi GUI
    │              ↓                      │
    │      root.mainloop()                │  Start event loop / Mulai event loop
    └─────────────────────────────────────┘
    """
    # Step 1: Create the main application window / Langkah 1: Buat jendela aplikasi utama
    # The root window is the top-level window that contains all other widgets
    # Jendela root adalah jendela tingkat atas yang berisi semua widget lainnya
    root = tk.Tk()
    
    # Step 2: Initialize the ModernOCRGui application / Langkah 2: Inisialisasi aplikasi ModernOCRGui
    # This creates all the GUI components and sets up the interface
    # Ini membuat semua komponen GUI dan mengatur antarmuka
    app = ModernOCRGui(root)
    
    # Step 3: Start the tkinter main event loop / Langkah 3: Mulai main event loop tkinter
    # This keeps the application running and responsive to user events
    # Ini menjaga aplikasi tetap berjalan dan responsif terhadap event pengguna
    root.mainloop()


# ============================================================================
# APPLICATION ENTRY POINT / TITIK MASUK APLIKASI
# ============================================================================

if __name__ == "__main__":
    """
    Main entry point guard / Penjaga titik masuk utama
    
    This conditional statement ensures that the main() function is only called
    when the script is run directly (not when imported as a module).
    
    Pernyataan kondisional ini memastikan bahwa fungsi main() hanya dipanggil
    ketika skrip dijalankan secara langsung (tidak ketika diimpor sebagai modul).
    
    How it works / Cara kerjanya:
    - __name__ is "__main__" when the script is run directly
    - __name__ is the module name when imported
    
    - __name__ adalah "__main__" ketika skrip dijalankan secara langsung
    - __name__ adalah nama modul ketika diimpor
    """
    main()
    
    # Alternative inline syntax (same as calling main()):
    # Sintaks alternatif sebaris (sama dengan memanggil main()):
    # tk.Tk(), ModernOCRGui(tk.Tk()).mainloop()

