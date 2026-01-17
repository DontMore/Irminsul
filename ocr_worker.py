"""Background OCR / Docker worker functions.

This module keeps heavy I/O and external calls out of UI modules. It exposes
`run_ocr` which is safe to call from a background thread and reports
progress via callbacks supplied by the caller.
"""
import subprocess
import os


def run_ocr(template_path, input_path, output_dir, export_format, progress_cb=None, done_cb=None):
    """Run OCR (docker) and optionally convert CSV→Excel.

    Arguments:
        template_path (str): path to JSON template (host path)
        input_path (str): input folder or file path
        output_dir (str): where outputs are expected (used for locating result files)
        export_format (str): 'CSV' or 'Excel'
        progress_cb (callable): progress callback receiving one string argument
        done_cb (callable): completion callback receiving (success: bool, message: str)
    """
    def p(msg):
        if callable(progress_cb):
            try:
                progress_cb(msg)
            except Exception:
                pass

    def done(success, message):
        if callable(done_cb):
            try:
                done_cb(success, message)
            except Exception:
                pass

    try:
        p("🚀 Menjalankan OCR di Docker...")

        template_dir = os.path.dirname(template_path) or "."
        # Determine if input is a folder or file
        if os.path.isdir(input_path):
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{template_dir}:/data",
                "-v", f"{input_path}:/input",
                "ocr-app",
                "/data/" + os.path.basename(template_path),
                "/input",
            ]
        else:
            file_dir = os.path.dirname(input_path) or "."
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{template_dir}:/data",
                "-v", f"{file_dir}:/input",
                "ocr-app",
                "/data/" + os.path.basename(template_path),
                "/input/" + os.path.basename(input_path),
            ]

        p("🔗 Command: " + " ".join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            p("❌ Docker process failed")
            done(False, result.stderr or "Docker run failed")
            return

        p("✅ Docker run completed")

        # Post-process: convert CSV to Excel if requested
        csv_path = os.path.join(template_dir, "hasil_ocr.csv")
        if export_format == "Excel" and os.path.exists(csv_path):
            try:
                p("🔁 Converting CSV to Excel...")
                import pandas as pd
                df = pd.read_csv(csv_path)
                excel_path = os.path.join(template_dir, "hasil_ocr.xlsx")
                df.to_excel(excel_path, index=False)
                p("✅ Conversion complete: hasil_ocr.xlsx")
                done(True, f"OCR completed, Excel saved: {excel_path}")
                return
            except Exception as e:
                p(f"⚠️ Conversion failed: {e}")
                done(True, f"OCR completed (CSV saved), but Excel conversion failed: {e}")
                return

        # Default: success with CSV
        p("✅ Selesai! Hasil OCR tersimpan di hasil_ocr.csv")
        done(True, f"OCR completed, CSV saved: {csv_path}")

    except FileNotFoundError:
        done(False, "Docker not found on PATH")
    except Exception as e:
        done(False, str(e))
