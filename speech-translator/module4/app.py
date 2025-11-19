"""
Module 4 — Flask Real-Time Speech Translator Web App
Upload audio/video files or use microphone for real-time translation.
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename
import re
import subprocess
import numpy as np
import sys

# Speech Recognition (Google STT - avoids torch DLL issues)
import speech_recognition as sr

# Translation (using deep-translator - already working in Modules 2 & 3)
from deep_translator import GoogleTranslator

# Text-to-Speech
from gtts import gTTS

# Audio processing
import librosa
import soundfile as sf
from scipy import signal
from pydub import AudioSegment

# Optional YouTube imports (lazy-loaded where possible)
try:
    from pytube import YouTube
    PYTUBE_AVAILABLE = True
except Exception:
    PYTUBE_AVAILABLE = False

# Edge TTS for gender-matched voices
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# ---------- CONFIG ----------
app = Flask(__name__)

# Ensure console can print unicode (emojis) without crashing on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

# Configure pydub to use embedded ffmpeg if available (avoids system ffmpeg requirement)
try:
    import imageio_ffmpeg
    _ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    # pydub looks at AudioSegment.converter; set it to the ffmpeg binary
    if _ffmpeg_bin and os.path.exists(_ffmpeg_bin):
        AudioSegment.converter = _ffmpeg_bin
        # Some pydub versions also read ffmpeg/ffprobe attributes
        try:
            from pydub.utils import which
            # Overwrite which to return embedded ffmpeg path when asked for ffmpeg/ffprobe
            os.environ['FFMPEG_BINARY'] = _ffmpeg_bin
        except Exception:
            pass
        print(f"🎛 Using embedded ffmpeg for pydub: {_ffmpeg_bin}")
except Exception as _e:
    print(f"⚠️ Could not configure embedded ffmpeg: {_e}")

# Target languages (same as Module 2 & 3)
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

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4', 'avi', 'mov', 'mkv'}

# ---------- HELPERS ----------
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(audio_file):
    """Convert audio file to WAV format (16kHz, mono) for speech recognition."""
    tmp = tempfile.mktemp(suffix=".wav")
    e1 = None
    e2 = None
    
    # Try moviepy FIRST (it has embedded ffmpeg via imageio_ffmpeg - handles M4A/MP4/WEBM perfectly)
    if audio_file.lower().endswith(('.m4a', '.mp4', '.mov', '.webm', '.avi', '.mkv', '.flv')):
        try:
            # In moviepy 2.x, AudioFileClip is directly in moviepy module, not moviepy.editor
            try:
                from moviepy import AudioFileClip  # New moviepy 2.x API
            except ImportError:
                from moviepy.editor import AudioFileClip  # Old moviepy 1.x API
            
            import imageio_ffmpeg
            print("🔄 Trying moviepy conversion first (has embedded ffmpeg via imageio_ffmpeg)...")
            
            # Get the embedded ffmpeg path
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            print(f"📁 Using embedded ffmpeg from: {ffmpeg_path}")
            
            # Create audio clip (moviepy will use imageio_ffmpeg automatically)
            clip = AudioFileClip(audio_file)
            
            # Write as WAV (16kHz, mono, PCM)
            # MoviePy 2.x API: fps, nbytes, codec, ffmpeg_params only
            clip.write_audiofile(
                tmp,
                fps=16000,
                nbytes=2,
                codec='pcm_s16le',
                ffmpeg_params=['-ac', '1', '-ar', '16000', '-loglevel', 'error']  # Force mono, 16kHz, quiet
            )
            clip.close()
            
            if os.path.exists(tmp) and os.path.getsize(tmp) > 100:  # At least 100 bytes
                print(f"✅ Converted to WAV using moviepy: {tmp} ({os.path.getsize(tmp)} bytes)")
                return tmp
            else:
                print(f"⚠️ Moviepy conversion created empty or invalid file")
        except ImportError as import_err:
            print(f"⚠️ Moviepy import failed: {import_err}")
            import traceback
            traceback.print_exc()
        except Exception as moviepy_err:
            print(f"⚠️ Moviepy conversion failed: {str(moviepy_err)}")
            import traceback
            traceback.print_exc()
    
    # Try ffmpeg via subprocess if available (system-installed)
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("🔄 Using system ffmpeg for conversion...")
            cmd = [
                'ffmpeg', '-i', audio_file,
                '-ar', '16000', '-ac', '1', '-f', 'wav', tmp, '-y', '-loglevel', 'error'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
                print(f"✅ Converted to WAV using ffmpeg: {tmp}")
                return tmp
            else:
                print(f"⚠️ ffmpeg conversion failed: {result.stderr}")
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as ffmpeg_err:
        print(f"⚠️ System ffmpeg not available: {ffmpeg_err}")
    
    # Try librosa (handles most formats but may fail on DASH M4A)
    try:
        print("🔄 Trying librosa conversion...")
        # For DASH M4A files, try loading with explicit backend
        try:
            # First try with default settings
            y, sr = librosa.load(audio_file, sr=16000, mono=True, duration=None)
        except Exception as librosa_err:
            # If that fails, try with explicit format hint
            if audio_file.lower().endswith('.m4a'):
                print("🔄 M4A file detected, trying alternative approach...")
                # Try loading with different backends
                try:
                    # Force audioread backend
                    y, sr = librosa.load(audio_file, sr=16000, mono=True, duration=None, res_type='kaiser_fast')
                except:
                    # Try with shorter duration first to test
                    try:
                        y, sr = librosa.load(audio_file, sr=16000, mono=True, duration=30)
                        print("⚠️ Only loaded first 30 seconds (testing)")
                    except:
                        raise librosa_err
            else:
                raise librosa_err
        
        sf.write(tmp, y, 16000)
        print(f"✅ Converted to WAV using librosa: {tmp}")
        return tmp
    except Exception as err1:
        e1 = str(err1)
        print(f"⚠️ Librosa failed: {e1}")
    
    # Fallback: Try using pydub (needs ffmpeg but handles many formats)
    try:
        from pydub import AudioSegment
        print(f"🔄 Trying pydub conversion...")
        # Try different format hints
        try:
            if audio_file.lower().endswith('.m4a'):
                audio = AudioSegment.from_file(audio_file, format='m4a')
            elif audio_file.lower().endswith('.mp4'):
                audio = AudioSegment.from_file(audio_file, format='mp4')
            else:
                audio = AudioSegment.from_file(audio_file)
            
            # Convert to WAV (16kHz, mono)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(tmp, format="wav")
            print(f"✅ Converted to WAV using pydub: {tmp}")
            return tmp
        except Exception as pydub_inner_err:
            e2 = str(pydub_inner_err)
            print(f"⚠️ Pydub direct conversion failed: {e2}")
            raise Exception(f"Pydub failed: {e2}")
    except Exception as err2:
        e2 = str(err2)
        print(f"⚠️ Pydub failed: {e2}")

    # Final attempt: try moviepy regardless of extension (handles mislabeled files)
    try:
        try:
            from moviepy import AudioFileClip
        except ImportError:
            from moviepy.editor import AudioFileClip
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print("🔄 Final fallback: moviepy generic attempt...")
        clip = AudioFileClip(audio_file)
        clip.write_audiofile(
            tmp,
            fps=16000,
            nbytes=2,
            codec='pcm_s16le',
            ffmpeg_params=['-ac', '1', '-ar', '16000', '-loglevel', 'error']
        )
        clip.close()
        if os.path.exists(tmp) and os.path.getsize(tmp) > 100:
            print(f"✅ Converted to WAV using moviepy (fallback): {tmp}")
            return tmp
    except Exception as final_mp_err:
        print(f"⚠️ Moviepy fallback failed: {final_mp_err}")
    
    # Last resort: Check if already WAV
    if audio_file.lower().endswith('.wav'):
        print(f"✅ File is already WAV: {audio_file}")
        return audio_file
    
    # Final error
    error_msg = f"All conversion methods failed. "
    if e1:
        error_msg += f"Librosa: {e1}. "
    if e2:
        error_msg += f"Pydub: {e2}. "
    error_msg += "For M4A/WEBM files, ffmpeg may be required. Install ffmpeg or try a different video."
    
    print(f"❌ {error_msg}")
    return None

def speech_to_text(audio_file, source_language=None, max_chunk_seconds: int = 45):
    """Convert speech to text using Google Speech Recognition with chunking and better language handling."""
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.6

    # Map shorthand to Google language codes
    lang_map = {
        "hi": "hi-IN", "en": "en-US", "mr": "mr-IN", "ta": "ta-IN",
        "te": "te-IN", "kn": "kn-IN", "gu": "gu-IN", "ml": "ml-IN",
        "bn": "bn-IN", "pa": "pa-IN", "or": "or-IN", "ur": "ur-PK"
    }
    preferred_lang = lang_map.get(source_language, source_language) if source_language else None

    try:
        # Determine duration using soundfile for reliability
        try:
            info = sf.info(audio_file)
            total_duration = float(getattr(info, 'duration', 0.0))
        except Exception:
            total_duration = 0.0

        texts: list[str] = []
        if total_duration and total_duration > max_chunk_seconds:
            # Process in chunks to avoid Google STT long-audio failures
            offset = 0.0
            while offset < total_duration:
                duration = min(max_chunk_seconds, total_duration - offset)
                with sr.AudioFile(audio_file) as source:
                    try:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    except Exception:
                        pass
                    audio_chunk = recognizer.record(source, duration=duration, offset=offset)
                text = _recognize_with_fallbacks(recognizer, audio_chunk, preferred_lang)
                if text:
                    texts.append(text)
                offset += duration
        else:
            with sr.AudioFile(audio_file) as source:
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                except Exception:
                    pass
                audio_data = recognizer.record(source)
            text = _recognize_with_fallbacks(recognizer, audio_data, preferred_lang)
            if text:
                texts.append(text)

        final_text = " ".join(t.strip() for t in texts if t).strip()
        return final_text or None
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"❌ STT failed: {e}")
        return None


def _recognize_with_fallbacks(recognizer: sr.Recognizer, audio_data, preferred_lang: str | None) -> str | None:
    # 1) Try preferred language if provided
    if preferred_lang:
        try:
            return recognizer.recognize_google(audio_data, language=preferred_lang)
        except Exception:
            pass
    # 2) Try auto
    try:
        return recognizer.recognize_google(audio_data)
    except Exception:
        pass
    # 3) Try English
    try:
        return recognizer.recognize_google(audio_data, language="en-US")
    except Exception:
        pass
    # 4) Try Hindi
    try:
        return recognizer.recognize_google(audio_data, language="hi-IN")
    except Exception:
        pass
    return None

def translate_text(text, target_lang):
    """Translate text to target language."""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return None

def detect_gender_from_audio(audio_file):
    """
    Detect speaker gender from audio using pitch analysis.
    Returns 'male', 'female', or 'unknown'
    """
    try:
        # Load audio (analyze first 5 seconds for faster processing)
        y, sr = librosa.load(audio_file, sr=16000, mono=True, duration=5.0)
        
        if len(y) < sr:  # Too short (< 1 second)
            return 'unknown'
        
        # Use librosa's pyin (probabilistic YIN) for better pitch detection
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),  # ~65 Hz (lowest male)
            fmax=librosa.note_to_hz('C7'),  # ~2093 Hz (highest female)
            frame_length=2048
        )
        
        # Filter out unvoiced frames and get valid pitch values
        pitch_values = f0[voiced_flag]
        
        if len(pitch_values) == 0:
            # Fallback: try autocorrelation method
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0 and 80 < pitch < 400:  # Valid human pitch range
                    pitch_values.append(pitch)
        
        if len(pitch_values) == 0:
            return 'unknown'
        
        # Calculate statistics
        avg_pitch = np.mean(pitch_values)
        median_pitch = np.median(pitch_values)
        
        # Use median for more robust classification (less affected by outliers)
        final_pitch = median_pitch
        
        # Gender classification based on pitch
        # Male voices typically: 85-180 Hz (average ~120 Hz)
        # Female voices typically: 165-255 Hz (average ~220 Hz)
        # There's overlap around 150-200 Hz, use median for better accuracy
        if final_pitch < 140:
            return 'male'
        elif final_pitch > 200:
            return 'female'
        else:
            # Ambiguous range (140-200 Hz) - use average as tie-breaker
            if avg_pitch < 170:
                return 'male'
            else:
                return 'female'
    
    except Exception as e:
        print(f"⚠️ Gender detection failed: {e}")
        return 'male'  # Default to male if detection fails

def get_edge_tts_voice(lang_code, gender='male'):
    """
    Get appropriate Edge TTS voice for language and gender.
    Returns voice name or None if not available.
    """
    if not EDGE_TTS_AVAILABLE:
        return None
    
    # Edge TTS voice mapping by language and gender
    # Format: {lang_code: {'male': 'voice_name', 'female': 'voice_name'}}
    voice_map = {
        'en': {
            'male': 'en-US-GuyNeural',  # or 'en-US-DavisNeural'
            'female': 'en-US-AriaNeural'
        },
        'hi': {
            'male': 'hi-IN-MadhurNeural',
            'female': 'hi-IN-SwaraNeural'
        },
        'mr': {
            'male': 'mr-IN-ManoharNeural',
            'female': 'mr-IN-AarohiNeural'
        },
        'ta': {
            'male': 'ta-IN-ValluvarNeural',
            'female': 'ta-IN-PallaviNeural'
        },
        'te': {
            'male': 'te-IN-MohanNeural',
            'female': 'te-IN-ShrutiNeural'
        },
        'kn': {
            'male': 'kn-IN-GaganNeural',
            'female': 'kn-IN-SapnaNeural'
        },
        'gu': {
            'male': 'gu-IN-NiranjanNeural',
            'female': 'gu-IN-DhwaniNeural'
        },
        'ml': {
            'male': 'ml-IN-MidhunNeural',
            'female': 'ml-IN-SobhanaNeural'
        },
        'bn': {
            'male': 'bn-IN-BashkarNeural',
            'female': 'bn-IN-TanishaaNeural'
        },
        'ur': {
            'male': 'ur-PK-AsadNeural',
            'female': 'ur-PK-UzmaNeural'
        },
        'pa': {
            'male': 'pa-IN-GurpreetNeural',
            'female': 'pa-IN-GurpreetNeural'  # Limited options
        },
        'or': {
            'male': 'or-IN-LekhaNeural',  # Limited options
            'female': 'or-IN-LekhaNeural'
        }
    }
    
    lang_voices = voice_map.get(lang_code)
    if lang_voices:
        return lang_voices.get(gender, lang_voices.get('male'))  # Default to male if gender not found
    
    return None

def text_to_speech(text, lang_code, output_path, gender='male'):
    """
    Convert text to speech with gender matching.
    Uses edge-tts if available (better voices), falls back to gTTS.
    """
    # Try Edge TTS first (better quality, gender-matched voices)
    if EDGE_TTS_AVAILABLE:
        try:
            voice = get_edge_tts_voice(lang_code, gender)
            if voice:
                print(f"🔊 Using Edge TTS voice: {voice} ({gender})")
                # Generate audio using edge-tts
                import asyncio
                import edge_tts
                
                async def generate():
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(output_path)
                
                # Run async function
                try:
                    asyncio.run(generate())
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        return True
                except Exception as e:
                    print(f"⚠️ Edge TTS failed: {e}, falling back to gTTS")
        except Exception as e:
            print(f"⚠️ Edge TTS error: {e}, falling back to gTTS")
    
    # Fallback to gTTS (no gender matching, but works)
    try:
        print(f"🔊 Using gTTS (no gender matching)")
        # Handle languages that gTTS doesn't support
        if lang_code == "pa" or lang_code == "or":
            # Use Hindi as fallback for Punjabi and Odia
            tts = gTTS(text=text, lang='hi', slow=False)
        else:
            tts = gTTS(text=text, lang=lang_code, slow=False)
        
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"⚠️ TTS failed for {lang_code}: {e}")
        return False


# ---------- ROUTES ----------
@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', languages=TARGET_LANGS)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and translation."""
    try:
        # Check if file is present (accept both 'file' and 'audio')
        if 'file' in request.files:
            file = request.files['file']
        elif 'audio' in request.files:
            file = request.files['audio']
        else:
            return jsonify({"error": "No file provided (expected form field 'file' or 'audio')"}), 400
        target_lang = request.form.get('lang', 'hi')
        gender = request.form.get('gender', 'male')  # Get gender from user selection
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        print(f"📁 Uploaded: {filename}")
        
        # Convert to WAV for speech recognition
        wav_file = convert_to_wav(file_path)
        if not wav_file:
            return jsonify({"error": "Failed to convert audio file"}), 500
        
        # Speech to Text (with improved accuracy)
        # Try to detect source language from file name if available
        source_lang = None
        for lang_code in TARGET_LANGS.keys():
            if lang_code in filename.lower():
                source_lang = lang_code
                break
        
        original_text = speech_to_text(wav_file, source_language=source_lang)
        if not original_text:
            return jsonify({"error": "Could not recognize speech. Please ensure audio contains clear speech."}), 400
        
        print(f"💬 Recognized: {original_text}")
        
        # Use user-selected gender (not auto-detection)
        print(f"👤 Using selected voice gender: {gender}")
        
        # Translate
        translated_text = translate_text(original_text, target_lang)
        if not translated_text:
            return jsonify({"error": "Translation failed"}), 500
        
        print(f"🌐 Translated: {translated_text}")
        
        # Generate TTS with user-selected gender
        tts_filename = f"translated_{target_lang}_{Path(filename).stem}.mp3"
        tts_path = os.path.join(app.config['STATIC_FOLDER'], tts_filename)
        if not text_to_speech(translated_text, target_lang, tts_path, gender=gender):
            return jsonify({"error": "TTS generation failed"}), 500
        
        # Clean up temporary WAV file
        if os.path.exists(wav_file):
            os.remove(wav_file)
        
        return jsonify({
            "success": True,
            "original_text": original_text,
            "translated_text": translated_text,
            "target_language": target_lang,
            "audio_url": f"/static/{tts_filename}"
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/translate_text', methods=['POST'])
def translate_text_only():
    """Translate text directly (for real-time mic input)."""
    try:
        data = request.json
        text = data.get('text', '').strip()
        target_lang = data.get('lang', 'hi')
        gender = data.get('gender', 'male')  # Get gender from request, default to male
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Translate
        translated_text = translate_text(text, target_lang)
        if not translated_text:
            return jsonify({"error": "Translation failed"}), 500
        
        # Generate TTS with gender matching
        tts_filename = f"translated_live_{target_lang}.mp3"
        tts_path = os.path.join(app.config['STATIC_FOLDER'], tts_filename)
        if text_to_speech(translated_text, target_lang, tts_path, gender=gender):
            return jsonify({
                "success": True,
                "translated_text": translated_text,
                "audio_url": f"/static/{tts_filename}?t={int(os.path.getmtime(tts_path))}"
            })
        else:
            return jsonify({
                "success": True,
                "translated_text": translated_text,
                "audio_url": None
            })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<filename>')
def static_file(filename):
    """Serve static files."""
    return send_file(os.path.join(app.config['STATIC_FOLDER'], filename))


@app.route('/mic_record', methods=['POST'])
def mic_record():
    """Accept microphone audio upload (field name 'audio') and translate + TTS."""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio provided"}), 400

        file = request.files['audio']
        target_lang = request.form.get('lang', 'hi')
        gender = request.form.get('gender', 'male')

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename or 'mic_audio.wav')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        print(f"🎙 Received mic audio: {filename}")

        wav_file = convert_to_wav(file_path)
        if not wav_file:
            return jsonify({"error": "Failed to convert audio file"}), 500

        # Allow optional explicit source language for improved accuracy
        source_lang_hint = request.form.get('source_lang')
        original_text = speech_to_text(wav_file, source_language=source_lang_hint)
        if not original_text:
            return jsonify({"error": "Could not recognize speech."}), 400

        translated_text = translate_text(original_text, target_lang)
        if not translated_text:
            return jsonify({"error": "Translation failed"}), 500

        tts_filename = f"translated_live_{target_lang}.mp3"
        tts_path = os.path.join(app.config['STATIC_FOLDER'], tts_filename)
        if not text_to_speech(translated_text, target_lang, tts_path, gender=gender):
            return jsonify({"error": "TTS generation failed"}), 500

        try:
            if os.path.exists(wav_file):
                os.remove(wav_file)
        except Exception:
            pass

        return jsonify({
            "success": True,
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_url": f"/static/{tts_filename}?t={int(os.path.getmtime(tts_path))}"
        })
    except Exception as e:
        print(f"❌ Mic processing error: {e}")
        return jsonify({"error": str(e)}), 500


# ---------- YOUTUBE TRANSLATION (CHUNKED) ----------
def download_youtube_audio_to_file(url: str) -> str:
    """
    Download YouTube audio-only stream and return a local file path.
    Returns the path to the downloaded file (usually .mp4/m4a).
    """
    if not PYTUBE_AVAILABLE:
        raise RuntimeError("pytube is not installed. Please install dependencies.")
    # Prefer pytube; fall back to yt_dlp for better compatibility
    # Returns path to downloaded file; conversion is handled later by convert_to_wav
    last_err = None
    try:
        if not (url.startswith('http://') or url.startswith('https://')):
            raise RuntimeError("Invalid URL. Include http(s) scheme.")
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        if stream is None:
            raise RuntimeError("No audio stream available for this YouTube URL (private/age/region restricted?).")
        out_file = stream.download(filename="yt_audio")
        return out_file
    except Exception as e:
        last_err = e

    # Fallback: yt-dlp
    try:
        import yt_dlp
        tmp_base = os.path.join(tempfile.gettempdir(), 'yt_audio')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': tmp_base + '.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
            },
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            out_file = ydl.prepare_filename(info)
        if not os.path.exists(out_file):
            raise RuntimeError("yt-dlp did not produce a file")
        return out_file
    except Exception as e:
        raise RuntimeError(f"YouTube download failed: {e if e else last_err}")


