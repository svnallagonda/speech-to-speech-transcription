# Module 1 — Environment & Basic Translation Test

## Goal
Set up environment, install dependencies, and run a basic translation test (Hindi ↔ English) using `transformers` pipeline and a small model (Helsinki-NLP) to confirm tokenization, model loading and inference work.

## Quick Start (Local — VS Code)

### 1. Create virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the test
```bash
python test_env.py
```

**Expected output:** Model downloads (first run), then printed translations with timing information and BLEU scores.

---

## Quick Start (Google Colab)

Open a new Colab notebook and run these cells sequentially:

### Cell 1 — Install dependencies
```python
# Colab: install exact versions that are Colab-friendly
!pip install -q torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
!pip install -q transformers==4.36.2 sentencepiece==0.1.99 sacrebleu==2.3.1 huggingface-hub==0.18.1
```

### Cell 2 — Upload sample file (or create)
```python
%%bash
cat > sample_texts.csv <<'CSV'
id,text,lang
1,"Hello, how are you?","en"
2,"नमस्ते, आप कैसे हैं?","hi"
3,"Good morning, everyone","en"
4,"क्या आप आज उपलब्ध हैं?","hi"
CSV
```

### Cell 3 — Quick test
```python
from transformers import pipeline
hi_en = pipeline("translation", model="Helsinki-NLP/opus-mt-hi-en")
print(hi_en("नमस्ते, आप कैसे हैं?"))
```

> **Note:** If GPU runtime is available, Colab will use it automatically. For these small models, CPU is fine.

---

## Hugging Face Authentication (Optional)

If you need access to large or private models:

**Local terminal:**
```bash
huggingface-cli login
# or export in shell
export HUGGINGFACE_HUB_TOKEN="hf_xxx"
```

**In Colab:**
```python
from huggingface_hub import notebook_login
notebook_login()
```

---

## Project Structure
```
speech-translator/
├─ module1/
│  ├─ README.md              # This file
│  ├─ requirements.txt       # Python dependencies
│  ├─ test_env.py           # Quick command-line test
│  ├─ colab_setup.ipynb     # Optional Colab notebook
│  └─ sample_texts.csv      # Tiny sample phrases
```

---

## Purpose
Validate that transformers pipelines can be loaded and perform Hindi↔English translation on sample phrases.

## Models Used
- **Helsinki-NLP/opus-mt-hi-en**: Hindi → English translation
- **Helsinki-NLP/opus-mt-en-hi**: English → Hindi translation

These are lightweight models suitable for CPU inference and testing.

---

## Common Problems & Fixes

### Out of memory / crash on load
→ Use smaller models (`opus-mt` are small). If using Whisper/large models, use GPU instance or Whisper tiny/small.

### Version conflicts (torch / transformers)
→ Use the locked versions from `requirements.txt`. If you see `ImportError`, reinstall `transformers` matching your `torch`.

### Model download blocked
→ Authenticate with HF token if model requires it. Check network/proxy.

### Sacrebleu error
→ Ensure `sacrebleu` is installed (included in requirements.txt). For corpus BLEU, inputs must be lists of equal length.

---

## Caching Models

Models are cached at `~/.cache/huggingface/transformers`. For CI or ephemeral runners, mount a volume to persist cache. For Docker builds, do not install large models into image. Instead pull models at container start and use a shared PV in prod (AKS) or pre-warm node images (AMI).

---

## Next Steps

After confirming Module 1 works:
- **Module 2**: Audio conversion, pydub, speech_recognition/Whisper examples
- **Module 3**: Integration and deployment

