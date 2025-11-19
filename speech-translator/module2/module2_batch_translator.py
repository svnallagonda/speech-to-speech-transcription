"""
Module 2 — Multilingual Batch Translator
Automatically transcribes audio files and translates to 12+ target languages.
"""
import os
import glob
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm
import csv
from datetime import datetime

# Try to import librosa as fallback for MP3 without ffmpeg
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# ---------- CONFIG ----------
INPUT_DIR = "data"
OUTPUT_DIR = "outputs"
LOG_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Target languages (12+ Indian languages + English)
TARGET_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "pa": "Punjabi",
    "mr": "Marathi",
    "kn": "Kannada",
    "te": "Telugu",
    "ta": "Tamil",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "bn": "Bengali",
    "or": "Odia",
    "ur": "Urdu"
}

# Translation log file
log_file = os.path.join(LOG_DIR, f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# ---------- HELPERS ----------
def convert_to_wav(src):
    """Convert any audio file to WAV format (16kHz, mono) for speech recognition."""
    tmp = "tmp.wav"
    
    # If already WAV, return as-is
    if src.lower().endswith('.wav'):
        return src
    
    # Try pydub first (requires ffmpeg for MP3)
    try:
        audio = AudioSegment.from_file(src)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(tmp, format="wav")
        return tmp
    except Exception:
        # If pydub fails (no ffmpeg), try librosa as fallback
        if LIBROSA_AVAILABLE and src.lower().endswith(('.mp3', '.m4a', '.flac', '.ogg')):
            try:
                import soundfile as sf
                import numpy as np
                # Load audio with librosa (doesn't need ffmpeg)
                y, sr_orig = librosa.load(src, sr=16000, mono=True)
                # Save as WAV
                sf.write(tmp, y, 16000)
                return tmp
            except Exception as e:
                print(f"⚠️ Audio conversion failed for {src}: {e}")
                return None
        else:
            print(f"⚠️ Audio conversion failed for {src}")
            if not LIBROSA_AVAILABLE:
                print(f"   Tip: Install librosa for MP3 support without ffmpeg: pip install librosa soundfile")
            else:
                print(f"   Tip: Install ffmpeg for full format support: https://ffmpeg.org/download.html")
            return None

def speech_to_text(path):
    """Convert speech to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(path) as src:
            audio_data = recognizer.record(src)
        text = recognizer.recognize_google(audio_data, language="auto")
        return text
    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"❌ STT service error: {e}")
        return None
    except Exception as e:
        print(f"❌ STT failed: {e}")
        return None

def translate_text(text, lang):
    """Translate text to target language using Google Translate."""
    try:
        translator = GoogleTranslator(source='auto', target=lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"⚠️ Translation to {lang} failed: {e}")
        return None

def tts(text, lang, path):
    """Convert text to speech using Google TTS and save as MP3."""
    try:
        t = gTTS(text=text, lang=lang)
        t.save(path)
        return True
    except Exception as e:
        print(f"⚠️ TTS failed for {lang}: {e}")
        return False

# ---------- MAIN ----------
def main():
    # Find all audio files in input directory
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.m4a', '*.flac', '*.ogg']:
        audio_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
    
    if not audio_files:
        print(f"❌ No audio files found in '{INPUT_DIR}' directory!")
        print(f"💡 Run 'python fetch_audio_datasets.py' first, or place your audio files in '{INPUT_DIR}'")
        return
    
    # Limit files for 1-hour processing (about 40-45 files max at ~50s per file)
    MAX_FILES = 45
    if len(audio_files) > MAX_FILES:
        print(f"\n⚠️ Found {len(audio_files)} files, limiting to {MAX_FILES} files for ~1 hour processing")
        print(f"📊 This will generate ~{MAX_FILES * len(TARGET_LANGS)} output files")
        print(f"⏱️ Estimated time: ~50-60 minutes\n")
        audio_files = audio_files[:MAX_FILES]
    else:
        estimated_min = len(audio_files) * 50 / 60
        print(f"\n🎧 Found {len(audio_files)} audio file(s) to process")
        print(f"📊 Will generate ~{len(audio_files) * len(TARGET_LANGS)} output files")
        print(f"⏱️ Estimated time: ~{estimated_min:.0f} minutes\n")
    
    # Initialize log file
    log_entries = []
    
    # Process each audio file
    for file in tqdm(audio_files, desc="Processing files"):
        print(f"\n{'='*60}")
        print(f"🎧 Processing: {os.path.basename(file)}")
        print(f"{'='*60}")
        
        # Convert to WAV
        tmp = convert_to_wav(file)
        if not tmp:
            continue
        
        # Speech to text
        text = speech_to_text(tmp)
        if not text:
            os.remove(tmp) if os.path.exists(tmp) else None
            continue
        
        print(f"🗣 Recognized: {text}")
        
        # Translate to all target languages
        translations = {}
        for code, langname in tqdm(TARGET_LANGS.items(), desc=f"Translating {os.path.basename(file)}", leave=False):
            print(f"  🌐 Translating → {langname} ({code}) ...", end=" ")
            translated = translate_text(text, code)
            
            if translated:
                translations[code] = translated
                # Generate TTS
                out_mp3 = os.path.join(OUTPUT_DIR, f"{os.path.splitext(os.path.basename(file))[0]}_{code}.mp3")
                if tts(translated, code, out_mp3):
                    print(f"✅")
                else:
                    print(f"⚠️ (TTS failed)")
            else:
                print(f"❌")
        
        # Log entry
        log_entries.append({
            'input_file': os.path.basename(file),
            'recognized_text': text,
            **{f'translation_{code}': translations.get(code, '') for code in TARGET_LANGS.keys()}
        })
        
        # Clean up temp file
        if os.path.exists(tmp):
            os.remove(tmp)
    
    # Write log file
    if log_entries:
        fieldnames = ['input_file', 'recognized_text'] + [f'translation_{code}' for code in TARGET_LANGS.keys()]
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_entries)
        print(f"\n📝 Translation log saved: {log_file}")
    
    print(f"\n{'='*60}")
    print(f"🎉 Batch translation complete!")
    print(f"📁 Output files saved in: {OUTPUT_DIR}")
    print(f"📊 Total files generated: {len(audio_files) * len(TARGET_LANGS)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

