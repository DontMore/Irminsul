"""
OCR Processing Module / Modul Pemrosesan OCR
==============================================
Handles OCR processing, threading, and related UI updates.
"""

import threading
import time
from tkinter import messagebox

from ocr_worker import run_ocr


class OCRProcessing:
    """
    Manages OCR processing, threading, and UI state during OCR operations.
    Mengelola pemrosesan OCR, threading, dan state UI selama operasi OCR.
    """
    
    def __init__(self, ocr_tab, root):
        """
        Initialize OCR Processing handler.
        
        Args:
            ocr_tab: OCRTab instance / Instansi OCRTab
            root: tkinter root window / Jendela root tkinter
        """
        self.ocr_tab = ocr_tab
        self.root = root
        self.current_template_path = ""
        
        # OCR state variables / Variabel state OCR
        self._ocr_running = False
        self._ocr_start_time = None
        self._loading_dots = 0
        self._ocr_timer_job = None
        self._ocr_anim_job = None
    
    def set_current_template(self, template_path):
        """
        Set the current template path for OCR processing.
        Atur path template saat ini untuk pemrosesan OCR.
        
        Args:
            template_path: Path to the template file / Path ke file template
        """
        self.current_template_path = template_path
    
    def _update_ocr_timer(self):
        """
        Update the elapsed time display during OCR processing.
        Perbarui tampilan waktu yang telah berlalu selama pemrosesan OCR.
        """
        if not self._ocr_running:
            return
        
        elapsed = int(time.time() - (self._ocr_start_time or time.time()))
        mins, secs = divmod(elapsed, 60)
        self.ocr_tab.ocr_timer_label.config(text=f"Waktu: {mins:02d}:{secs:02d}")
        
        # Schedule next update / Jadwalkan pembaruan berikutnya
        self._ocr_timer_job = self.root.after(1000, self._update_ocr_timer)

    def _animate_ocr_loading(self):
        """
        Animate loading indicator during OCR processing.
        Animasi indikator loading selama pemrosesan OCR.
        """
        if not self._ocr_running:
            self.ocr_tab.ocr_loading_label.config(text="")
            return
        
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = '.' * self._loading_dots
        self.ocr_tab.ocr_loading_label.config(text=f"Status: Running{dots}")
        
        # Schedule next animation frame / Jadwalkan frame animasi berikutnya
        self._ocr_anim_job = self.root.after(500, self._animate_ocr_loading)

    def _stop_ocr_ui(self):
        """
        Stop OCR processing UI indicators and re-enable controls.
        Hentikan indikator UI pemrosesan OCR dan aktifkan kembali kontrol.
        """
        self._ocr_running = False
        
        # Cancel timer / Batalkan timer
        try:
            if self._ocr_timer_job:
                self.root.after_cancel(self._ocr_timer_job)
        except Exception:
            pass
        
        # Cancel animation / Batalkan animasi
        try:
            if self._ocr_anim_job:
                self.root.after_cancel(self._ocr_anim_job)
        except Exception:
            pass
        
        # Re-enable controls / Aktifkan kembali kontrol
        try:
            self.ocr_tab.template_btn.config(state='normal')
            self.ocr_tab.input_btn.config(state='normal')
            try:
                self.ocr_tab.input_file_btn.config(state='normal')
            except Exception:
                pass
            self.ocr_tab.output_btn.config(state='normal')
            self.ocr_tab.start_btn.config(state='normal')
        except Exception:
            pass

    def _ocr_worker(self):
        """
        Worker thread for OCR processing.
        Thread worker untuk pemrosesan OCR.
        
        This runs in a separate thread to avoid blocking the UI.
        Ini berjalan di thread terpisah untuk menghindari pemblokiran UI.
        """
        try:
            # Determine input source / Tentukan sumber input
            mode = self.ocr_tab.input_mode_var.get()
            
            if mode == "folder":
                input_path = self.ocr_tab.input_folder_path
                is_batch = True
            else:
                input_path = self.ocr_tab.input_file_path
                is_batch = False
            
            # Get output folder / Dapatkan folder output
            output_path = self.ocr_tab.output_folder_path
            
            # Get export format / Dapatkan format export
            export_format = self.ocr_tab.export_format_var.get()
            
            # Log start / Catat awal
            self.ocr_tab.log.insert('end', f"🚀 Memulai pemrosesan OCR...\n")
            self.ocr_tab.log.insert('end', f"📄 Template: {self.current_template_path}\n")
            self.ocr_tab.log.insert('end', f"📁 Input: {input_path}\n")
            self.ocr_tab.log.insert('end', f"📁 Output: {output_path}\n")
            self.ocr_tab.log.insert('end', f"📊 Format: {export_format}\n")
            self.ocr_tab.log.insert('end', "=" * 50 + "\n")
            self.ocr_tab.log.see('end')
            
            # Run OCR processing / Jalankan pemrosesan OCR
            result = run_ocr(
                template_path=self.current_template_path,
                input_path=input_path,
                output_path=output_path,
                is_batch=is_batch,
                export_format=export_format,
                log_callback=self._log_ocr_message
            )
            
            # Log result / Catat hasil
            if result:
                self.ocr_tab.log.insert('end', "\n" + "=" * 50 + "\n")
                self.ocr_tab.log.insert('end', f"✅ Pemrosesan OCR selesai!\n")
                self.ocr_tab.log.insert('end', f"📁 Hasil tersimpan di: {output_path}\n")
                self.ocr_tab.log.see('end')
            else:
                self.ocr_tab.log.insert('end', "\n" + "=" * 50 + "\n")
                self.ocr_tab.log.insert('end', "❌ Pemrosesan OCR gagal.\n")
                self.ocr_tab.log.see('end')
        
        except Exception as e:
            self.ocr_tab.log.insert('end', f"\n❌ Error: {str(e)}\n")
            self.ocr_tab.log.see('end')
            print(f"OCR Error: {e}")
        
        finally:
            # Stop OCR UI / Hentikan UI OCR
            self._stop_ocr_ui()

    def _log_ocr_message(self, message):
        """
        Callback to log OCR processing messages.
        Callback untuk mencatat pesan pemrosesan OCR.
        
        Args:
            message: Message to log / Pesan untuk dicatat
        """
        try:
            self.ocr_tab.log.insert('end', f"{message}\n")
            self.ocr_tab.log.see('end')
        except Exception:
            pass

    def run_ocr(self):
        """
        Start OCR processing with selected options.
        Mulai pemrosesan OCR dengan opsi yang dipilih.
        
        This method:
        - Validates input parameters / Validasi parameter input
        - Disables UI controls during processing / Nonaktifkan kontrol UI selama pemrosesan
        - Starts background worker thread / Mulai thread worker latar belakang
        - Shows timer and loading indicator / Tampilkan timer dan indikator loading
        """
        # Validate template selection / Validasi pemilihan template
        if not self.current_template_path:
            messagebox.showerror(
                "❌ Error", 
                "Template belum dipilih. Buat template di tab Template Creator atau pilih template existing."
            )
            return

        # Validate input according to selected mode / Validasi input sesuai mode yang dipilih
        mode = self.ocr_tab.input_mode_var.get()
        
        if mode == "folder":
            if not self.ocr_tab.input_folder_path:
                messagebox.showerror(
                    "❌ Error", 
                    "Folder input belum dipilih untuk mode batch."
                )
                return
        else:
            if not self.ocr_tab.input_file_path:
                messagebox.showerror(
                    "❌ Error", 
                    "File input belum dipilih untuk mode single-file."
                )
                return

        # Validate output folder / Validasi folder output
        if not self.ocr_tab.output_folder_path:
            messagebox.showerror(
                "❌ Error",
                "Folder output belum dipilih."
            )
            return

        # Disable controls during processing / Nonaktifkan kontrol selama pemrosesan
        try:
            self.ocr_tab.template_btn.config(state='disabled')
            self.ocr_tab.input_btn.config(state='disabled')
            try:
                self.ocr_tab.input_file_btn.config(state='disabled')
            except Exception:
                pass
            self.ocr_tab.output_btn.config(state='disabled')
            self.ocr_tab.start_btn.config(state='disabled')
        except Exception:
            pass

        # Initialize timer/animation state / Inisialisasi state timer/animasi
        self._ocr_running = True
        self._ocr_start_time = time.time()
        self._loading_dots = 0

        # Start UI timers / Mulai timer UI
        self._update_ocr_timer()
        self._animate_ocr_loading()

        # Start worker thread / Mulai thread worker
        thread = threading.Thread(target=self._ocr_worker, daemon=True)
        thread.start()
