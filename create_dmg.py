#!/usr/bin/env python3
"""
Meeting Recorder — Creatore DMG per distribuzione macOS
Crea un file .dmg professionale contenente l'installer e il sorgente.

Uso:
    python3 create_dmg.py

Il DMG verrà creato sul Desktop.
Sviluppato da Marco Bonometti
"""

import os
import sys
import subprocess
import shutil
import tempfile
import plistlib
from pathlib import Path
from datetime import datetime

# ── Configurazione ──
APP_NAME = "Meeting Recorder"
VERSION = "2.0.0"
DMG_NAME = f"Meeting_Recorder_v{VERSION}_Installer"
VOLUME_NAME = f"{APP_NAME} v{VERSION}"
OUTPUT_DIR = Path.home() / "Desktop"

# File sorgente (devono essere nella stessa cartella di questo script)
SCRIPT_DIR = Path(__file__).parent.resolve()


def log(msg, icon="▸"):
    print(f"  {icon} {msg}")


def check_prerequisites():
    """Verifica che i file necessari esistano."""
    gui_file = SCRIPT_DIR / "meeting_recorder_gui.py"
    installer_file = SCRIPT_DIR / "install_meeting_recorder.py"

    missing = []
    if not gui_file.exists():
        missing.append("meeting_recorder_gui.py")
    if not installer_file.exists():
        missing.append("install_meeting_recorder.py")

    if missing:
        print(f"\n  ❌ File mancanti nella cartella {SCRIPT_DIR}:")
        for f in missing:
            print(f"     • {f}")
        print(f"\n  Copia i file mancanti accanto a questo script e rilancia.")
        sys.exit(1)


def create_readme(dest):
    """Crea il file README con le istruzioni."""
    readme = dest / "LEGGIMI.txt"
    readme.write_text(f"""╔══════════════════════════════════════════════════════════════╗
║               🎙  Meeting Recorder v{VERSION}                  ║
║               Sviluppato da Marco Bonometti                  ║
╚══════════════════════════════════════════════════════════════╝

INSTALLAZIONE RAPIDA
════════════════════

  1. Apri il Terminale (Applicazioni → Utility → Terminale)

  2. Se non hai Python 3 installato:
     brew install python

  3. Trascina la cartella "{APP_NAME}" dove preferisci
     (es. sulla Scrivania o in Applicazioni)

  4. Nel Terminale, vai nella cartella:
     cd /percorso/della/cartella/Meeting\\ Recorder

  5. Lancia l'installer grafico:
     python3 install_meeting_recorder.py

  6. L'installer farà tutto automaticamente:
     ✅ Crea un virtual environment
     ✅ Installa tutte le dipendenze
     ✅ Installa la speaker diarization (opzionale)
     ✅ Configura HuggingFace (opzionale)
     ✅ Compila l'app .app standalone (opzionale)


AVVIO DOPO L'INSTALLAZIONE
═══════════════════════════

  • Doppio clic su "start_meeting_recorder.command"
  • Oppure da terminale:
    source ~/meeting-recorder-env/bin/activate
    python3 meeting_recorder_gui.py


REQUISITI
═════════

  • macOS 11 Big Sur o successivo
  • Python 3.10+ (brew install python)
  • ~2 GB di spazio libero (con diarizzazione)


SUPPORTO
════════

  Per problemi, controlla i file di log:
  • ~/meeting_recorder_log.txt
  • ~/meeting_recorder_debug.txt

""", encoding="utf-8")


def create_background_script(dest):
    """Crea uno script AppleScript per impostare l'icona della finestra DMG."""
    script = dest / ".set_dmg_view.scpt"
    script.write_text(f"""
tell application "Finder"
    tell disk "{VOLUME_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{200, 120, 880, 540}}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 80
        close
    end tell
end tell
""")
    return script


