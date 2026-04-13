# Meeting-Recording
meeting recording and Chat with LLM Studio
Meeting Recorder
Documentazione Completa
Versione 2.1 — Aprile 2026

Sviluppato da Marco Bonometti
Registrazione, Trascrizione, Speaker Diarization e Report AI
 
1. Introduzione
Meeting Recorder è un’applicazione desktop sviluppata in Python con interfaccia grafica PyQt6 per registrare riunioni, trascriverle automaticamente tramite intelligenza artificiale e generare report strutturati.
L’applicazione funziona interamente in locale: l’audio viene elaborato sul tuo computer con Whisper di OpenAI e i report vengono generati tramite LM Studio, un server LLM locale. Nessun dato viene inviato a servizi cloud esterni.
1.1 Funzionalità principali
•	Registrazione audio:  cattura l’audio del microfono in tempo reale con indicatore di livello visuale.
•	Caricamento file:  supporta file audio esistenti in formato WAV, MP3, M4A, OGG, FLAC.
•	Trascrizione automatica:  conversione audio-testo tramite faster-whisper con supporto multilingue.
•	Speaker Diarization:  identificazione automatica dei diversi partecipanti con riconoscimento del timbro vocale (pyannote.audio 3.x).
•	Generazione report AI:  analisi della trascrizione e produzione di report strutturati tramite LM Studio.
•	5 formati di report:  Strutturato, Libero, Verbale formale, Solo Action Items, Executive Summary.
•	Incolla e genera:  possibilità di incollare manualmente una trascrizione e generare direttamente il report.
•	Chat AI integrata:  chatbot locale con 5 toni di conversazione e storico sessioni.
•	Esportazione Word:  esporta i report in formato .docx professionale.
•	Stampa:  stampa diretta dei report dall’applicazione.
•	Archivio report:  visualizzazione e gestione dei report salvati.
1.2 Architettura
L’applicazione è composta da un singolo file Python (meeting_recorder_gui.py) ed è organizzata in moduli interni:
Componente	Descrizione
RecordWorker	Thread di registrazione audio via sounddevice
TranscribeWorker	Thread di trascrizione con faster-whisper + speaker diarization
ReportWorker	Thread di generazione report via LM Studio API
RecordTab	Scheda principale: registra, trascrivi, genera report
ReportsTab	Archivio report salvati con esportazione Word e stampa
SettingsTab	Configurazione LM Studio, Whisper, diarizzazione, output
ChatWindow	Chatbot AI con toni configurabili e storico conversazioni
 
2. Requisiti di sistema
2.1 Software richiesto
Software	Versione	Note
Python	3.10 / 3.11 / 3.12 / 3.14	3.11 raccomandato
LM Studio	Ultima versione	Server LLM locale sulla porta 1234
ffmpeg	Qualsiasi recente	Solo per file non-WAV (mp3, m4a, ecc.)
2.2 Librerie Python
Pacchetto	Scopo	Installazione
PyQt6	Interfaccia grafica	pip install PyQt6
faster-whisper	Trascrizione audio	pip install faster-whisper
sounddevice	Cattura audio	pip install sounddevice
numpy	Elaborazione audio	pip install numpy
requests	Comunicazione LM Studio	pip install requests
python-docx	Esportazione Word	pip install python-docx
pyannote.audio	Speaker diarization avanzata	pip install pyannote.audio (opzionale)
 
