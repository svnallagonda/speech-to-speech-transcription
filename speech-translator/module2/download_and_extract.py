"""
Download parquet files and extract audio using pyarrow (no torch needed).
"""
import os
from huggingface_hub import HfApi, hf_hub_download
import pyarrow.parquet as pq
import soundfile as sf
import numpy as np

LANGUAGE_MAP = {
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

def extract_audio_from_parquet(parquet_path, output_dir, lang_name, max_samples=20):
    """Extract audio files from a parquet file."""
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        table = pq.read_table(parquet_path)
        df = table.to_pandas()
        
        saved = 0
        for idx, row in df.iterrows():
            if saved >= max_samples:
                break
            
            # Get audio data
            audio_data = row.get('audio', {})
            if not audio_data or not isinstance(audio_data, dict):
                continue
            
            audio_array = audio_data.get('array')
            sample_rate = audio_data.get('sampling_rate', 16000)
            
            if audio_array is None:
                continue
            
            # Convert to numpy
            if not isinstance(audio_array, np.ndarray):
                audio_array = np.array(audio_array, dtype=np.float32)
            
            # Mono conversion
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)
            
            # Normalize
            if audio_array.max() > 1.0 or audio_array.min() < -1.0:
                audio_array = audio_array / np.max(np.abs(audio_array))
            
            # Save
            filename = f"sample_{lang_name.lower()}_{saved:03d}.wav"
            filepath = os.path.join(output_dir, filename)
            sf.write(filepath, audio_array.astype(np.float32), int(sample_rate))
            
            saved += 1
            if saved % 5 == 0:
                print(f"    Extracted {saved} files from this parquet...")
        
        return saved
        
    except Exception as e:
        print(f"    ❌ Error reading parquet: {e}")
        return 0

def download_and_extract(lang_code, lang_name, num_samples=20):
    """Download parquet files and extract audio for one language."""
    print(f"\n📥 Processing {lang_name} ({lang_code})...")
    
    api = HfApi()
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Download first 2 parquet files (should have enough samples)
    saved_total = 0
    for i in range(2):
        if saved_total >= num_samples:
            break
        
        filename = f"{lang_name}/train-{i:05d}-of-00099.parquet"
        print(f"  Downloading {filename}...")
        
        try:
            parquet_path = hf_hub_download(
                repo_id="ai4bharat/indicvoices_r",
                filename=filename,
                repo_type="dataset",
                local_dir="./temp_parquet"
            )
            
            remaining = num_samples - saved_total
            extracted = extract_audio_from_parquet(parquet_path, output_dir, lang_name, remaining)
            saved_total += extracted
            
            # Clean up parquet file
            if os.path.exists(parquet_path):
                os.remove(parquet_path)
                
        except Exception as e:
            print(f"  ⚠️ Could not download {filename}: {e}")
            continue
    
    print(f"  {lang_name}: {saved_total} files extracted")
    return saved_total

if __name__ == "__main__":
    print("🎯 Downloading and extracting audio files...")
    print("📊 Target: 20 samples per language (11 languages = 220 files)\n")
    
    total = 0
    for code, name in LANGUAGE_MAP.items():
        count = download_and_extract(code, name, num_samples=20)
        total += count
    
    print(f"\nComplete! Total files extracted: {total}")
    print(f"Files saved in: {os.path.abspath('data')}")

