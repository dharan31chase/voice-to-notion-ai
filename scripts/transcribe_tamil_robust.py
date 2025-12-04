#!/usr/bin/env python3
"""
Robust Tamil Interview Transcription
- Timeout handling for API calls
- Unbuffered output for real-time progress
- Connection retry logic
"""

import os
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import time

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

load_dotenv()

# Create OpenAI client with timeout
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=300.0,  # 5 minute timeout per request
    max_retries=2
)

def split_with_ffmpeg(input_file, num_chunks=4):
    """Split audio with ffmpeg (fast and reliable)"""
    print(f"📂 Analyzing audio: {input_file}", flush=True)

    # Get duration
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        str(input_file)
    ], capture_output=True, text=True)

    total_duration = float(result.stdout.strip())
    chunk_duration = total_duration / num_chunks

    print(f"✂️ Splitting {total_duration/60:.1f} min into {num_chunks} chunks", flush=True)

    chunks_dir = Path(input_file).parent / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    chunks = []

    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_path = chunks_dir / f"chunk_{i+1}.mp3"

        subprocess.run([
            'ffmpeg', '-i', str(input_file),
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-c', 'copy',
            '-y',
            str(chunk_path)
        ], capture_output=True)

        size_mb = chunk_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Chunk {i+1}: {size_mb:.1f}MB ({chunk_duration/60:.1f} min)", flush=True)
        chunks.append(chunk_path)

    return chunks

def transcribe_chunk(chunk_path, language="ta", max_retries=3):
    """Transcribe with OpenAI API with timeout and retry"""
    for attempt in range(max_retries):
        try:
            print(f"🎙️ Transcribing {chunk_path.name} (attempt {attempt+1}/{max_retries})...", flush=True)
            start_time = time.time()

            with open(chunk_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language
                )

            elapsed = time.time() - start_time
            print(f"  ✓ Complete in {elapsed:.1f}s ({len(transcript.text)} chars)", flush=True)
            return transcript.text

        except Exception as e:
            print(f"  ✗ Failed: {e}", flush=True)
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"  ⏱️  Retrying in {wait_time}s...", flush=True)
                time.sleep(wait_time)
            else:
                print(f"  ❌ All {max_retries} attempts failed", flush=True)
                raise
    return ""

def translate_text(tamil_text):
    """Translate Tamil to English with GPT-4"""
    print(f"\n🌍 Translating to English...", flush=True)

    # Split into manageable chunks
    max_chars = 8000
    chunks = []
    words = tamil_text.split()
    current = []
    current_len = 0

    for word in words:
        if current_len + len(word) > max_chars and current:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + 1

    if current:
        chunks.append(" ".join(current))

    print(f"  Translating in {len(chunks)} parts...", flush=True)

    translations = []
    for i, chunk in enumerate(chunks, 1):
        try:
            print(f"  Part {i}/{len(chunks)}...", flush=True)
            start_time = time.time()

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Translate this Tamil interview transcript to English. Preserve meaning and tone."},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.3
            )

            elapsed = time.time() - start_time
            translation = response.choices[0].message.content
            translations.append(translation)
            print(f"    ✓ Part {i} complete in {elapsed:.1f}s ({len(translation)} chars)", flush=True)

        except Exception as e:
            print(f"    ✗ Part {i} failed: {e}", flush=True)
            translations.append(f"[Translation failed for part {i}]")

    result = "\n\n".join(translations)
    print(f"  ✓ Translation complete ({len(result)} chars)", flush=True)
    return result

def main():
    input_file = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/staging/251201_0526.mp3")
    output_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai/research/customer-interviews/legacy-interviews")

    print("=" * 60, flush=True)
    print("Tamil Interview Transcription (Robust Method)", flush=True)
    print("=" * 60, flush=True)
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("=" * 60, flush=True)

    try:
        # Step 1: Split audio
        print("\n[1/5] Splitting audio...", flush=True)
        chunks = split_with_ffmpeg(input_file, num_chunks=8)

        # Step 2: Transcribe all chunks
        print(f"\n[2/5] Transcribing {len(chunks)} chunks...", flush=True)
        transcripts = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\n  Chunk {i}/{len(chunks)}:", flush=True)
            transcript = transcribe_chunk(chunk, language="ta")
            transcripts.append(transcript)

        # Step 3: Combine
        print(f"\n[3/5] Combining Tamil transcripts...", flush=True)
        tamil_text = "\n\n".join(transcripts)
        print(f"  ✓ Combined: {len(tamil_text)} chars", flush=True)

        # Step 4: Translate
        print(f"\n[4/5] Translating to English...", flush=True)
        english_text = translate_text(tamil_text)

        # Step 5: Save
        print(f"\n[5/5] Saving files...", flush=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        tamil_file = output_dir / "aya_interview_tamil.txt"
        tamil_file.write_text(tamil_text, encoding='utf-8')
        print(f"  ✓ Tamil:   {tamil_file}", flush=True)

        english_file = output_dir / "aya_interview_english.txt"
        english_file.write_text(english_text, encoding='utf-8')
        print(f"  ✓ English: {english_file}", flush=True)

        # Cleanup
        print(f"\n🧹 Cleaning up chunks...", flush=True)
        for chunk in chunks:
            chunk.unlink()
        chunks[0].parent.rmdir()

        print("\n" + "=" * 60, flush=True)
        print("✅ COMPLETE", flush=True)
        print("=" * 60, flush=True)
        print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("=" * 60, flush=True)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
