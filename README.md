QalamAI Speech Translator – Monorepo (Modules 1–4)
A multi-module project for speech translation workflows, ranging from environment checks to dataset preparation, batch translation, realtime OTT/YouTube translation, and a web UI built with Flask.

Repository Layout
speech-translator/module1/ – Environment & quick sanity checks

colab_setup.ipynb, test_env.py, requirements.txt
Goal: verify Python/audio stack, GPUs (if any), and key libraries
speech-translator/module2/ – Offline/Batch translation toolkit

Scripts: dataset downloaders, audio conversion, batch translator
Assets: data/, outputs/, logs/ etc.
Goal: prepare audio datasets, convert formats, translate in batches
speech-translator/module3/ – OTT/realtime translation (scripted)

module3_ott_realtime.py and related docs
Goal: run realtime style translation from mic/stream inputs without web UI
speech-translator/module4/ – Flask web app (UI + endpoints)

app.py, templates/, static/, uploads/
Goal: upload audio/video, live mic translation, and YouTube chunked translation with TTS output
Features by Module
Module 1 – Environment Check
Quick verification of Python/audio libs
Simple recognition/translation dry-runs
Good for first-time setup and CI sanity checks
Module 2 – Batch Tools
Download/open datasets (e.g., HuggingFace)
Convert mp3 ↔ wav with consistent sampling (16kHz, mono)
Batch translate using chosen translation backend
Logs and outputs saved under outputs/, logs/
Module 3 – OTT/Realtime (Scripted)
CLI-style experiment for realtime translation from mic or stream
Good for quick experiments without the web server
Module 4 – Flask Web App
Pages:
Live Microphone translation (record → STT → translate → TTS)
Upload Audio/Video with preview and TTS output
YouTube link translation (downloads audio, chunks ~8s, STT+translate+TTS)
TTS voices:
Edge TTS when available (gendered voices for supported languages)
Fallback to gTTS
STT:
Google SpeechRecognition (chunking + language fallbacks)
Conversion pipeline robust to assorted formats (moviepy/librosa/pydub)
Supported target languages (UI): en, hi, pa, mr, kn, te, ta, gu, ml, bn, or, ur

Prerequisites
Python 3.11–3.13 recommended
Windows users: FFmpeg is handled automatically via imageio_ffmpeg in Module 4. For other modules, installing FFmpeg system-wide is still recommended:
Download static build from ffmpeg.org and add bin to PATH
For YouTube: pytube and yt-dlp are used as needed
Quick Start – Module 4 (Web App)
Install dependencies
cd speech-translator/module4
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Run the app
python app.py
Open the UI
http://127.0.0.1:5000
Notes

If using a separate static host (e.g., Netlify), deploy speech-translator/module4/ and set window.BACKEND_BASE_URL in index.html to your Flask server URL.
Module 2 – Common Commands
Convert mp3 to wav (example):
python convert_mp3_to_wav.py
Batch translate
python module2_batch_translator.py
Dataset utilities
python fetch_audio_datasets.py
Refer to QUICK_START.md and README.md inside Module 2 for details.

Module 3 – Realtime Script
See speech-translator/module3/README.md and QUICK_START.md
Example
python module3_ott_realtime.py
Configuration & Tips
STT language hint: Module 4 allows a source_lang hint on /mic_record to improve recognition.
Audio conversion: app.py attempts multiple pipelines (moviepy → system ffmpeg → librosa → pydub → moviepy fallback) to maximize compatibility.
YouTube: If pytube fails, the app falls back to yt-dlp.
Troubleshooting
"FFmpeg not found" in Modules 1–3
Install FFmpeg and ensure ffmpeg -version works in terminal.
400/500 responses in the web app
Check server logs; the app prints precise errors (invalid URL, download failure, STT errors)
Unicode console errors on Windows
The app configures UTF-8 console output; if problems persist, run terminal as UTF-8 (chcp 65001).
License
This repository is provided for educational and research purposes. Review third‑party package licenses (gTTS, Edge TTS, yt-dlp, pytube, librosa, etc.) before commercial use.

Acknowledgments
Python SpeechRecognition, gTTS, Edge TTS, librosa, moviepy, yt-dlp, pytube
Hugging Face datasets (optional, Module 2)
