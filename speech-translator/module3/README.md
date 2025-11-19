# Module 3 — Real-Time OTT Speech-to-Speech Translator (Free/Open Source)

## Goal
Build a real-time speech-to-speech translator using **free, open-source tools** — no Azure required! Uses Whisper (local STT) + Google Translate + gTTS.

---

## Features
- ✅ **Free & Open Source** — No Azure subscription required!
- ✅ **Whisper STT** — High-quality local speech recognition (offline-capable)
- ✅ **Google Speech Recognition** — Cloud-based alternative (free tier)
- ✅ **Google Translate** — Via deep-translator (free API)
- ✅ **gTTS** — Google Text-to-Speech (free)
- ✅ **12+ Languages** — Supports all Indian languages from Module 2
- ✅ **Multiple audio formats** — MP3, WAV, M4A, FLAC, OGG

---

## Prerequisites

### No Subscription Required! 🎉

This module uses **free, open-source tools**:
- **Whisper** (OpenAI) — Free, local STT
- **Google Speech Recognition** — Free tier
- **Google Translate** — Free API (via deep-translator)
- **gTTS** — Free text-to-speech

No Azure account needed!

---

## Quick Start

### Step 1: Install Dependencies

```powershell
cd speech-translator\module3
pip install -r requirements.txt
```

### Step 2: Choose STT Method (Optional)

Edit `module3_ott_realtime.py` or set environment variable:

```powershell
# Option 1: Whisper (local, high quality, offline) - Recommended
set STT_METHOD=whisper
set WHISPER_MODEL=base  # tiny, base, small, medium, large

# Option 2: Google Speech Recognition (cloud, free tier)
set STT_METHOD=google
```

**Whisper Models:**
- `tiny` — Fastest, least accurate (~39M params)
- `base` — **Recommended** — Good balance (~74M params)
- `small` — Better accuracy (~244M params)
- `medium` — High accuracy (~769M params)
- `large` — Best accuracy (~1550M params, slowest)

### Step 3: Run Real-Time Translator

```powershell
# Single file translation
python module3_ott_realtime.py ../module2/data/sample_en_000.mp3 hi

# Or use in Python:
python -c "from module3_ott_realtime import realtime_translate_audio_file; realtime_translate_audio_file('../module2/data/sample_en_000.mp3', 'hi')"
```

---

## Usage Examples

### Example 1: Translate Audio File

```python
from module3_ott_realtime import realtime_translate_audio_file

# Translate to Hindi using Whisper
result = realtime_translate_audio_file(
    audio_file="../module2/data/sample_en_000.mp3",
    target_lang="hi",
    stt_method="whisper",  # or "google"
    save_output=True
)

print(f"Recognized: {result['recognized_text']}")
print(f"Translated: {result['translated_text']}")
```

### Example 2: Batch Translate Multiple Files

```python
from module3_ott_realtime import batch_realtime_translate
import glob

# Get all audio files
audio_files = glob.glob("../module2/data/*.mp3")[:10]  # First 10 files

# Translate to multiple languages
results = batch_realtime_translate(
    audio_files=audio_files,
    target_langs=["hi", "mr", "te"],  # Hindi, Marathi, Telugu
    stt_method="whisper"
)
```

### Example 3: Use Google Speech Recognition

```python
from module3_ott_realtime import realtime_translate_audio_file

# Use Google STT instead of Whisper
result = realtime_translate_audio_file(
    audio_file="audio.wav",
    target_lang="hi",
    stt_method="google"  # Cloud-based, free tier
)
```

---

## Supported Languages

All languages from Module 2 are supported:

| Code | Language | STT | Translation | TTS |
|------|----------|-----|-------------|-----|
| `en` | English | ✅ | ✅ | ✅ |
| `hi` | Hindi | ✅ | ✅ | ✅ |
| `pa` | Punjabi | ✅ | ✅ | ⚠️ (uses Hindi fallback) |
| `mr` | Marathi | ✅ | ✅ | ✅ |
| `kn` | Kannada | ✅ | ✅ | ✅ |
| `te` | Telugu | ✅ | ✅ | ✅ |
| `ta` | Tamil | ✅ | ✅ | ✅ |
| `gu` | Gujarati | ✅ | ✅ | ✅ |
| `ml` | Malayalam | ✅ | ✅ | ✅ |
| `bn` | Bengali | ✅ | ✅ | ✅ |
| `or` | Odia | ✅ | ✅ | ⚠️ (uses Hindi fallback) |
| `ur` | Urdu | ✅ | ✅ | ✅ |

**Note:** Punjabi and Odia use Hindi TTS as fallback since gTTS doesn't support them directly.

---

## Output

After running, you'll get:
- **Recognized text** (original speech-to-text)
- **Translated text** (translated to target language)
- **TTS audio file** (saved as `{filename}_{lang}.mp3` in `outputs/` directory)

---

## STT Method Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Whisper** | ✅ Offline, high quality, multiple languages | ⚠️ Slower, requires GPU for large models | Local processing, privacy |
| **Google STT** | ✅ Fast, free tier, cloud-based | ⚠️ Requires internet, privacy concerns | Quick testing, cloud deployment |

**Recommendation:** Use **Whisper `base`** model for best balance of speed and quality.

---

## Troubleshooting

### Issue: "Whisper not available"
```powershell
pip install openai-whisper
```

### Issue: Whisper is slow
→ Use smaller model: `WHISPER_MODEL=tiny` or `base`
→ Or use Google STT: `STT_METHOD=google`

### Issue: "SpeechRecognition not available"
```powershell
pip install SpeechRecognition
```

### Issue: Audio conversion fails
```powershell
pip install librosa soundfile
```

### Issue: Translation fails
→ Check internet connection (Google Translate requires internet)
→ Verify deep-translator is installed: `pip install deep-translator`

### Issue: TTS fails for Punjabi/Odia
→ These languages use Hindi TTS as fallback (this is expected)

---

## Cost: FREE! 🎉

- **Whisper**: 100% free, open-source, runs locally
- **Google Speech Recognition**: Free tier available (60 requests/minute)
- **Google Translate**: Free tier (via deep-translator, no API key needed for basic usage)
- **gTTS**: Free, unlimited usage

**No subscription or API keys required!**

---

## Integration with Module 2

You can use Module 3 to process files from Module 2 with higher quality STT:

```python
# Process Module 2 audio files with Whisper (better quality)
from module3_ott_realtime import realtime_translate_audio_file

realtime_translate_audio_file(
    audio_file="../module2/data/sample_en_000.mp3",
    target_lang="hi",
    stt_method="whisper"  # Better quality than Google STT
)
```

**Advantage:** Whisper provides better transcription quality than Google Speech Recognition for complex audio.

---

## Future Enhancements

- [ ] Streaming mode (process audio in chunks)
- [ ] Live YouTube/OTT stream integration
- [ ] Faster Whisper (CTranslate2 backend)
- [ ] WebSocket server for real-time API
- [ ] Multiple target language outputs in parallel
- [ ] Offline translation models (no internet required)

