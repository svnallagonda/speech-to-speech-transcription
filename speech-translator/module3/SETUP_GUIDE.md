# Module 3 — Setup Guide

## 📋 Checklist

### ✅ Files Created
- [x] `requirements.txt` - Dependencies (free/open-source)
- [x] `module3_ott_realtime.py` - Main script (no Azure needed!)
- [x] `README.md` - Full documentation
- [x] `QUICK_START.md` - 3-minute guide

---

## 🚀 Next Steps

### 1. Install Dependencies
```powershell
cd speech-translator\module3
pip install -r requirements.txt
```

### 2. Choose STT Method (Optional)
Edit `module3_ott_realtime.py` or set environment variable:
```powershell
# Whisper (local, high quality) - Recommended
set STT_METHOD=whisper
set WHISPER_MODEL=base  # tiny, base, small, medium, large

# Or Google STT (cloud, free tier)
set STT_METHOD=google
```

### 3. Run Real-Time Translator
```powershell
# Single file translation
python module3_ott_realtime.py ../module2/data/sample_en_000.mp3 hi

# Or use in Python
python -c "from module3_ott_realtime import realtime_translate_audio_file; realtime_translate_audio_file('../module2/data/sample_en_000.mp3', 'hi')"
```

---

## 📊 Status

- ✅ Module 1: Environment setup & basic translation test
- ✅ Module 2: Batch translator (running in background)
- ✅ Module 3: Real-time OTT translator (ready to use)

---

## 💡 Quick Test

```python
from module3_ott_realtime import realtime_translate_audio_file

realtime_translate_audio_file(
    audio_file="../module2/data/sample_en_000.mp3",
    target_lang="hi",
    stt_method="whisper"  # or "google"
)
```

---

## ⚠️ Important Notes

1. **No Subscription Required**: Everything is free!
2. **STT Method**: Choose `whisper` (local) or `google` (cloud)
3. **Whisper Models**: Start with `base` for good balance of speed/quality
4. **First Run**: Whisper downloads model (~150MB for `base`), takes a moment

---

## 🆘 Troubleshooting

See `README.md` for detailed troubleshooting steps.

