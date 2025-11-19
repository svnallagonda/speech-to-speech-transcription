"""
Simplified version that uses huggingface_hub directly to avoid torch dependency issues.
Fetches audio files from ai4bharat/indicvoices_r dataset.
"""
import os
from huggingface_hub import snapshot_download, list_repo_files
import json
import requests

def fetch_with_api(languages=None, num_samples=2, output_dir="data"):
    """
    Alternative method: Use HuggingFace API directly to fetch samples.
    This avoids torch dependency issues.
    """
    print("⚠️ Note: This simplified version requires manual audio file download.")
    print("💡 Recommended: Use HuggingFace website or CLI to download dataset files directly.")
    print("\nYou can:")
    print("1. Visit: https://huggingface.co/datasets/ai4bharat/indicvoices_r")
    print("2. Or use: huggingface-cli download ai4bharat/indicvoices_r")
    print("\nThen place the audio files in the 'data' folder.")
    
    return []

if __name__ == "__main__":
    print("📥 To fetch audio files, you have two options:\n")
    print("OPTION 1: Use HuggingFace CLI (recommended):")
    print("  huggingface-cli login")
    print("  huggingface-cli download ai4bharat/indicvoices_r --repo-type dataset")
    print("\nOPTION 2: Manually download from:")
    print("  https://huggingface.co/datasets/ai4bharat/indicvoices_r\n")
    print("Then place the audio files in the 'data' folder.\n")