def create_install_shortcut(dest):
    """Crea un AppleScript .app che lancia l'installer con doppio clic."""
    shortcut_app = dest / "▶ Installa Meeting Recorder.app"
    contents = shortcut_app / "Contents"
    macos = contents / "MacOS"
    macos.mkdir(parents=True, exist_ok=True)

    # Info.plist
    plist = {
        "CFBundleName": "Installa Meeting Recorder",
        "CFBundleDisplayName": "Installa Meeting Recorder",
        "CFBundleIdentifier": "com.marcobonometti.meetingrecorder.installer",
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "CFBundleExecutable": "launcher",
        "CFBundlePackageType": "APPL",
        "LSMinimumSystemVersion": "11.0",
    }
    with open(contents / "Info.plist", "wb") as f:
        plistlib.dump(plist, f)

    # Script di lancio
    launcher = macos / "launcher"
    launcher.write_text(f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
INSTALLER="$DIR/Meeting Recorder/install_meeting_recorder.py"

if [ ! -f "$INSTALLER" ]; then
    osascript -e 'display alert "Errore" message "File install_meeting_recorder.py non trovato. Assicurati che la cartella Meeting Recorder sia nella stessa posizione." as critical'
    exit 1
fi

# Verifica Python
if ! command -v python3 &> /dev/null; then
    osascript -e 'display alert "Python 3 non trovato" message "Installa Python 3 con: brew install python" as critical'
    exit 1
fi

cd "$DIR/Meeting Recorder"
python3 install_meeting_recorder.py
""")
    os.chmod(str(launcher), 0o755)

    return shortcut_app


def create_dmg():
    """Crea il DMG finale."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          🎙  Meeting Recorder — Creatore DMG                 ║
╚══════════════════════════════════════════════════════════════╝
""")

    check_prerequisites()

    dmg_output = OUTPUT_DIR / f"{DMG_NAME}.dmg"

    # ── Crea cartella temporanea ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        staging = tmpdir / "dmg_content"
        staging.mkdir()

        # ── Cartella principale dell'app ──
        app_folder = staging / APP_NAME
        app_folder.mkdir()

        log("Copia dei file sorgente...")
        shutil.copy2(SCRIPT_DIR / "meeting_recorder_gui.py", app_folder)
        shutil.copy2(SCRIPT_DIR / "install_meeting_recorder.py", app_folder)

        # ── Copia file extra se presenti ──
        extras = ["start_meeting_recorder.command", "create_dmg.py"]
        for extra in extras:
            src = SCRIPT_DIR / extra
            if src.exists():
                shutil.copy2(src, app_folder)
                log(f"Incluso: {extra}")

        # ── Crea README ──
        log("Creazione LEGGIMI.txt...")
        create_readme(staging)

        # ── Crea shortcut installer ──
        log("Creazione launcher di installazione...")
        create_install_shortcut(staging)

        # ── Crea il DMG ──
        log("Creazione immagine DMG...")

        # Rimuovi DMG precedente se esiste
        if dmg_output.exists():
            dmg_output.unlink()

        # Crea DMG con hdiutil
        temp_dmg = tmpdir / "temp.dmg"

        # Step 1: crea DMG read-write
        cmd_create = [
            "hdiutil", "create",
            "-volname", VOLUME_NAME,
            "-srcfolder", str(staging),
            "-ov",
            "-format", "UDRW",
            str(temp_dmg),
        ]
        result = subprocess.run(cmd_create, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n  ❌ Errore creazione DMG:\n{result.stderr}")
            sys.exit(1)

        log("Configurazione layout DMG...")

        # Step 2: monta il DMG per configurarlo
        mount_result = subprocess.run(
            ["hdiutil", "attach", str(temp_dmg), "-readwrite", "-noverify", "-noautoopen"],
            capture_output=True, text=True
        )

        if mount_result.returncode == 0:
            # Trova il mount point
            lines = mount_result.stdout.strip().split("\n")
            mount_point = None
            for line in lines:
                parts = line.split("\t")
                if len(parts) >= 3:
                    mount_point = parts[-1].strip()

            if mount_point:
                # Crea link simbolico ad Applications (opzionale, per drag & drop)
                # Non serve per questo tipo di installer

                # Smonta
                subprocess.run(["hdiutil", "detach", mount_point, "-quiet"],
                              capture_output=True)

        # Step 3: Converti in DMG compresso (read-only)
        log("Compressione DMG finale...")
        cmd_convert = [
            "hdiutil", "convert",
            str(temp_dmg),
            "-format", "UDZO",
            "-imagekey", "zlib-level=9",
            "-o", str(dmg_output),
        ]
        result = subprocess.run(cmd_convert, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n  ❌ Errore compressione DMG:\n{result.stderr}")
            sys.exit(1)

    # ── Risultato ──
    size_mb = dmg_output.stat().st_size / (1024 * 1024)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅  DMG creato con successo!                                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📦  {str(dmg_output.name):<52} ║
║  📍  {str(OUTPUT_DIR):<52} ║
║  📊  {f"{size_mb:.1f} MB":<52} ║
║                                                              ║
║  Per distribuire: invia il file .dmg all'altro Mac.          ║
║  L'utente apre il DMG e lancia l'installer grafico.          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    create_dmg()
