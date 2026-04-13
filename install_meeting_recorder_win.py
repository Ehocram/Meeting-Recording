#!/usr/bin/env python3
"""
Meeting Recorder — Installer per Windows
Installa automaticamente tutte le dipendenze e configura l'applicazione.
Sviluppato da Marco Bonometti
"""

import os
import sys
import subprocess
import shutil
import threading
import ctypes
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox

# ── Configurazione ──
APP_NAME = "Meeting Recorder"
VENV_DIR = Path.home() / "meeting-recorder-env"
APP_DIR = Path(__file__).parent.resolve()
ICON_EMOJI = "\U0001F3A4"

BASE_PACKAGES = [
    "PyQt6",
    "faster-whisper",
    "sounddevice",
    "numpy",
    "requests",
    "python-docx",
]

DIARIZATION_PACKAGES = [
    "pyannote.audio",
]

BUILD_PACKAGES = [
    "pyinstaller",
]


def is_admin():
    """Verifica se lo script gira come admin."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# ══════════════════════════════════════════
# INSTALLER GUI
# ══════════════════════════════════════════
class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Installer Windows")
        self.root.geometry("720x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#0F1117")

        # Variabili
        self.install_diarization = tk.BooleanVar(value=True)
        self.install_cuda = tk.BooleanVar(value=False)
        self.hf_token = tk.StringVar(value="")
        self.build_app = tk.BooleanVar(value=False)
        self.create_shortcut = tk.BooleanVar(value=True)

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        main = tk.Frame(self.root, bg="#0F1117")
        main.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Header ──
        tk.Label(main, text=f"{ICON_EMOJI}  {APP_NAME}", font=("Segoe UI", 20, "bold"),
                 bg="#0F1117", fg="#F1F5F9").pack(pady=(0, 2))
        tk.Label(main, text="Installer per Windows", font=("Segoe UI", 11),
                 bg="#0F1117", fg="#64748B").pack(pady=(0, 16))

        # ── Separator ──
        tk.Frame(main, height=1, bg="#2D3748").pack(fill="x", pady=(0, 16))

        # ── Opzioni ──
        tk.Label(main, text="Opzioni di installazione", font=("Segoe UI", 13, "bold"),
                 bg="#0F1117", fg="#60A5FA").pack(anchor="w", pady=(0, 10))

        # Checkbox diarization
        chk_diar = tk.Checkbutton(main, text="  Installa Speaker Diarization (pyannote.audio ~500 MB)",
                                   variable=self.install_diarization,
                                   bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                   activebackground="#0F1117", activeforeground="#E2E8F0",
                                   font=("Segoe UI", 11), command=self._toggle_hf_section)
        chk_diar.pack(anchor="w", pady=2)

        # HF Token frame
        self.hf_frame = tk.Frame(main, bg="#0F1117")
        self.hf_frame.pack(fill="x", pady=(4, 4), padx=(24, 0))
        tk.Label(self.hf_frame, text="HuggingFace Token:", font=("Segoe UI", 11),
                 bg="#0F1117", fg="#E2E8F0").pack(anchor="w")
        tk.Label(self.hf_frame, text="Crea un token Read su huggingface.co/settings/tokens",
                 font=("Segoe UI", 9), bg="#0F1117", fg="#64748B").pack(anchor="w")
        self.hf_entry = tk.Entry(self.hf_frame, textvariable=self.hf_token,
                                  bg="#1E293B", fg="#E2E8F0", insertbackground="#E2E8F0",
                                  font=("Consolas", 11), relief="flat", bd=6,
                                  highlightthickness=1, highlightcolor="#2563EB",
                                  highlightbackground="#334155")
        self.hf_entry.pack(fill="x", pady=(4, 0))

        # Checkbox CUDA
        self.chk_cuda = tk.Checkbutton(main,
                                        text="  Installa PyTorch con supporto CUDA (GPU NVIDIA)",
                                        variable=self.install_cuda,
                                        bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                        activebackground="#0F1117", activeforeground="#E2E8F0",
                                        font=("Segoe UI", 11))
        self.chk_cuda.pack(anchor="w", pady=2)

        # Checkbox collegamento desktop
        chk_short = tk.Checkbutton(main, text="  Crea collegamento sul Desktop",
                                    variable=self.create_shortcut,
                                    bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                    activebackground="#0F1117", activeforeground="#E2E8F0",
                                    font=("Segoe UI", 11))
        chk_short.pack(anchor="w", pady=2)

        # Checkbox build exe
        chk_build = tk.Checkbutton(main, text="  Compila in .exe standalone (PyInstaller)",
                                    variable=self.build_app,
                                    bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                    activebackground="#0F1117", activeforeground="#E2E8F0",
                                    font=("Segoe UI", 11))
        chk_build.pack(anchor="w", pady=(2, 12))

        # ── Progress ──
        tk.Label(main, text="Progresso", font=("Segoe UI", 13, "bold"),
                 bg="#0F1117", fg="#60A5FA").pack(anchor="w", pady=(8, 6))

        self.progress = ttk.Progressbar(main, mode="determinate", length=660)
        self.progress.pack(fill="x", pady=(0, 6))

        self.lbl_status = tk.Label(main, text="Pronto per l'installazione",
                                    font=("Segoe UI", 11), bg="#0F1117", fg="#94A3B8")
        self.lbl_status.pack(anchor="w")

        self.lbl_detail = tk.Label(main, text="", font=("Segoe UI", 9),
                                    bg="#0F1117", fg="#64748B", wraplength=640, justify="left")
        self.lbl_detail.pack(anchor="w", pady=(2, 12))

        # ── Pulsanti ──
        btn_frame = tk.Frame(main, bg="#0F1117")
        btn_frame.pack(fill="x", pady=(8, 0))

        self.btn_install = tk.Button(btn_frame, text="\u2B07  Installa tutto",
                                      command=self._start_install,
                                      bg="#2563EB", fg="white",
                                      activebackground="#1D4ED8", activeforeground="white",
                                      font=("Segoe UI", 13, "bold"),
                                      relief="flat", bd=0, padx=24, pady=10, cursor="hand2")
        self.btn_install.pack(side="left")

        self.btn_quit = tk.Button(btn_frame, text="Esci",
                                   command=self.root.quit,
                                   bg="#1E293B", fg="#CBD5E1",
                                   activebackground="#263548", activeforeground="#CBD5E1",
                                   font=("Segoe UI", 11),
                                   relief="flat", bd=0, padx=16, pady=8, cursor="hand2")
        self.btn_quit.pack(side="right")

    def _toggle_hf_section(self):
        if self.install_diarization.get():
            self.hf_frame.pack(fill="x", pady=(4, 4), padx=(24, 0))
            self.chk_cuda.pack(anchor="w", pady=2)
        else:
            self.hf_frame.pack_forget()
            self.chk_cuda.pack_forget()

    def _set_status(self, text, detail=""):
        self.lbl_status.config(text=text)
        self.lbl_detail.config(text=detail)
        self.root.update_idletasks()

    def _set_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def _run_cmd(self, cmd, desc="", timeout=900):
        """Esegue un comando e ritorna (success, output)."""
        self._set_status(desc, f"> {' '.join(str(c) for c in cmd[:4])}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0:
                return False, result.stderr
            return True, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Timeout: il comando ha impiegato troppo tempo."
        except Exception as e:
            return False, str(e)

    def _start_install(self):
        self.btn_install.config(state="disabled", bg="#374151")
        thread = threading.Thread(target=self._do_install, daemon=True)
        thread.start()

    def _do_install(self):
        total_steps = 5
        if self.install_diarization.get():
            total_steps += 2
            if self.install_cuda.get():
                total_steps += 1
        if self.create_shortcut.get():
            total_steps += 1
        if self.build_app.get():
            total_steps += 1
        step = 0

        def advance(desc, detail=""):
            nonlocal step
            step += 1
            pct = int(step / total_steps * 100)
            self._set_progress(pct)
            self._set_status(desc, detail)

        try:
            # ── Step 1: Verifica Python ──
            advance("Verifica Python...")
            python_exe = sys.executable
            python_ver = subprocess.run([python_exe, "--version"], capture_output=True, text=True)
            if python_ver.returncode != 0:
                self._fail("Python non trovato. Installa Python 3.11 da python.org e spunta 'Add to PATH'.")
                return
            ver = python_ver.stdout.strip()
            self._set_status(f"\u2705 {ver} trovato", python_exe)

            # ── Step 2: Crea virtual environment ──
            advance("Creazione virtual environment...", str(VENV_DIR))
            if not VENV_DIR.exists():
                ok, err = self._run_cmd([python_exe, "-m", "venv", str(VENV_DIR)],
                                         "Creazione virtual environment...")
                if not ok:
                    self._fail(f"Errore creazione venv:\n{err}")
                    return

            pip = str(VENV_DIR / "Scripts" / "pip.exe")
            python = str(VENV_DIR / "Scripts" / "python.exe")

            # Verifica che pip esista
            if not Path(pip).exists():
                self._fail(f"pip non trovato in {pip}. Ricrea il venv.")
                return

            # ── Step 3: Upgrade pip ──
            advance("Aggiornamento pip...")
            self._run_cmd([python, "-m", "pip", "install", "--upgrade", "pip"],
                          "Aggiornamento pip...")

            # ── Step 4: Installa dipendenze base ──
            advance("Installazione dipendenze base...",
                    "PyQt6, faster-whisper, sounddevice, numpy, requests...")
            ok, err = self._run_cmd([pip, "install"] + BASE_PACKAGES,
                                     "Installazione pacchetti base...", timeout=600)
            if not ok:
                self._fail(f"Errore installazione dipendenze:\n{err}")
                return

            # ── Step 5: Verifica ffmpeg ──
            advance("Verifica ffmpeg...")
            if shutil.which("ffmpeg"):
                self._set_status("\u2705 ffmpeg trovato")
            else:
                self._set_status("\u26A0\uFE0F ffmpeg non trovato",
                                 "Scarica da ffmpeg.org e aggiungi al PATH. Necessario solo per file non-WAV.")

            # ── Step 6+: Diarizzazione ──
            if self.install_diarization.get():
                # PyTorch CUDA (opzionale)
                if self.install_cuda.get():
                    advance("Installazione PyTorch con CUDA...",
                            "Questo pu\u00F2 richiedere diversi minuti (~2 GB)")
                    ok, err = self._run_cmd(
                        [pip, "install", "torch", "torchaudio",
                         "--index-url", "https://download.pytorch.org/whl/cu121"],
                        "Installazione PyTorch CUDA...", timeout=900)
                    if not ok:
                        self._set_status("\u26A0\uFE0F PyTorch CUDA fallito, continuo senza GPU",
                                         "La diarizzazione funzioner\u00E0 su CPU.")

                # pyannote.audio
                advance("Installazione pyannote.audio...",
                        "Pu\u00F2 richiedere diversi minuti (~500 MB)")
                ok, err = self._run_cmd([pip, "install"] + DIARIZATION_PACKAGES,
                                         "Installazione pyannote.audio...", timeout=900)
                if not ok:
                    self._set_status("\u26A0\uFE0F pyannote.audio non installato",
                                     "La diarizzazione avanzata non sar\u00E0 disponibile.")
                else:
                    # Imposta HF_TOKEN
                    advance("Configurazione HuggingFace Token...")
                    token = self.hf_token.get().strip()
                    if token:
                        # Imposta variabile d'ambiente permanente per l'utente
                        try:
                            subprocess.run(
                                ["setx", "HF_TOKEN", token],
                                capture_output=True, text=True, timeout=30
                            )
                            os.environ["HF_TOKEN"] = token
                            self._set_status("\u2705 HF_TOKEN configurato",
                                             "La variabile sar\u00E0 attiva dalla prossima apertura del Prompt.")
                        except Exception as e:
                            self._set_status(f"\u26A0\uFE0F Errore setx: {e}",
                                             "Imposta manualmente: setx HF_TOKEN \"hf_xxx\"")
                    else:
                        self._set_status("\u26A0\uFE0F HF_TOKEN non inserito",
                                         "Imposta dopo con: setx HF_TOKEN \"hf_xxx\"")

            # ── Collegamento Desktop ──
            if self.create_shortcut.get():
                advance("Creazione collegamento sul Desktop...")
                self._create_shortcut(python)

            # ── Build EXE (opzionale) ──
            if self.build_app.get():
                advance("Compilazione .exe standalone...",
                        "PyInstaller in esecuzione (pu\u00F2 richiedere qualche minuto)")
                # Installa PyInstaller
                self._run_cmd([pip, "install", "pyinstaller"],
                              "Installazione PyInstaller...")
                pyinstaller = str(VENV_DIR / "Scripts" / "pyinstaller.exe")
                gui_file = APP_DIR / "meeting_recorder_gui.py"
                if gui_file.exists():
                    ok, err = self._run_cmd(
                        [pyinstaller, "--onedir", "--windowed",
                         "--name", "Meeting Recorder",
                         "--distpath", str(APP_DIR / "dist"),
                         "--workpath", str(APP_DIR / "build"),
                         "--noconfirm",
                         str(gui_file)],
                        "Compilazione exe...", timeout=600)
                    if ok:
                        self._set_status("\u2705 Meeting Recorder.exe creato in dist/")
                    else:
                        self._set_status("\u26A0\uFE0F Errore compilazione",
                                         "Puoi avviare con il collegamento sul Desktop.")
                else:
                    self._set_status("\u26A0\uFE0F meeting_recorder_gui.py non trovato nella cartella corrente")

            self._complete()

        except Exception as e:
            self._fail(str(e))

    def _create_shortcut(self, python_exe):
        """Crea un file .bat e un collegamento .lnk sul Desktop."""
        try:
            # Crea il file .bat di avvio
            bat_file = APP_DIR / "Avvia Meeting Recorder.bat"
            gui_file = APP_DIR / "meeting_recorder_gui.py"
            python_in_venv = VENV_DIR / "Scripts" / "python.exe"

            bat_content = f"""@echo off