3. Installazione
3.1 Installer automatico (raccomandato)
Il modo più semplice per installare Meeting Recorder è usare l’installer grafico incluso. L’installer crea automaticamente il virtual environment, installa tutte le dipendenze, configura la speaker diarization e opzionalmente compila l’app .app standalone.
Su macOS
1.	Apri il Terminale (Applicazioni → Utility → Terminale).
2.	Vai nella cartella dove hai i file di Meeting Recorder.
3.	Lancia: python3 install_meeting_recorder.py
4.	Si aprirà una finestra grafica. Seleziona le opzioni desiderate e clicca “Installa tutto”.
✔ L’installer usa Tkinter (già incluso in macOS), non servono dipendenze esterne per lanciarlo.
Su Windows
1.	Assicurati di avere Python 3.11+ installato (da python.org, con “Add to PATH” spuntato).
2.	Apri il Prompt dei comandi nella cartella di Meeting Recorder.
3.	Lancia: python install_meeting_recorder.py
3.2 Installazione manuale su macOS
Passo 1 — Installa Python (se non presente)
brew install python
python3 --version
Passo 2 — Crea un virtual environment
macOS con Homebrew blocca le installazioni pip globali (PEP 668). Devi creare un ambiente virtuale dedicato:
python3 -m venv ~/meeting-recorder-env
source ~/meeting-recorder-env/bin/activate
⚠ Ogni volta che apri un nuovo terminale, devi riattivare il venv con il comando source prima di usare pip o lanciare l’app.
Passo 3 — Installa le dipendenze base
pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
Passo 4 — Installa ffmpeg (per file non-WAV)
brew install ffmpeg
Passo 5 — Avvia l’applicazione
source ~/meeting-recorder-env/bin/activate
cd ~/Desktop/Meeting\ Recorder\ MAC
python3 meeting_recorder_gui.py
3.3 Installazione manuale su Windows
Passo 1 — Installa Python
Scarica Python 3.11 da python.org. Durante l’installazione, spunta “Add Python to PATH”.
python --version
Passo 2 — Installa le dipendenze
pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
Passo 3 — Installa ffmpeg
Scarica ffmpeg da ffmpeg.org, estrai e aggiungi la sottocartella bin al PATH di sistema.
Passo 4 — Avvia
python meeting_recorder_gui.py
 
4. Speaker Diarization — Identificazione dei partecipanti
La speaker diarization permette di identificare automaticamente chi sta parlando durante una riunione. Nella trascrizione, ogni intervento viene attribuito a uno speaker con un timestamp.
4.1 Livelli di diarizzazione
Livello Base — Euristica sulle pause (sempre disponibile)
Quando pyannote.audio non è installato, il sistema usa un’euristica: quando rileva una pausa superiore a 1.5 secondi tra un segmento e l’altro, assume un cambio di speaker. Funziona bene per riunioni con turni di parola ordinati.
Livello Avanzato — Diarizzazione per timbro vocale (con pyannote.audio 3.x)
Con pyannote.audio installato e configurato, il sistema analizza il timbro vocale di ogni segmento audio e lo associa allo speaker corretto, anche quando le persone si alternano rapidamente.
⚠ La versione 3.x di pyannote restituisce un oggetto DiarizeOutput. Meeting Recorder estrae automaticamente l’attributo speaker_diarization per ottenere l’Annotation con i dati degli speaker.
4.2 Formato output
[00:00] [Speaker 1]: Buongiorno a tutti, iniziamo la riunione.

[01:23] [Speaker 2]: Grazie. Volevo aggiornare sullo stato del progetto.

[03:45] [Speaker 1]: Perfetto, passiamo al punto successivo.

[05:12] [Speaker 3]: Ho una domanda sul budget.
Ogni blocco contiene il timestamp di inizio, l’etichetta dello speaker e il testo. Gli interventi consecutivi dello stesso speaker vengono raggruppati.
 
