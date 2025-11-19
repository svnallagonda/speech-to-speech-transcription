"""
Fetch audio files using HuggingFace Hub API directly (no torch dependency).
Uses the token that's already saved from CLI login.
"""
import os
from huggingface_hub import HfApi, snapshot_download
import soundfile as sf
import numpy as np
import json

# Languages to fetch - mapping from code to dataset name
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

def download_language_samples(lang_code, lang_name, num_samples=20, output_dir="data"):
    """
    Download samples for one language using HuggingFace Hub.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📥 Fetching {lang_name} ({lang_code}) samples...")
    
    try:
        # Use Hub API to list and download files
        api = HfApi()
        repo_files = api.list_repo_files(
            repo_id="ai4bharat/indicvoices_r",
            repo_type="dataset"
        )
        
        # Filter files for this language
        lang_files = [f for f in repo_files if f.startswith(f"{lang_name}/") and f.endswith('.parquet')]
        
        if not lang_files:
            print(f"  ⚠️ No files found for {lang_name}")
            return 0
        
        # For now, we'll need to use datasets library to read parquet
        # But let's try a simpler approach - use CLI command instead
        print(f"  💡 Found {len(lang_files)} parquet file(s) for {lang_name}")
        print(f"  📝 Note: To extract audio, we need to process parquet files")
        print(f"  🔄 This will be handled by the datasets library...")
        
        # Alternative: Download using CLI and process
        return 0
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 0

if __name__ == "__main__":
    print("🎯 Fetching audio files using HuggingFace Hub API...")
    print("📊 Target: 20 samples per language (11 languages = 220 files)")
    print("\n💡 Strategy: Since torch/datasets has issues, we'll use a hybrid approach:")
    print("   1. Download parquet files using CLI")
    print("   2. Extract audio using a minimal datasets call\n")
    
    print("📋 Languages to fetch:")
    for code, name in LANGUAGE_MAP.items():
        print(f"   - {name} ({code})")
    
    print("\n⚠️ Due to Python 3.13 + torch compatibility issues,")
    print("   the best approach is to:")
    print("   1. Use HuggingFace CLI to download specific language parquet files")
    print("   2. Or add your own audio files directly to the 'data' folder")
    print("\n💡 Would you like me to create CLI commands for each language?")
    print("   Or you can manually add audio files (.wav, .mp3) to the 'data' folder.\n")