title Meeting Recorder
cd /d "{APP_DIR}"
"{python_in_venv}" "{gui_file}"
if errorlevel 1 (
    echo.
    echo Errore nell'avvio di Meeting Recorder.
    echo Verifica che l'installazione sia completata correttamente.
    pause
)
"""
            bat_file.write_text(bat_content, encoding="utf-8")

            # Crea collegamento .lnk sul Desktop tramite PowerShell
            desktop = Path.home() / "Desktop"
            lnk_path = desktop / "Meeting Recorder.lnk"

            ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{lnk_path}")
$Shortcut.TargetPath = "{bat_file}"
$Shortcut.WorkingDirectory = "{APP_DIR}"
$Shortcut.Description = "Avvia Meeting Recorder"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
"""
            subprocess.run(["powershell", "-Command", ps_script],
                          capture_output=True, text=True, timeout=30)

            self._set_status("\u2705 Collegamento creato sul Desktop")

        except Exception as e:
            self._set_status(f"\u26A0\uFE0F Collegamento non creato: {e}",
                             f"Puoi avviare manualmente: {VENV_DIR}\\Scripts\\python.exe meeting_recorder_gui.py")

    def _complete(self):
        self._set_progress(100)
        self.lbl_status.config(text="\u2705  Installazione completata!", fg="#10B981",
                               font=("Segoe UI", 12, "bold"))
        self.lbl_detail.config(text="Puoi chiudere questo installer e avviare Meeting Recorder.")
        self.btn_install.config(state="normal", bg="#059669", text="\u2705  Completato")
        messagebox.showinfo("Installazione completata",
            f"{APP_NAME} \u00E8 stato installato con successo!\n\n"
            f"Per avviare:\n"
            f"\u2022 Doppio clic su 'Meeting Recorder' sul Desktop\n"
            f"\u2022 Oppure doppio clic su 'Avvia Meeting Recorder.bat'\n"
            f"  nella cartella {APP_DIR}\n\n"
            f"Virtual environment: {VENV_DIR}"
        )

    def _fail(self, msg):
        self.lbl_status.config(text="\u274C  Errore", fg="#EF4444",
                               font=("Segoe UI", 12, "bold"))
        self.lbl_detail.config(text=msg[:200])
        self.btn_install.config(state="normal", bg="#DC2626", text="\U0001F504  Riprova")
        messagebox.showerror("Errore di installazione", msg)


# ══════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════
if __name__ == "__main__":
    InstallerApp()