5. Installazione di pyannote.audio e HuggingFace
Questa sezione descrive passo per passo come installare e configurare la diarizzazione avanzata.
5.1 Installazione su macOS
Passo 1 — Attiva il virtual environment
source ~/meeting-recorder-env/bin/activate
Passo 2 — Installa pyannote.audio
pip install pyannote.audio
⚠ L’installazione può richiedere diversi minuti e scaricare circa 500 MB di dipendenze (include PyTorch).
Passo 3 — Crea un account HuggingFace
Registrati su https://huggingface.co/join se non hai un account.
Passo 4 — Accetta le licenze dei modelli
Vai su ciascuna di queste pagine e clicca “Agree and access repository”:
https://huggingface.co/pyannote/speaker-diarization-3.1
https://huggingface.co/pyannote/segmentation-3.0
https://huggingface.co/pyannote/speaker-diarization-community-1
⚠ Tutti e tre i modelli sono necessari. Senza accettare le licenze il download fallirà con errore 403 Forbidden.
Passo 5 — Genera un Access Token
Vai su https://huggingface.co/settings/tokens e clicca “New token”.
⚠ IMPORTANTE: se crei un token di tipo “fine-grained”, devi spuntare anche la checkbox “Read access to contents of all public gated repos you can access” nei permessi. In alternativa, crea un token classico di tipo “Read” che ha già tutti i permessi necessari.
Passo 6 — Imposta la variabile d’ambiente HF_TOKEN
echo 'export HF_TOKEN="hf_IL_TUO_TOKEN_QUI"' >> ~/.zshrc
source ~/.zshrc
Verifica che sia impostato:
echo $HF_TOKEN
✔ Deve stampare il tuo token. Se è vuoto, chiudi e riapri il terminale.
Passo 7 — Verifica che pyannote funzioni
source ~/meeting-recorder-env/bin/activate
python3 -c "
from pyannote.audio import Pipeline
import os
pipeline = Pipeline.from_pretrained(
    'pyannote/speaker-diarization-3.1',
    token=os.environ['HF_TOKEN'])
print('Pipeline caricata OK!')
"
✔ Se vedi “Pipeline caricata OK!” la diarizzazione avanzata è pronta.
Passo 8 — Primo avvio
La prima volta che registri con la diarizzazione attiva, pyannote scaricherà i modelli (~300 MB). Dal secondo avvio in poi i modelli saranno in cache.
5.2 Installazione su Windows
Passo 1 — Installa pyannote.audio
Apri il Prompt dei comandi come Amministratore:
pip install pyannote.audio
Con GPU NVIDIA + CUDA, installa prima PyTorch ottimizzato:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install pyannote.audio
Passo 2 — Account e licenze HuggingFace
Stessa procedura di macOS: registrati, accetta le licenze dei 3 modelli, genera il token con i permessi per i gated repos.
Passo 3 — Imposta HF_TOKEN
setx HF_TOKEN "hf_IL_TUO_TOKEN_QUI"
⚠ setx rende la variabile permanente ma NON agisce sulla sessione corrente. Chiudi e riapri cmd.
echo %HF_TOKEN%
✔ Con una GPU NVIDIA la diarizzazione sarà quasi istantanea. Su CPU funziona ma è più lenta su registrazioni lunghe (>30 min).
 
6. Configurazione di LM Studio
LM Studio è il server LLM locale che genera i report. Meeting Recorder comunica con LM Studio tramite API REST compatibile OpenAI.
6.1 Setup iniziale
1.	Scarica e installa LM Studio da https://lmstudio.ai
2.	Scarica un modello LLM (raccomandati: Mistral 7B, Llama 3 8B, Gemma 2 9B, Qwen 2.5 7B).
3.	Avvia il server locale dalla tab “Server” sulla porta 1234.
4.	In Meeting Recorder → Impostazioni, verifica URL: http://localhost:1234/v1/chat/completions
5.	Clicca “Testa connessione” per verificare.
6.2 Modelli raccomandati
Modello	RAM	Qualità	Velocità
Mistral 7B Instruct	6 GB	Ottima	Veloce
Llama 3 8B Instruct	6 GB	Ottima	Veloce
Qwen 2.5 7B	6 GB	Molto buona	Veloce
Gemma 2 9B	7 GB	Eccellente	Media
 
