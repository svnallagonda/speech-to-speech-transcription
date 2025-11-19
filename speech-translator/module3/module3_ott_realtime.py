"""
Module 3 — Real-Time OTT Speech-to-Speech Translator (Free/Open Source)
Uses Whisper (local STT) + Deep Translator + gTTS — No Azure required!
"""
import os
import time
from typing import Optional, List, Dict
from dotenv import load_dotenv
import tempfile
from pathlib import Path

# Try to import Whisper (preferred for high quality)
# Note: Whisper requires torch which may have DLL issues on Windows
try:
    import whisper
    WHISPER_AVAILABLE = True
except (ImportError, OSError):
    # OSError catches torch DLL errors on Windows
    WHISPER_AVAILABLE = False

# Try to import SpeechRecognition (fallback)
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Translation (already used in Module 2)
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# Text-to-Speech
try:
    from gtts import gTTS
    from pydub import AudioSegment
    import librosa
    import soundfile as sf
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

load_dotenv()

# ---------- CONFIG ----------
# Choose STT method: "whisper" (local, high quality) or "google" (cloud, free tier)
# Default to "google" to avoid torch DLL issues on Windows
STT_METHOD = os.getenv("STT_METHOD", "google")  # "whisper" or "google"

# Whisper model size: "tiny", "base", "small", "medium", "large"
# Smaller = faster but less accurate, Larger = slower but more accurate
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # Good balance

# Target languages (same as Module 2)
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

# ---------- HELPERS ----------
def check_dependencies():
    """Check if required dependencies are available."""
    issues = []
    
    if not WHISPER_AVAILABLE and not SPEECH_RECOGNITION_AVAILABLE:
        issues.append("❌ No STT library found. Install: pip install openai-whisper OR pip install SpeechRecognition")
    
    if not TRANSLATOR_AVAILABLE:
        issues.append("❌ Deep Translator not found. Install: pip install deep-translator")
    
    if not TTS_AVAILABLE:
        issues.append("❌ TTS libraries not found. Install: pip install gTTS pydub librosa soundfile")
    
    if issues:
        print("\n⚠️ Missing Dependencies:\n")
        for issue in issues:
            print(f"  {issue}")
        print("\n💡 Run: pip install -r requirements.txt")
        return False
    
    return True

def convert_to_wav(audio_file: str) -> Optional[str]:
    """Convert audio file to WAV format (16kHz, mono) for processing."""
    tmp = tempfile.mktemp(suffix=".wav")
    
    # If already WAV, check if needs conversion
    if audio_file.lower().endswith('.wav'):
        # Check if it's already in the right format
        try:
            y, sr = librosa.load(audio_file, sr=16000, mono=True)
            sf.write(tmp, y, 16000)
            return tmp
        except:
            return audio_file
    
    # Convert to WAV using librosa (works with MP3, M4A, FLAC, OGG)
    try:
        y, sr = librosa.load(audio_file, sr=16000, mono=True)
        sf.write(tmp, y, 16000)
        return tmp
    except Exception as e:
        print(f"⚠️ Audio conversion failed: {e}")
        return None

def speech_to_text_whisper(audio_file: str, model_size: str = "base") -> Optional[str]:
    """
    Convert speech to text using Whisper (local, high quality).
    
    Args:
        audio_file: Path to audio file
        model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
    """
    if not WHISPER_AVAILABLE:
        print("❌ Whisper not available. Install: pip install openai-whisper")
        return None
    
    try:
        print(f"📥 Loading Whisper model ({model_size})... This may take a moment the first time.")
        model = whisper.load_model(model_size)
        
        print(f"🎤 Transcribing audio...")
        result = model.transcribe(audio_file, language=None)  # Auto-detect language
        text = result["text"].strip()
        
        return text
    except Exception as e:
        print(f"❌ Whisper STT failed: {e}")
        return None