def youtube_transcribe_chunk(wav_path: str, start_ms: int, end_ms: int) -> str:
    """
    Slice the WAV using librosa (no ffmpeg required) and run existing speech_to_text.
    """
    duration_s = max(0.01, (end_ms - start_ms) / 1000.0)
    offset_s = max(0.0, start_ms / 1000.0)
    tmp_chunk = tempfile.mktemp(suffix=".wav")
    try:
        # Load just the needed window and save
        y, sr = librosa.load(wav_path, sr=16000, mono=True, offset=offset_s, duration=duration_s)
        if y.size == 0:
            return ""
        sf.write(tmp_chunk, y, 16000)
        text = speech_to_text(tmp_chunk)
        return (text or "").strip()
    except Exception as e:
        print(f"⚠️ Chunk STT failed {start_ms}-{end_ms}ms: {e}")
        return ""
    finally:
        try:
            os.remove(tmp_chunk)
        except Exception:
            pass


@app.route('/youtube_translate', methods=['POST'])
def youtube_translate():
    """
    Accepts JSON { url, lang [, gender] }.
    Downloads audio, chunks into 8s segments, transcribes with Whisper,
    translates each chunk, and generates per-chunk TTS.
    Returns list of chunk dicts.
    """
    try:
        # Accept JSON or form submissions
        data = request.get_json(silent=True) or {}
        if not data:
            data = request.form.to_dict() if request.form else {}
        youtube_url = (data.get('url') or '').strip()
        target_lang = (data.get('lang') or 'hi').strip()
        gender = (data.get('gender') or 'male').strip()

        if not youtube_url:
            return jsonify({"error": "Please provide a valid YouTube URL in the 'url' field."}), 400

        # Download audio file and convert to wav using existing pipeline
        downloaded_path = download_youtube_audio_to_file(youtube_url)
        wav_path = convert_to_wav(downloaded_path)
        if not wav_path:
            return jsonify({"error": "Failed to prepare audio from YouTube"}), 500

        # Chunk in 8s windows (derive duration with librosa to avoid ffmpeg)
        chunk_ms = 8000
        try:
            total_duration_s = librosa.get_duration(path=wav_path)
        except Exception:
            # Fallback: load fully then compute length
            y_full, sr_full = librosa.load(wav_path, sr=16000, mono=True)
            total_duration_s = len(y_full) / float(sr_full or 16000)
        total_ms = int(total_duration_s * 1000)
        total_ms = min(total_ms, 60000)
        results = []

        for start in range(0, total_ms, chunk_ms):
            end = min(start + chunk_ms, total_ms)
            print(f"🎧 Processing chunk {start//1000}s - {end//1000}s")
            text = youtube_transcribe_chunk(wav_path, start, end)
            if text:
                # Translate using existing translator for consistency
                translated_text = translate_text(text, target_lang) or ""
                # Generate TTS per chunk
                tts_filename = f"yt_chunk_{start}.mp3"
                tts_path = os.path.join(app.config['STATIC_FOLDER'], tts_filename)
                audio_ok = text_to_speech(translated_text or " ", target_lang, tts_path, gender=gender)
                results.append({
                    "start": start // 1000,
                    "original": text,
                    "translated": translated_text,
                    "audio": f"/static/{tts_filename}" if audio_ok else None
                })

        # Cleanup temp files
        try:
            if os.path.exists(wav_path) and wav_path != downloaded_path:
                os.remove(wav_path)
        except Exception:
            pass
        try:
            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)
        except Exception:
            pass

        return jsonify(results)
    except Exception as e:
        print(f"❌ YouTube processing error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🎧 Module 4 — Flask Real-Time Speech Translator")
    print("="*60)
    print("🌐 Starting server...")
    print("📱 Open: http://127.0.0.1:5000")
    print("="*60)
    app.run(debug=True, host='127.0.0.1', port=5000)

