# LAYLA2

A clean local-first foundation for Layla.

## Architecture

LAYLA2 → llama.cpp → SmolLM2-135M-Instruct-Q4_K_M.gguf → Layla Chat → Memory → Voice/Files → Android APK

## Phase 1

Phase 1 only tests local GGUF inference.

No cloud API is required by the test program.

## Model

Expected model:

`models/SmolLM2-135M-Instruct-Q4_K_M.gguf`

The GGUF model is intentionally excluded from Git because it is a large binary file.

## Current Files

- `main.py` — local Layla inference test
- `requirements.txt` — Python dependency
- `.gitignore` — keeps model/build files out of Git
- `.github/workflows/test.yml` — GitHub Actions project check

## Next Steps

1. Test the local GGUF model
2. Build Layla chat UI
3. Add persistent memory
4. Add voice
5. Add file/photo/video support
6. Prepare Android APK