def speech_to_text_google(audio_file: str) -> Optional[str]:
    """
    Convert speech to text using Google Speech Recognition (cloud, free tier).
    
    Args:
        audio_file: Path to audio file (WAV format)
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("❌ SpeechRecognition not available. Install: pip install SpeechRecognition")
        return None
    
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        
        print(f"🎤 Transcribing audio...")
        text = recognizer.recognize_google(audio_data, language="auto")
        return text
    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")
        return None
    except Exception as e:
        print(f"❌ Google STT failed: {e}")
        return None

def speech_to_text(audio_file: str, method: str = None) -> Optional[str]:
    """
    Convert speech to text using specified method.
    
    Args:
        audio_file: Path to audio file
        method: "whisper" or "google" (uses STT_METHOD if not specified)
    """
    method = method or STT_METHOD
    
    if method == "whisper":
        return speech_to_text_whisper(audio_file, WHISPER_MODEL)
    elif method == "google":
        return speech_to_text_google(audio_file)
    else:
        print(f"❌ Unknown STT method: {method}")
        return None

def translate_text(text: str, target_lang: str) -> Optional[str]:
    """
    Translate text to target language using Google Translate (via deep-translator).
    
    Args:
        text: Source text
        target_lang: Target language code (e.g., "hi")
    """
    if not TRANSLATOR_AVAILABLE:
        print("❌ Deep Translator not available")
        return None
    
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"⚠️ Translation to {target_lang} failed: {e}")
        return None

def text_to_speech(text: str, lang_code: str, output_file: str) -> bool:
    """
    Convert text to speech using gTTS and save as MP3.
    
    Args:
        text: Text to synthesize
        lang_code: Language code (e.g., "hi")
        output_file: Output file path (.mp3)
    """
    if not TTS_AVAILABLE:
        print("❌ gTTS not available")
        return False
    
    try:
        # Handle languages that gTTS doesn't support directly
        if lang_code == "pa":
            # Punjabi - use Hindi as fallback
            tts = gTTS(text=text, lang='hi', slow=False)
        elif lang_code == "or":
            # Odia - use Hindi as fallback
            tts = gTTS(text=text, lang='hi', slow=False)
        else:
            tts = gTTS(text=text, lang=lang_code, slow=False)
        
        tts.save(output_file)
        return True
    except Exception as e:
        print(f"⚠️ TTS failed for {lang_code}: {e}")
        return False

def realtime_translate_audio_file(
    audio_file: str,
    target_lang: str = "hi",
    output_dir: str = "outputs",
    stt_method: str = None,
    save_output: bool = True
) -> Dict:
    """
    Complete pipeline: Translate audio file in real-time.
    
    Args:
        audio_file: Input audio file path
        target_lang: Target language code
        output_dir: Output directory for translated audio
        stt_method: STT method ("whisper" or "google")
        save_output: If True, save TTS audio files
    
    Returns:
        Dictionary with translation results
    """
    print("="*60)
    print("Module 3 — Real-Time OTT Speech Translator (Free/Open Source)")
    print("="*60)
    print()
    
    if not check_dependencies():
        return None
    
    stt_method = stt_method or STT_METHOD
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Input: {os.path.basename(audio_file)}")
    print(f"🎯 Target Language: {TARGET_LANGS.get(target_lang, target_lang)} ({target_lang})")
    print(f"🎤 STT Method: {stt_method.upper()}")
    print()
    
    # Convert to WAV if needed
    print("🔄 Converting audio to WAV format...")
    wav_file = convert_to_wav(audio_file)
    if not wav_file:
        return None
    
    # Speech to Text
    print(f"\n📝 Step 1: Speech-to-Text ({stt_method})...")
    text = speech_to_text(wav_file, method=stt_method)
    if not text:
        print("❌ Speech recognition failed")
        return None
    
    print(f"💬 Recognized Text: {text}")
    print()
    
    # Translate
    print(f"🌐 Step 2: Translation to {TARGET_LANGS.get(target_lang, target_lang)}...")
    translated = translate_text(text, target_lang)
    if not translated:
        print("❌ Translation failed")
        return None
    
    print(f"🌐 Translated Text: {translated}")
    print()
    
    # Text to Speech
    if save_output:
        print(f"🔊 Step 3: Text-to-Speech...")
        output_file = os.path.join(output_dir, f"{Path(audio_file).stem}_{target_lang}.mp3")
        if text_to_speech(translated, target_lang, output_file):
            print(f"✅ Saved: {output_file}")
        else:
            print("⚠️ TTS generation failed")
    
    result = {
        "input_file": audio_file,
        "recognized_text": text,
        "translated_text": translated,
        "target_language": target_lang,
        "output_file": output_file if save_output else None
    }
    
    print()
    print("="*60)
    print("✅ Translation Complete!")
    print("="*60)
    
    return result

def batch_realtime_translate(
    audio_files: List[str],
    target_langs: List[str] = None,
    output_dir: str = "outputs",
    stt_method: str = None
) -> List[Dict]:
    """
    Batch translate multiple audio files to multiple languages.
    
    Args:
        audio_files: List of input audio file paths
        target_langs: List of target language codes (default: all 12 languages)
        output_dir: Output directory
        stt_method: STT method
    
    Returns:
        List of translation results
    """
    if target_langs is None:
        target_langs = list(TARGET_LANGS.keys())
    
    results = []
    
    print(f"\n📊 Batch Translation: {len(audio_files)} files → {len(target_langs)} languages")
    print(f"📈 Total: {len(audio_files) * len(target_langs)} outputs\n")
    
    from tqdm import tqdm
    
    for audio_file in tqdm(audio_files, desc="Processing files"):
        for target_lang in target_langs:
            result = realtime_translate_audio_file(
                audio_file=audio_file,
                target_lang=target_lang,
                output_dir=output_dir,
                stt_method=stt_method,
                save_output=True
            )
            if result:
                results.append(result)
    
    return results

# ---------- MAIN ----------
if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        target_lang = sys.argv[2] if len(sys.argv) > 2 else "hi"
        
        realtime_translate_audio_file(
            audio_file=audio_file,
            target_lang=target_lang,
            stt_method=STT_METHOD
        )
    else:
        print("💡 Usage:")
        print("  python module3_ott_realtime.py <audio_file> [target_lang]")
        print()
        print("  Example:")
        print("    python module3_ott_realtime.py ../module2/data/sample_en_000.mp3 hi")
        print()
        print("📚 Supported languages:")
        for code, name in TARGET_LANGS.items():
            print(f"    {code}: {name}")
