"""
Fetch a few sample audio files from indicvoices_r using datasets library.
This should work now that we're authenticated with HuggingFace.
"""
import os
import sys

# Try importing - might still have torch issues, but let's try
try:
    from datasets import load_dataset
    import soundfile as sf
    import numpy as np
    print("✅ Libraries imported successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Since the full dataset is very large, you can:")
    print("   1. Add your own audio files to the 'data' folder")
    print("   2. Or manually download specific files from HuggingFace")
    sys.exit(1)

def fetch_language_samples(language, num_samples=20, output_dir="data"):
    """Fetch samples from one language."""
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print(f"\n📥 Loading {language} dataset (streaming mode)...")
        # Load just a small split to avoid downloading everything
        # Streaming=True means we only download what we iterate over
        dataset = load_dataset("ai4bharat/indicvoices_r", language, split="train", streaming=True)
        
        print(f"🎧 Extracting {num_samples} sample(s) for {language}...")
        saved = 0
        
        for i, sample in enumerate(dataset):
            if i % 50 == 0 and i > 0:
                print(f"  ⏳ Processed {i} samples, found {saved} valid audio files so far...")
            if saved >= num_samples:
                break
                
            audio = sample.get("audio")
            if audio is None:
                continue
            
            audio_array = audio.get("array")
            sample_rate = audio.get("sampling_rate", 16000)
            
            if audio_array is None:
                continue
            
            # Convert to numpy array
            if not isinstance(audio_array, np.ndarray):
                audio_array = np.array(audio_array)
            
            # Convert to mono if needed
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)
            
            # Normalize
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)
            if audio_array.max() > 1.0 or audio_array.min() < -1.0:
                audio_array = audio_array / np.max(np.abs(audio_array))
            
            # Save
            filename = f"sample_{language.lower()}_{saved:03d}.wav"
            filepath = os.path.join(output_dir, filename)
            sf.write(filepath, audio_array, int(sample_rate))
            
            # Print progress every 10 files
            if (saved + 1) % 10 == 0 or (saved + 1) == num_samples:
                print(f"  ✅ Progress: {saved + 1}/{num_samples} files saved for {language}")
            saved += 1
        
        return saved
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 0

if __name__ == "__main__":
    # Languages to fetch (20 samples each - 11 languages = 220 files total)
    # Note: English is typically not in indicvoices_r (it's Indian languages dataset)
    languages = [
        "Hindi",      # hi
        "Punjabi",    # pa
        "Marathi",    # mr
        "Kannada",    # kn
        "Telugu",     # te
        "Tamil",     # ta
        "Gujarati",  # gu
        "Malayalam",  # ml
        "Bengali",    # bn
        "Odia",       # or
        "Urdu"        # ur
    ]
    
    print("🎯 Fetching audio files from indicvoices_r...")
    print(f"This will download 20 samples per language (total: {len(languages) * 20} files)")
    print("Using streaming mode - downloading only what we need.\n")
    
    total = 0
    for lang in languages:
        count = fetch_language_samples(lang, num_samples=20)
        total += count
    
    print(f"\n🎉 Done! Total files downloaded: {total}")
    print(f"📁 Files saved in: {os.path.abspath('data')}")

