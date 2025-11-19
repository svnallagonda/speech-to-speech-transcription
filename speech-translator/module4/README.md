# Module 4 — Flask Real-Time Speech Translator Web App

## Goal
Create a web application for real-time speech translation with file upload support and microphone recording.

---

## Features
- ✅ **Web Interface** — Beautiful, responsive Flask app
- ✅ **File Upload** — Support for audio/video files
- ✅ **Microphone Recording** — Real-time speech capture
- ✅ **12+ Languages** — All Indian languages from Module 2
- ✅ **Free & Open Source** — Uses Google STT + Deep Translator + gTTS
- ✅ **No Azure Required** — Fully local/cloud-free stack

---

## Quick Start

### 1. Install Dependencies

```powershell
cd speech-translator\module4
pip install -r requirements.txt
```

### 2. Run the App

```powershell
python app.py
```

### 3. Open in Browser

```
http://127.0.0.1:5000
```

---

## Usage

### Upload File
1. Click "Choose File"
2. Select an audio or video file
3. Choose target language
4. Click "Upload & Translate"
5. View results and listen to translated audio

### Microphone Recording
1. Click "Start Recording"
2. Speak into your microphone
3. Click "Stop" when done
4. Translation will process automatically
5. Listen to translated audio

---

## Supported File Formats

**Audio:** MP3, WAV, M4A, FLAC, OGG  
**Video:** MP4, AVI, MOV, MKV

---

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi |
| `pa` | Punjabi |
| `mr` | Marathi |
| `kn` | Kannada |
| `te` | Telugu |
| `ta` | Tamil |
| `gu` | Gujarati |
| `ml` | Malayalam |
| `bn` | Bengali |
| `or` | Odia |
| `ur` | Urdu |

---

## API Endpoints

### POST `/upload`
Upload and translate audio/video file.

**Form Data:**
- `file`: Audio/video file
- `lang`: Target language code

**Response:**
```json
{
    "success": true,
    "original_text": "Hello, how are you?",
    "translated_text": "नमस्ते, आप कैसे हैं?",
    "target_language": "hi",
    "audio_url": "/static/translated_hi_file.mp3"
}
```

### POST `/translate_text`
Translate text directly (for external speech recognition).

**JSON Body:**
```json
{
    "text": "Hello, how are you?",
    "lang": "hi"
}
```

**Response:**
```json
{
    "success": true,
    "translated_text": "नमस्ते, आप कैसे हैं?",
    "audio_url": "/static/translated_live_hi.mp3?t=1234567890"
}
```

---

## File Structure

```
module4/
├── app.py                 # Flask application
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── style.css         # Styling
│   └── app.js           # JavaScript logic
├── uploads/              # Uploaded files (created automatically)
└── static/               # Generated audio files (created automatically)
```

---

## Troubleshooting

### Issue: Microphone not working
→ Allow microphone access in browser settings
→ Check if another app is using the microphone

### Issue: File upload fails
→ Check file size (max 50MB)
→ Verify file format is supported
→ Ensure audio contains clear speech

### Issue: Translation fails
→ Check internet connection (Google Translate requires internet)
→ Verify language code is valid

### Issue: TTS fails for Punjabi/Odia
→ These languages use Hindi TTS as fallback (expected behavior)

---

## Integration with Other Modules

Module 4 can process files from:
- **Module 2** — Batch translated audio files
- **Module 3** — Real-time translated outputs
- Any audio/video file on your system

---

## Future Enhancements

- [ ] Real-time streaming translation (WebSocket)
- [ ] YouTube URL input (download & translate)
- [ ] Batch file processing
- [ ] Voice gender selection (male/female)
- [ ] Subtitle generation (SRT files)
- [ ] Multi-language output (translate to multiple languages at once)

---

## Technical Details

**Backend:**
- Flask — Web framework
- Google Speech Recognition — STT
- Deep Translator — Translation
- gTTS — Text-to-Speech
- librosa — Audio processing

**Frontend:**
- HTML5 — Structure
- CSS3 — Styling
- JavaScript — Logic
- MediaRecorder API — Microphone recording

---

## Cost: FREE! 🎉

- No Azure subscription needed
- Google services (STT, Translate, TTS) have free tiers
- Fully open-source stack

