#!/usr/bin/env python3
"""
Simple Tamil Interview Transcription - No dependencies except OpenAI
Uses ffmpeg to split, then OpenAI API to transcribe and translate
"""

import os
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def split_with_ffmpeg(input_file, num_chunks=4):
    """Split audio with ffmpeg (fast and reliable)"""
    print(f"📂 Analyzing audio: {input_file}")

    # Get duration
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        str(input_file)
    ], capture_output=True, text=True)

    total_duration = float(result.stdout.strip())
    chunk_duration = total_duration / num_chunks

    print(f"✂️ Splitting {total_duration/60:.1f} min into {num_chunks} chunks")

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
        print(f"  ✓ Chunk {i+1}: {size_mb:.1f}MB ({chunk_duration/60:.1f} min)")
        chunks.append(chunk_path)

    return chunks

def transcribe_chunk(chunk_path, language="ta", max_retries=3):
    """Transcribe with OpenAI API"""
    for attempt in range(max_retries):
        try:
            print(f"🎙️ Transcribing {chunk_path.name} (attempt {attempt+1})...")
            with open(chunk_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language
                )
            print(f"  ✓ Complete ({len(transcript.text)} chars)")
            return transcript.text
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise
    return ""

def translate_text(tamil_text):
    """Translate Tamil to English with GPT-4"""
    print(f"\n🌍 Translating to English...")

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

    print(f"  Translating in {len(chunks)} parts...")

    translations = []
    for i, chunk in enumerate(chunks, 1):
        try:
            print(f"  Part {i}/{len(chunks)}...")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Translate this Tamil interview transcript to English. Preserve meaning and tone."},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.3
            )
            translations.append(response.choices[0].message.content)
        except Exception as e:
            print(f"  ✗ Part {i} failed: {e}")
            translations.append(f"[Translation failed for part {i}]")

    result = "\n\n".join(translations)
    print(f"  ✓ Complete ({len(result)} chars)")
    return result

def main():
    input_file = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/staging/251201_0526.mp3")
    output_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai/research/customer-interviews/legacy-interviews")

    print("=" * 60)
    print("Tamil Interview Transcription (Simple Method)")
    print("=" * 60)

    try:
        # Step 1: Split audio
        chunks = split_with_ffmpeg(input_file, num_chunks=4)

        # Step 2: Transcribe all chunks
        print(f"\n🎙️ Transcribing {len(chunks)} chunks...")
        transcripts = []
        for chunk in chunks:
            transcript = transcribe_chunk(chunk, language="ta")
            transcripts.append(transcript)

        # Step 3: Combine
        tamil_text = "\n\n".join(transcripts)
        print(f"\n✓ Combined Tamil transcript: {len(tamil_text)} chars")

        # Step 4: Translate
        english_text = translate_text(tamil_text)

        # Step 5: Save
        output_dir.mkdir(parents=True, exist_ok=True)

        tamil_file = output_dir / "aya_interview_tamil.txt"
        tamil_file.write_text(tamil_text, encoding='utf-8')

        english_file = output_dir / "aya_interview_english.txt"
        english_file.write_text(english_text, encoding='utf-8')

        # Step 6: Cleanup
        print(f"\n🧹 Cleaning up chunks...")
        for chunk in chunks:
            chunk.unlink()
        chunks[0].parent.rmdir()

        print("\n" + "=" * 60)
        print("✅ COMPLETE")
        print("=" * 60)
        print(f"Tamil:   {tamil_file}")
        print(f"English: {english_file}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
