#!/usr/bin/env python3
"""
Meeting Recorder — Installer per macOS
Installa automaticamente tutte le dipendenze e configura l'applicazione.
Sviluppato da Marco Bonometti
"""

import os
import sys
import subprocess
import shutil
import threading
from pathlib import Path

# ── Usa Tkinter (incluso in macOS) per la GUI ──
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Configurazione ──
APP_NAME = "Meeting Recorder"
VENV_DIR = Path.home() / "meeting-recorder-env"
APP_DIR = Path.home() / "Desktop" / "Meeting Recorder MAC"
ICON_EMOJI = "🎙"

BASE_PACKAGES = [
    "PyQt6",
    "faster-whisper",
    "sounddevice",
    "numpy",
    "requests",
    "python-docx",
    "pyinstaller",
]

DIARIZATION_PACKAGES = [
    "pyannote.audio",
]

# ══════════════════════════════════════════
# INSTALLER GUI
# ══════════════════════════════════════════
class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Installer")
        self.root.geometry("700x580")
        self.root.resizable(False, False)
        self.root.configure(bg="#0F1117")

        # Variabili
        self.install_diarization = tk.BooleanVar(value=True)
        self.hf_token = tk.StringVar(value="")
        self.build_app = tk.BooleanVar(value=True)
        self.venv_path = tk.StringVar(value=str(VENV_DIR))

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        # ── Stile ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#0F1117")
        style.configure("Dark.TLabel", background="#0F1117", foreground="#E2E8F0",
                         font=("SF Pro Display", 13))
        style.configure("Title.TLabel", background="#0F1117", foreground="#F1F5F9",
                         font=("SF Pro Display", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#0F1117", foreground="#64748B",
                         font=("SF Pro Display", 11))
        style.configure("Section.TLabel", background="#0F1117", foreground="#60A5FA",
                         font=("SF Pro Display", 14, "bold"))
        style.configure("Status.TLabel", background="#0F1117", foreground="#94A3B8",
                         font=("SF Pro Display", 11))
        style.configure("Success.TLabel", background="#0F1117", foreground="#10B981",
                         font=("SF Pro Display", 12, "bold"))
        style.configure("Error.TLabel", background="#0F1117", foreground="#EF4444",
                         font=("SF Pro Display", 12))
        style.configure("Dark.TCheckbutton", background="#0F1117", foreground="#E2E8F0",
                         font=("SF Pro Display", 12))
        style.configure("Install.TButton", font=("SF Pro Display", 14, "bold"),
                         padding=(20, 12))
        style.configure("Dark.TEntry", fieldbackground="#1E293B", foreground="#E2E8F0",
                         font=("SF Pro Display", 12))
        style.configure("green.Horizontal.TProgressbar", troughcolor="#1E293B",
                         background="#2563EB")

        main = ttk.Frame(self.root, style="Dark.TFrame")
        main.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Header ──
        ttk.Label(main, text=f"{ICON_EMOJI}  {APP_NAME}", style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(main, text="Installer per macOS", style="Subtitle.TLabel").pack(pady=(0, 20))

        # ── Separator ──
        sep = ttk.Frame(main, height=2, style="Dark.TFrame")
        sep.pack(fill="x", pady=(0, 16))

        # ── Opzioni ──
        ttk.Label(main, text="Opzioni di installazione", style="Section.TLabel").pack(anchor="w", pady=(0, 10))

        # Checkbox diarization
        chk_diar = tk.Checkbutton(main, text="  Installa Speaker Diarization (pyannote.audio ~500 MB)",
                                   variable=self.install_diarization,
                                   bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                   activebackground="#0F1117", activeforeground="#E2E8F0",
                                   font=("SF Pro Display", 12),
                                   command=self._toggle_hf_token)
        chk_diar.pack(anchor="w", pady=2)

        # HF Token
        self.hf_frame = ttk.Frame(main, style="Dark.TFrame")
        self.hf_frame.pack(fill="x", pady=(4, 8), padx=(24, 0))
        ttk.Label(self.hf_frame, text="HuggingFace Token:", style="Dark.TLabel").pack(anchor="w")
        ttk.Label(self.hf_frame, text="Crea un token su huggingface.co/settings/tokens (tipo Read)",
                  style="Subtitle.TLabel").pack(anchor="w")
        self.hf_entry = tk.Entry(self.hf_frame, textvariable=self.hf_token,
                                  bg="#1E293B", fg="#E2E8F0", insertbackground="#E2E8F0",
                                  font=("Menlo", 12), relief="flat", bd=6,
                                  highlightthickness=1, highlightcolor="#2563EB",
                                  highlightbackground="#334155")
        self.hf_entry.pack(fill="x", pady=(4, 0))

        # Checkbox build app
        chk_build = tk.Checkbutton(main, text="  Compila in applicazione .app standalone",
                                    variable=self.build_app,
                                    bg="#0F1117", fg="#E2E8F0", selectcolor="#1E293B",
                                    activebackground="#0F1117", activeforeground="#E2E8F0",
                                    font=("SF Pro Display", 12))
        chk_build.pack(anchor="w", pady=(8, 12))

        # ── Progress ──
        ttk.Label(main, text="Progresso", style="Section.TLabel").pack(anchor="w", pady=(8, 6))

        self.progress = ttk.Progressbar(main, style="green.Horizontal.TProgressbar",
                                         mode="determinate", length=640)
        self.progress.pack(fill="x", pady=(0, 6))

        self.lbl_status = ttk.Label(main, text="Pronto per l'installazione", style="Status.TLabel")
        self.lbl_status.pack(anchor="w")

        self.lbl_detail = ttk.Label(main, text="", style="Subtitle.TLabel")
        self.lbl_detail.pack(anchor="w", pady=(2, 12))

        # ── Pulsanti ──
        btn_frame = ttk.Frame(main, style="Dark.TFrame")
        btn_frame.pack(fill="x", pady=(8, 0))

        self.btn_install = tk.Button(btn_frame, text="⬇  Installa tutto",
                                      command=self._start_install,
                                      bg="#2563EB", fg="white",
                                      activebackground="#1D4ED8", activeforeground="white",
                                      font=("SF Pro Display", 14, "bold"),
                                      relief="flat", bd=0, padx=24, pady=10,
                                      cursor="hand2")
        self.btn_install.pack(side="left")

        self.btn_quit = tk.Button(btn_frame, text="Esci",
                                   command=self.root.quit,
                                   bg="#1E293B", fg="#CBD5E1",
                                   activebackground="#263548", activeforeground="#CBD5E1",
                                   font=("SF Pro Display", 12),
                                   relief="flat", bd=0, padx=16, pady=8,
                                   cursor="hand2")
        self.btn_quit.pack(side="right")

    def _toggle_hf_token(self):
        if self.install_diarization.get():
            self.hf_frame.pack(fill="x", pady=(4, 8), padx=(24, 0))
        else:
            self.hf_frame.pack_forget()

    def _set_status(self, text, detail=""):
        self.lbl_status.config(text=text)
        self.lbl_detail.config(text=detail)
        self.root.update_idletasks()

    def _set_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def _run_cmd(self, cmd, desc=""):
        """Esegue un comando e ritorna (success, output)."""
        self._set_status(desc, f"$ {' '.join(cmd[:3])}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
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
        total_steps = 6
        if self.install_diarization.get():
            total_steps += 2
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
            python_ver = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            if python_ver.returncode != 0:
                self._fail("Python 3 non trovato. Installa con: brew install python")
                return
            ver = python_ver.stdout.strip()
            self._set_status(f"✅ {ver} trovato")

            # ── Step 2: Crea virtual environment ──
            advance("Creazione virtual environment...", str(VENV_DIR))
            if not VENV_DIR.exists():
                ok, err = self._run_cmd(["python3", "-m", "venv", str(VENV_DIR)],
                                         "Creazione virtual environment...")
                if not ok:
                    self._fail(f"Errore creazione venv:\n{err}")
                    return

            pip = str(VENV_DIR / "bin" / "pip")
            python = str(VENV_DIR / "bin" / "python3")

            # ── Step 3: Upgrade pip ──
            advance("Aggiornamento pip...")
            self._run_cmd([pip, "install", "--upgrade", "pip"], "Aggiornamento pip...")

            # ── Step 4: Installa dipendenze base ──
            advance("Installazione dipendenze base...", "PyQt6, faster-whisper, sounddevice, numpy, requests...")
            ok, err = self._run_cmd([pip, "install"] + BASE_PACKAGES,
                                     "Installazione pacchetti base...")
            if not ok:
                self._fail(f"Errore installazione dipendenze:\n{err}")
                return

            # ── Step 5: Verifica ffmpeg ──
            advance("Verifica ffmpeg...")
            if shutil.which("ffmpeg"):
                self._set_status("✅ ffmpeg trovato")
            else:
                self._set_status("⚠️ ffmpeg non trovato", "Installa con: brew install ffmpeg (necessario solo per file non-WAV)")

            # ── Step 6: Installa diarizzazione (opzionale) ──
            if self.install_diarization.get():
                advance("Installazione pyannote.audio...", "Questo può richiedere diversi minuti (~500 MB)")
                ok, err = self._run_cmd([pip, "install"] + DIARIZATION_PACKAGES,
                                         "Installazione pyannote.audio...")
                if not ok:
                    self._set_status("⚠️ Errore installazione pyannote.audio",
                                     "La diarizzazione avanzata non sarà disponibile. L'euristica base funzionerà comunque.")
                else:
                    # Imposta HF_TOKEN
                    advance("Configurazione HuggingFace Token...")
                    token = self.hf_token.get().strip()
                    if token:
                        zshrc = Path.home() / ".zshrc"
                        existing = zshrc.read_text() if zshrc.exists() else ""
                        if "HF_TOKEN" not in existing:
                            with open(zshrc, "a") as f:
                                f.write(f'\nexport HF_TOKEN="{token}"\n')
                            os.environ["HF_TOKEN"] = token
                            self._set_status("✅ HF_TOKEN configurato in ~/.zshrc")
                        else:
                            self._set_status("✅ HF_TOKEN già presente in ~/.zshrc")
                    else:
                        self._set_status("⚠️ HF_TOKEN non inserito",
                                         "Puoi aggiungerlo dopo in ~/.zshrc: export HF_TOKEN=\"hf_xxx\"")

            # ── Step 7: Crea script di avvio ──
            advance("Creazione script di avvio...")
            app_dir = APP_DIR
            app_dir.mkdir(parents=True, exist_ok=True)
            launcher = app_dir / "start_meeting_recorder.command"
            launcher.write_text(
                '#!/bin/bash\n'
                f'source "{VENV_DIR}/bin/activate"\n'
                f'cd "{app_dir}"\n'
                f'python3 meeting_recorder_gui.py\n'
            )
            os.chmod(str(launcher), 0o755)

            # ── Step 8: Build .app (opzionale) ──
            if self.build_app.get():
                advance("Compilazione .app standalone...", "PyInstaller in esecuzione (può richiedere qualche minuto)")
                gui_file = app_dir / "meeting_recorder_gui.py"
                if not gui_file.exists():
                    # Cerca nella directory corrente
                    cwd_file = Path.cwd() / "meeting_recorder_gui.py"
                    if cwd_file.exists():
                        shutil.copy2(str(cwd_file), str(gui_file))
                    else:
                        self._set_status("⚠️ meeting_recorder_gui.py non trovato",
                                         f"Copia il file in {app_dir} e rilancia il build.")
                        # Saltiamo il build ma continuiamo
                        self._complete()
                        return

                pyinstaller = str(VENV_DIR / "bin" / "pyinstaller")
                spec_content = self._generate_spec(str(gui_file))
                spec_file = app_dir / "MeetingRecorder.spec"
                spec_file.write_text(spec_content)

                ok, err = self._run_cmd(
                    [pyinstaller, str(spec_file), "--distpath", str(app_dir / "dist"),
                     "--workpath", str(app_dir / "build"), "--noconfirm"],
                    "Compilazione .app..."
                )
                if ok:
                    dist_app = app_dir / "dist" / "Meeting Recorder.app"
                    desktop_app = Path.home() / "Desktop" / "Meeting Recorder.app"
                    if dist_app.exists():
                        if desktop_app.exists():
                            shutil.rmtree(str(desktop_app))
                        shutil.copytree(str(dist_app), str(desktop_app))
                        self._set_status("✅ Meeting Recorder.app creata sul Desktop")
                    else:
                        self._set_status("⚠️ Build completato ma .app non trovata nella posizione attesa")
                else:
                    self._set_status("⚠️ Errore nella compilazione .app",
                                     "Puoi avviare l'app con lo script .command")

            self._complete()

        except Exception as e:
            self._fail(str(e))

    def _generate_spec(self, script_path):
        """Genera il file .spec per PyInstaller."""
        return f'''# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(
    ['{script_path}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtPrintSupport',
        'sounddevice',
        'numpy',
        'requests',
        'wave',
        'json',
        'ctranslate2',
        'faster_whisper',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'PIL', 'scipy', 'pandas', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Meeting Recorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Meeting Recorder',
)

app = BUNDLE(
    coll,
    name='Meeting Recorder.app',
    bundle_identifier='com.marcobonometti.meetingrecorder',
    info_plist={{
        'CFBundleName': 'Meeting Recorder',
        'CFBundleDisplayName': 'Meeting Recorder',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'NSMicrophoneUsageDescription': 'Meeting Recorder necessita del microfono per registrare le riunioni.',
        'NSHighResolutionCapable': True,
    }},
)
'''

    def _complete(self):
        self._set_progress(100)
        self.lbl_status.config(text="✅  Installazione completata!", style="Success.TLabel")
        self.lbl_detail.config(text="Puoi chiudere questo installer e avviare Meeting Recorder.")
        self.btn_install.config(state="normal", bg="#059669", text="✅  Completato")
        messagebox.showinfo("Installazione completata",
            f"{APP_NAME} è stato installato con successo!\n\n"
            f"Per avviare:\n"
            f"• Doppio clic su start_meeting_recorder.command\n"
            f"  nella cartella {APP_DIR}\n\n"
            f"Oppure da terminale:\n"
            f"  source ~/meeting-recorder-env/bin/activate\n"
            f"  python3 meeting_recorder_gui.py"
        )

    def _fail(self, msg):
        self.lbl_status.config(text="❌  Errore", style="Error.TLabel")
        self.lbl_detail.config(text=msg[:120])
        self.btn_install.config(state="normal", bg="#DC2626", text="🔄  Riprova")
        messagebox.showerror("Errore di installazione", msg)


# ══════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════
if __name__ == "__main__":
    InstallerApp()
