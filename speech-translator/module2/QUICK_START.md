# Module 2 — Quick Start Guide

## 🚀 3-Step Setup

### 1️⃣ Install Dependencies
```powershell
cd speech-translator\module2
pip install -r requirements.txt
```

### 2️⃣ Get Audio Files
```powershell
# Option A: Download samples
python fetch_audio_datasets.py

# Option B: Place your own audio files in 'data/' folder
```

### 3️⃣ Run Translation
```powershell
python module2_batch_translator.py
```

---

## 📊 What Happens

1. **Input**: Audio files from `data/` folder
2. **Process**: 
   - Convert audio → text (speech recognition)
   - Translate text → 12+ languages
   - Convert translations → speech (TTS)
3. **Output**: 
   - MP3 files in `outputs/` folder (one per language)
   - CSV log in `logs/` folder

---

## 📁 Folder Structure (Auto-Created)

```
module2/
├── data/           ← Put audio files here
├── outputs/        ← Translated MP3s appear here
└── logs/           ← Translation logs appear here
```

---

## ⚡ Example

```
🎧 Processing: sample_1_hi.wav
🗣 Recognized: आप कैसे हैं
  🌐 Translating → English (en) ... ✅
  🌐 Translating → Punjabi (pa) ... ✅
  ...
🎉 Batch translation complete!
📊 Total files generated: 12
```

---

## ❓ Troubleshooting

**"No audio files found"**
→ Run `fetch_audio_datasets.py` or add your own files to `data/`

**Internet required**
→ Uses Google services for STT, translation, and TTS

**Rate limits**
→ Add small delays if processing many files

---

## 🎯 Next: Module 3
Real-time microphone translation!

