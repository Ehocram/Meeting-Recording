🎙 Meeting Recorder
Registrazione, Trascrizione, Speaker Diarization e Report AI — tutto in locale.
Sviluppato da Marco Bonometti
---
Meeting Recorder è un'applicazione desktop open source sviluppata in Python con interfaccia grafica PyQt6 per registrare riunioni in presenza, trascriverle automaticamente tramite intelligenza artificiale e generare report strutturati.
L'applicazione funziona interamente in locale: l'audio viene elaborato sul tuo computer con Whisper di OpenAI, gli speaker vengono identificati con pyannote.audio e i report vengono generati tramite LM Studio, un server LLM locale. Nessun dato viene inviato a servizi cloud esterni.
---
🔐 Perché Meeting Recorder
La maggior parte degli strumenti AI per le riunioni richiede di caricare le registrazioni su server esterni. Quando si discutono strategie aziendali, dati sensibili, vulnerabilità o decisioni riservate, questo non è accettabile. Meeting Recorder nasce per risolvere questo problema: tutta l'elaborazione avviene on-premise, i dati restano nel perimetro dell'organizzazione.
---
✨ Funzionalità
Funzionalità	Descrizione
🎙 Registrazione audio	Cattura l'audio del microfono in tempo reale con indicatore di livello visuale
📂 Caricamento file	Supporta file audio esistenti: WAV, MP3, M4A, OGG, FLAC
📝 Trascrizione automatica	Conversione audio-testo tramite faster-whisper con supporto multilingue
🗣 Speaker Diarization	Identificazione automatica dei partecipanti con riconoscimento del timbro vocale
🤖 Generazione report AI	Analisi della trascrizione e produzione di report strutturati tramite LLM locale
📋 5 formati di report	Strutturato, Libero, Verbale formale, Solo Action Items, Executive Summary
✏️ Incolla e genera	Incolla una trascrizione manualmente e genera il report senza registrare audio
💬 Chat AI integrata	Chatbot locale con 5 toni di conversazione e storico sessioni
📄 Esportazione Word	Esporta i report in formato .docx professionale
🖨 Stampa	Stampa diretta dei report dall'applicazione
📂 Archivio report	Visualizzazione e gestione dei report salvati
---
🏗 Architettura
L'applicazione è composta da un singolo file Python (`meeting_recorder_gui.py`) ed è organizzata in moduli interni:
Componente	Descrizione
RecordWorker	Thread di registrazione audio via sounddevice
TranscribeWorker	Thread di trascrizione con faster-whisper + speaker diarization
ReportWorker	Thread di generazione report via LM Studio API
RecordTab	Scheda principale: registra, trascrivi, genera report
ReportsTab	Archivio report salvati con esportazione Word e stampa
SettingsTab	Configurazione LM Studio, Whisper, diarizzazione, output
ChatWindow	Chatbot AI con toni configurabili e storico conversazioni
---
📋 Requisiti di sistema
Software richiesto
Software	Versione	Note
Python	3.10 / 3.11 / 3.12 / 3.14	3.11 raccomandato
LM Studio	Ultima versione	Server LLM locale sulla porta 1234
ffmpeg	Qualsiasi recente	Solo per file non-WAV (mp3, m4a, ecc.)
Librerie Python
Pacchetto	Scopo	Installazione
PyQt6	Interfaccia grafica	`pip install PyQt6`
faster-whisper	Trascrizione audio	`pip install faster-whisper`
sounddevice	Cattura audio	`pip install sounddevice`
numpy	Elaborazione audio	`pip install numpy`
requests	Comunicazione LM Studio	`pip install requests`
python-docx	Esportazione Word	`pip install python-docx`
pyannote.audio	Speaker diarization avanzata	`pip install pyannote.audio` (opzionale)
---
🚀 Installazione
Installer automatico (raccomandato)
Il modo più semplice è usare l'installer grafico incluso che configura tutto automaticamente.
macOS:
```bash
python3 install_meeting_recorder.py
```
Windows:
```bash
python install_meeting_recorder_win.py
```
L'installer crea il virtual environment, installa tutte le dipendenze, configura la speaker diarization e opzionalmente compila l'app standalone.
---
Installazione manuale — macOS
1. Installa Python (se non presente)
```bash
brew install python
python3 --version
```
2. Crea un virtual environment
macOS con Homebrew blocca le installazioni pip globali (PEP 668):
```bash
python3 -m venv ~/meeting-recorder-env
source ~/meeting-recorder-env/bin/activate
```
> ⚠️ Ogni volta che apri un nuovo terminale, devi riattivare il venv con `source` prima di usare pip o lanciare l'app.
3. Installa le dipendenze
```bash
pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
```
4. Installa ffmpeg (per file non-WAV)
```bash
brew install ffmpeg
```
5. Avvia l'applicazione
```bash
source ~/meeting-recorder-env/bin/activate
python3 meeting_recorder_gui.py
```
---
Installazione manuale — Windows
1. Installa Python
Scarica Python 3.11 da python.org. Spunta "Add Python to PATH" durante l'installazione.
```bash
python --version
```
2. Installa le dipendenze
```bash
pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
```
3. Installa ffmpeg
Scarica da ffmpeg.org, estrai e aggiungi la sottocartella `bin` al PATH di sistema.
4. Avvia
```bash
python meeting_recorder_gui.py
```
---
🗣 Speaker Diarization — Identificazione dei partecipanti
La speaker diarization identifica automaticamente chi sta parlando durante una riunione. Nella trascrizione, ogni intervento viene attribuito a uno speaker con un timestamp.
Livelli di diarizzazione
Livello Base — Euristica sulle pause (sempre disponibile)
Quando pyannote.audio non è installato, il sistema rileva le pause superiori a 1.5 secondi tra i segmenti e assume un cambio di speaker. Funziona bene per riunioni con turni di parola ordinati.
Livello Avanzato — Diarizzazione per timbro vocale (con pyannote.audio 3.x)
Con pyannote.audio installato, il sistema analizza il timbro vocale di ogni segmento audio e lo associa allo speaker corretto, anche quando le persone si alternano rapidamente.
> La versione 3.x di pyannote restituisce un oggetto `DiarizeOutput`. Meeting Recorder estrae automaticamente l'attributo `speaker_diarization` per ottenere l'`Annotation` con i dati degli speaker.
Formato output
```
[00:00] [Speaker 1]: Buongiorno a tutti, iniziamo la riunione.

[01:23] [Speaker 2]: Grazie. Volevo aggiornare sullo stato del progetto.

[03:45] [Speaker 1]: Perfetto, passiamo al punto successivo.

[05:12] [Speaker 3]: Ho una domanda sul budget.
```
---
🔧 Installazione di pyannote.audio e HuggingFace
macOS
1. Attiva il virtual environment
```bash
source ~/meeting-recorder-env/bin/activate
```
2. Installa pyannote.audio
```bash
pip install pyannote.audio
```
> ⚠️ L'installazione può richiedere diversi minuti e scaricare circa 500 MB di dipendenze (include PyTorch).
3. Crea un account HuggingFace
Registrati su huggingface.co/join se non hai un account.
4. Accetta le licenze dei modelli
Vai su ciascuna di queste pagine e clicca "Agree and access repository":
pyannote/speaker-diarization-3.1
pyannote/segmentation-3.0
pyannote/speaker-diarization-community-1
> ⚠️ **Tutti e tre i modelli sono necessari.** Senza accettare le licenze il download fallirà con errore 403 Forbidden.
5. Genera un Access Token
Vai su huggingface.co/settings/tokens e clicca "New token".
> ⚠️ **IMPORTANTE:** se crei un token di tipo "fine-grained", devi spuntare anche la checkbox **"Read access to contents of all public gated repos you can access"** nei permessi. In alternativa, crea un token classico di tipo **"Read"** che ha già tutti i permessi necessari.
6. Imposta la variabile d'ambiente HF_TOKEN
```bash
echo 'export HF_TOKEN="hf_IL_TUO_TOKEN_QUI"' >> ~/.zshrc
source ~/.zshrc
```
Verifica:
```bash
echo $HF_TOKEN
```
7. Verifica che pyannote funzioni
```bash
source ~/meeting-recorder-env/bin/activate
python3 -c "
from pyannote.audio import Pipeline
import os
pipeline = Pipeline.from_pretrained(
    'pyannote/speaker-diarization-3.1',
    token=os.environ['HF_TOKEN'])
print('Pipeline caricata OK!')
"
```
> ✅ Se vedi "Pipeline caricata OK!" la diarizzazione avanzata è pronta.
8. La prima volta che registri con la diarizzazione attiva, pyannote scaricherà i modelli (~300 MB). Dal secondo avvio in poi i modelli saranno in cache.
---
Windows
1. Installa pyannote.audio
```bash
pip install pyannote.audio
```
Con GPU NVIDIA + CUDA, installa prima PyTorch ottimizzato:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install pyannote.audio
```
2. Account e licenze HuggingFace
Stessa procedura di macOS: registrati, accetta le licenze dei 3 modelli, genera il token con i permessi per i gated repos.
3. Imposta HF_TOKEN
```bash
setx HF_TOKEN "hf_IL_TUO_TOKEN_QUI"
```
> ⚠️ `setx` rende la variabile permanente ma NON agisce sulla sessione corrente. Chiudi e riapri il Prompt dei comandi.
> ✅ Con una GPU NVIDIA la diarizzazione sarà quasi istantanea. Su CPU funziona ma è più lenta su registrazioni lunghe (>30 min).
---
⚙️ Configurazione di LM Studio
LM Studio è il server LLM locale che genera i report. Meeting Recorder comunica con LM Studio tramite API REST compatibile OpenAI.
Setup
Scarica e installa LM Studio da lmstudio.ai
Scarica un modello LLM (raccomandati: Mistral 7B, Llama 3 8B, Gemma 2 9B, Qwen 2.5 7B)
Avvia il server locale dalla tab "Server" sulla porta 1234
In Meeting Recorder → Impostazioni, verifica URL: `http://localhost:1234/v1/chat/completions`
Clicca "Testa connessione" per verificare
Modelli raccomandati
Modello	RAM	Qualità	Velocità
Mistral 7B Instruct	6 GB	Ottima	Veloce
Llama 3 8B Instruct	6 GB	Ottima	Veloce
Qwen 2.5 7B	6 GB	Molto buona	Veloce
Gemma 2 9B	7 GB	Eccellente	Media
Uso in rete aziendale
LM Studio può essere avviato su un server fisico nel CED con l'opzione "Serve on Local Network" abilitata. Tutti i client in rete puntano all'IP del server:
```
http://192.168.1.XXX:1234/v1/chat/completions
```
I dati non escono mai dal perimetro dell'organizzazione.
---
📖 Guida all'uso
Scheda Registra
Registrare una riunione:
Clicca "⏺ Registra" per avviare la cattura audio
La barra del livello audio mostrerà il segnale e il timer conterà la durata
Clicca "⏹ Stop" per terminare
La trascrizione parte automaticamente con identificazione degli speaker
Caricare un file audio esistente:
Clicca "📂 Carica file audio" per selezionare un file già registrato (WAV, MP3, M4A, OGG, FLAC).
Incollare una trascrizione manualmente:
Incolla del testo nel campo Trascrizione. Appena il campo contiene testo, il pulsante "🤖 Genera report" si attiva automaticamente. Non serve registrare audio.
Generare il report:
Seleziona il formato dal menu a tendina
Clicca "🤖 Genera report"
Il report appare nel pannello inferiore
Clicca "💾 Salva" per salvare su disco
Formati di report
Formato	Contenuto
📋 Strutturato	Sommario, decisioni, action items (tabella), punti chiave, rischi, note
🆓 Libero	Struttura scelta dal modello AI in base al contenuto
📝 Verbale formale	Formato burocratico: data, partecipanti, OdG, delibere
⚡ Solo Action Items	Tabella: azione, responsabile, scadenza, priorità
📊 Executive Summary	Max 10 righe: obiettivo, decisioni, prossimi passi
Chat AI
Il pulsante "💬 Chat AI" apre una finestra di chat con il modello LLM locale. Toni disponibili:
🏢 Aziendale formale — linguaggio professionale e autorevole
💬 Informale — tono amichevole e diretto
🎓 Tecnico — linguaggio specialistico e dettagliato
📝 Sintetico — risposte ultra-concise
🧠 Analitico — analisi multi-angolo con pro e contro
Impostazioni
LM Studio: URL del server e nome del modello, con test di connessione
Whisper: modello (tiny/base/small/medium/large-v3) e lingua
Diarizzazione: checkbox per attivare/disattivare l'identificazione speaker
Output: cartella di destinazione per i file salvati
---
🍎 Script di avvio macOS (.command)
Per avviare Meeting Recorder con un doppio clic nel Finder:
```bash
cd ~/Desktop/Meeting\ Recorder\ MAC

cat > start_meeting_recorder.command << 'EOF'
#!/bin/bash
source "$HOME/meeting-recorder-env/bin/activate"
cd "$(dirname "$0")"
python3 meeting_recorder_gui.py
EOF

chmod +x start_meeting_recorder.command
```
Doppio clic su `start_meeting_recorder.command` nel Finder per avviare.
---
📦 Creazione pacchetto DMG per distribuzione macOS
Il DMG permette di distribuire Meeting Recorder su altri Mac. Nella cartella devono essere presenti: `meeting_recorder_gui.py`, `install_meeting_recorder.py` e `create_dmg.py`.
```bash
cd ~/Desktop/Meeting\ Recorder\ MAC
source ~/meeting-recorder-env/bin/activate
python3 create_dmg.py
```
Il file `Meeting_Recorder_v2.0.0_Installer.dmg` verrà creato sul Desktop.
L'utente di destinazione apre il DMG, lancia l'installer grafico e tutto viene configurato automaticamente. L'unico prerequisito è Python 3 (`brew install python`). Funziona sia su Apple Silicon che su Intel.
---
🔧 Risoluzione problemi
Problema	Soluzione
`pip: command not found` (macOS)	Attiva il venv: `source ~/meeting-recorder-env/bin/activate`
`externally-managed-environment`	Crea un venv: `python3 -m venv ~/meeting-recorder-env`
`No module named 'PyQt6'`	Hai dimenticato di attivare il venv prima di lanciare l'app
Errore 403 su pyannote	Accetta le licenze su HuggingFace per tutti e 3 i modelli
Token fine-grained non funziona	Abilita "Read access to public gated repos" nei permessi del token
`use_auth_token` error	pyannote 3.x usa `token=` invece di `use_auth_token=`
`'DiarizeOutput' no attribute 'itertracks'`	pyannote 3.x: usare `diarization.speaker_diarization.itertracks()`
HF_TOKEN non trovato	Verifica con `echo $HF_TOKEN` (Mac) o `echo %HF_TOKEN%` (Win)
LM Studio non raggiungibile	Avvia il server in LM Studio porta 1234 e testa la connessione
Trascrizione lenta	Usa modello Whisper più piccolo (tiny o base) nelle impostazioni
Un solo speaker rilevato	Registrazione troppo breve o senza pause. Installa pyannote per diarizzazione per timbro
Crash all'avvio	Controlla `~/meeting_recorder_log.txt` e `~/meeting_recorder_debug.txt`
File di log
`~/meeting_recorder_log.txt` — errori critici e crash
`~/meeting_recorder_debug.txt` — log dettagliato delle operazioni
File di configurazione
```
~/.meeting_recorder_config.json
```
Cancella questo file per ripristinare le impostazioni di default.
---
⚡ Riepilogo comandi rapidi
macOS
Azione	Comando
Crea virtual environment	`python3 -m venv ~/meeting-recorder-env`
Attiva venv	`source ~/meeting-recorder-env/bin/activate`
Installa dipendenze base	`pip install PyQt6 faster-whisper sounddevice numpy requests python-docx`
Installa diarizzazione	`pip install pyannote.audio`
Imposta HF_TOKEN	`echo 'export HF_TOKEN="hf_xxx"' >> ~/.zshrc && source ~/.zshrc`
Avvia applicazione	`python3 meeting_recorder_gui.py`
Crea DMG	`python3 create_dmg.py`
Verifica pyannote	`python3 -c "from pyannote.audio import Pipeline; print('OK')"`
Windows
Azione	Comando
Installa dipendenze base	`pip install PyQt6 faster-whisper sounddevice numpy requests python-docx`
Installa diarizzazione	`pip install pyannote.audio`
PyTorch con CUDA	`pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121`
Imposta HF_TOKEN	`setx HF_TOKEN "hf_xxx"` (poi riapri cmd)
Avvia applicazione	`python meeting_recorder_gui.py`
---
📄 Licenza
Open source. Sentiti libero di usare, modificare e distribuire questo software.
---
🤝 Contribuire
Se vuoi contribuire al progetto, fai un fork del repository, apporta le tue modifiche e apri una pull request. Ogni contributo è benvenuto!

