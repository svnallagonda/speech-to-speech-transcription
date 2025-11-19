# Module 2 — Multilingual Batch Translator

## Goal
Automatically transcribe audio files and translate them to 12+ target languages, generating audio outputs for each translation.

## Features
- ✅ Automatic speech-to-text transcription
- ✅ Translation to 12+ languages (Hindi, English, Punjabi, Marathi, Kannada, Telugu, Tamil, Gujarati, Malayalam, Bengali, Odia, Urdu)
- ✅ Text-to-speech generation for all translations
- ✅ Batch processing of multiple audio files
- ✅ CSV log of all translations

---

## Quick Start (VS Code — Windows)

### Step 1: Install Dependencies

```powershell
cd speech-translator\module2
pip install -r requirements.txt
```

**Note:** If you encounter issues with `googletrans`, you may need to install it from the GitHub repository:
```powershell
pip install googletrans==4.0.0-rc1
```

### Step 2: Get Sample Audio Files (Optional)

**Option A: Download sample datasets**
```powershell
python fetch_audio_datasets.py
```

This will download 6 sample audio files from the IndicSUPERB dataset into the `data/` folder.

**Option B: Use your own audio files**
Place your audio files (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`) in the `data/` folder.

### Step 3: Run Batch Translation

```powershell
python module2_batch_translator.py
```

---

## Output Structure

After running, you'll have:

```
speech-translator/
└─ module2/
   ├─ data/                    # Input audio files
   ├─ outputs/                  # Generated MP3 files (translated speech)
   │  ├─ sample_0_hi_en.mp3    # Hindi audio → English translation
   │  ├─ sample_0_hi_hi.mp3    # Hindi audio → Hindi (same)
   │  ├─ sample_0_hi_pa.mp3    # Hindi audio → Punjabi translation
   │  └─ ...
   └─ logs/                     # CSV logs with all translations
      └─ translations_YYYYMMDD_HHMMSS.csv
```

---

## Example Output

```
🎧 Processing: sample_1_hi.wav
🗣 Recognized: आप कैसे हैं
  🌐 Translating → English (en) ... ✅
  🌐 Translating → Punjabi (pa) ... ✅
  🌐 Translating → Marathi (mr) ... ✅
  ...
🎉 Batch translation complete!
📁 Output files saved in: outputs
📊 Total files generated: 12
```

---

## Configuration

Edit `module2_batch_translator.py` to customize:

- **Target languages**: Modify the `TARGET_LANGS` dictionary
- **Input/Output directories**: Change `INPUT_DIR` and `OUTPUT_DIR`
- **Audio settings**: Adjust sample rate in `convert_to_wav()` function

---

## Troubleshooting

### Issue: "No audio files found"
**Solution:** 
- Run `python fetch_audio_datasets.py` to download samples, OR
- Place your own audio files in the `data/` folder

### Issue: Speech recognition fails
**Solutions:**
- Check internet connection (Google Speech Recognition requires internet)
- Ensure audio file is clear and not too noisy
- Verify audio format (will be auto-converted to 16kHz mono WAV)

### Issue: Translation service errors
**Solutions:**
- Check internet connection
- Google Translate may have rate limits — add delays between requests if needed
- For offline mode, use alternative translation APIs (Azure, DeepL)

### Issue: TTS fails for some languages
**Solutions:**
- Some language codes may not be supported by gTTS
- Check gTTS language support: https://gtts.readthedocs.io/en/latest/module.html#languages
- Try alternative TTS engines (pyttsx3 for offline, or cloud APIs)

---

## Performance Tips

1. **Faster processing**: Process files in parallel (add threading/multiprocessing)
2. **Offline mode**: Replace Google services with offline alternatives:
   - STT: `vosk` or `whisper`
   - Translation: Use pre-loaded models or APIs
   - TTS: `pyttsx3` (offline) or `coqui-tts`
3. **Progress tracking**: Already included with `tqdm`
4. **Caching**: Add caching for repeated translations

---

## Advanced: Offline Alternative

For offline operation, create `module2_batch_translator_offline.py` with:

- **STT**: Use `whisper` (OpenAI) or `vosk` (offline)
- **Translation**: Use local models (transformers from Module 1)
- **TTS**: Use `pyttsx3` or `coqui-tts`

---

## Next Steps

- **Module 3**: Real-time translation (microphone input → instant translation → spoken output)
- **Module 4**: Web interface or API deployment

---

## Dependencies

See `requirements.txt` for full list. Key packages:
- `SpeechRecognition`: Speech-to-text
- `googletrans`: Translation service
- `gTTS`: Text-to-speech
- `pydub`: Audio processing
- `datasets`: Sample audio download
- `tqdm`: Progress bars

