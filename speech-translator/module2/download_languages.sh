#!/bin/bash
# HuggingFace CLI commands to download language-specific files
# Note: English (en) is not in indicvoices_r dataset

echo "📥 Downloading audio dataset files for 11 languages..."

# Languages: hi, pa, mr, kn, te, ta, gu, ml, bn, or, ur
# We'll download parquet files for each language

LANGUAGES=("Hindi" "Punjabi" "Marathi" "Kannada" "Telugu" "Tamil" "Gujarati" "Malayalam" "Bengali" "Odia" "Urdu")

for lang in "${LANGUAGES[@]}"; do
    echo "📥 Downloading $lang..."
    huggingface-cli download ai4bharat/indicvoices_r --repo-type dataset \
        --local-dir "./datasets_cache/$lang" \
        --include "$lang/*.parquet"
done

echo "✅ Download complete! Files saved in ./datasets_cache/"