7. Guida all’uso
7.1 Scheda Registra
Registrare una riunione
1.	Clicca “⏺ Registra” per avviare la cattura audio.
2.	La barra del livello audio mostrerà il segnale e il timer conterà la durata.
3.	Clicca “⏹ Stop” per terminare.
4.	La trascrizione parte automaticamente con identificazione degli speaker.
Caricare un file audio esistente
Clicca “📂 Carica file audio” per selezionare un file già registrato (WAV, MP3, M4A, OGG, FLAC). La trascrizione partirà automaticamente.
Incollare una trascrizione manualmente
Puoi incollare del testo direttamente nel campo Trascrizione. Appena il campo contiene testo, il pulsante “🤖 Genera report” si attiva automaticamente. Non serve registrare audio.
✔ Utile quando hai già una trascrizione da un’altra fonte e vuoi solo il report.
Generare il report
1.	Seleziona il formato dal menu a tendina.
2.	Clicca “🤖 Genera report”.
3.	Il report appare nel pannello inferiore.
4.	Clicca “💾 Salva” per salvare su disco.
7.2 Formati di report
Formato	Contenuto
📋 Strutturato	Sommario, decisioni, action items (tabella), punti chiave, rischi, note
🆓 Libero	Struttura scelta dal modello AI in base al contenuto
📝 Verbale formale	Formato burocratico: data, partecipanti, OdG, delibere
⚡ Solo Action Items	Tabella: azione, responsabile, scadenza, priorità
📊 Executive Summary	Max 10 righe: obiettivo, decisioni, prossimi passi
7.3 Scheda Report
•	Visualizzare qualsiasi report salvato cliccandolo nella lista.
•	Esportare in formato Word (.docx).
•	Stampare direttamente dall’applicazione.
•	Aprire la cartella di output nel Finder / Esplora risorse.
7.4 Chat AI
Il pulsante “💬 Chat AI” apre una finestra di chat con il modello LLM locale. Toni disponibili:
•	🏢 Aziendale formale — linguaggio professionale e autorevole.
•	💬 Informale — tono amichevole e diretto.
•	🎓 Tecnico — linguaggio specialistico e dettagliato.
•	📝 Sintetico — risposte ultra-concise.
•	🧠 Analitico — analisi multi-angolo con pro e contro.
7.5 Impostazioni
•	LM Studio:  URL del server e nome del modello, con test di connessione.
•	Whisper:  modello (tiny/base/small/medium/large-v3) e lingua.
•	Diarizzazione:  checkbox per attivare/disattivare l’identificazione speaker.
•	Output:  cartella di destinazione per i file salvati.
 
8. Creazione script di avvio e pacchetto DMG
8.1 Script di avvio (.command) per macOS
Lo script .command permette di avviare Meeting Recorder con un doppio clic nel Finder, senza dover aprire il terminale e attivare manualmente il virtual environment.
Creazione
Vai nella cartella di Meeting Recorder e lancia questi comandi:
cd ~/Desktop/Meeting\ Recorder\ MAC

cat > start_meeting_recorder.command << 'EOF'
#!/bin/bash
source "$HOME/meeting-recorder-env/bin/activate"
cd "$(dirname "$0")"
python3 meeting_recorder_gui.py
EOF

