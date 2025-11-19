# Module 3 — Quick Start (3 Minutes)

## ⚡ 3 Steps to Real-Time Translation (FREE!)

### 1️⃣ Install Dependencies
```powershell
cd speech-translator\module3
pip install -r requirements.txt
```

### 2️⃣ Run Translator
```powershell
# Translate audio file to Hindi
python module3_ott_realtime.py ../module2/data/sample_en_000.mp3 hi
```

### 3️⃣ That's It! 🎉
No API keys or subscriptions needed — everything is free!

---

## 🎯 Quick Test

```python
from module3_ott_realtime import realtime_translate_audio_file

# Translate English audio to Hindi (male voice)
realtime_translate_audio_file(
    audio_file="your_audio.wav",
    target_lang="hi",
    gender="male"
)
```

---

## 📊 What You Get

- **Input**: Audio file (any language)
- **Process**: Real-time translation
- **Output**: 
  - Translated text (console)
  - Neural voice audio file
  - Optional speaker playback

---

## 💰 Cost
Free tier covers ~5 hours/month for testing!