chmod +x start_meeting_recorder.command
Utilizzo
Fai doppio clic sul file start_meeting_recorder.command nel Finder. Si aprirà una finestra del Terminale e l’applicazione partirà automaticamente.
⚠ La prima volta macOS potrebbe chiedere conferma di sicurezza. Clicca “Apri”. Se non appare l’opzione, vai in Preferenze di Sistema → Privacy e Sicurezza e autorizza il file.
8.2 Creazione pacchetto DMG per distribuzione
Il file DMG è il formato standard macOS per distribuire software. Puoi inviare il DMG a qualsiasi altro Mac: l’utente lo apre, lancia l’installer grafico e tutto viene configurato automaticamente.
Prerequisiti
Nella cartella di Meeting Recorder devono essere presenti tre file:
•	meeting_recorder_gui.py — il codice sorgente dell’applicazione
•	install_meeting_recorder.py — l’installer grafico
•	create_dmg.py — lo script che crea il DMG
Comandi
cd ~/Desktop/Meeting\ Recorder\ MAC
source ~/meeting-recorder-env/bin/activate
python3 create_dmg.py
Il file Meeting_Recorder_v2.0.0_Installer.dmg verrà creato sul Desktop.
Contenuto del DMG
•	Meeting Recorder/  cartella con il sorgente e l’installer.
•	▶ Installa Meeting Recorder.app  doppio clic per lanciare l’installer grafico.
•	LEGGIMI.txt  istruzioni rapide per l’utente.
Distribuzione su un altro Mac
1.	Invia il file .dmg all’altro utente (email, chiavetta USB, AirDrop, ecc.).
2.	L’utente apre il DMG con doppio clic.
3.	Trascina la cartella Meeting Recorder dove preferisce (es. Desktop).
4.	Lancia “▶ Installa Meeting Recorder” con doppio clic.
5.	L’installer configura tutto automaticamente sulla macchina di destinazione.
⚠ L’unico prerequisito è Python 3 installato sull’altro Mac (brew install python). Il DMG non contiene binari compilati, quindi funziona sia su Apple Silicon che su Intel.
 
9. Risoluzione problemi
Problema	Soluzione
pip: command not found (macOS)	Attiva il venv: source ~/meeting-recorder-env/bin/activate
externally-managed-environment	Crea un venv: python3 -m venv ~/meeting-recorder-env
No module named 'PyQt6'	Hai dimenticato di attivare il venv prima di lanciare l'app
Errore 403 su pyannote	Accetta le licenze su HuggingFace per tutti e 3 i modelli
Token fine-grained non funziona	Abilita "Read access to public gated repos" nei permessi del token
use_auth_token error	pyannote 3.x usa token= invece di use_auth_token=. Aggiorna il file
'DiarizeOutput' no attribute 'itertracks'	pyannote 3.x: usare diarization.speaker_diarization.itertracks()
HF_TOKEN non trovato	Verifica con echo $HF_TOKEN (Mac) o echo %HF_TOKEN% (Win)
LM Studio non raggiungibile	Avvia il server in LM Studio porta 1234 e testa la connessione
Trascrizione lenta	Usa modello Whisper più piccolo (tiny o base) nelle impostazioni
Un solo speaker rilevato	Registrazioni troppo brevi o senza pause. Installa pyannote per diarizzazione per timbro
Crash all’avvio	Controlla ~/meeting_recorder_log.txt e ~/meeting_recorder_debug.txt
9.1 File di log
•	~/meeting_recorder_log.txt:  errori critici e crash.
•	~/meeting_recorder_debug.txt:  log dettagliato delle operazioni.
9.2 File di configurazione
~/.meeting_recorder_config.json
Cancella questo file per ripristinare le impostazioni di default.
 
10. Riepilogo comandi rapidi
macOS
Azione	Comando
Crea virtual environment	python3 -m venv ~/meeting-recorder-env
Attiva venv	source ~/meeting-recorder-env/bin/activate
Installa dipendenze base	pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
Installa diarizzazione	pip install pyannote.audio
Imposta HF_TOKEN	echo 'export HF_TOKEN="hf_xxx"' >> ~/.zshrc && source ~/.zshrc
Avvia applicazione	python3 meeting_recorder_gui.py
Crea script .command	cat > start_meeting_recorder.command << 'EOF' ... EOF && chmod +x ...
Crea DMG	python3 create_dmg.py
Verifica pyannote	python3 -c "from pyannote.audio import Pipeline; print('OK')"
Windows
Azione	Comando
Installa dipendenze base	pip install PyQt6 faster-whisper sounddevice numpy requests python-docx
Installa diarizzazione	pip install pyannote.audio
PyTorch con CUDA	pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
Imposta HF_TOKEN	setx HF_TOKEN "hf_xxx" (poi riapri cmd)
Avvia applicazione	python meeting_recorder_gui.py



