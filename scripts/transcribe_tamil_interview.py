#!/usr/bin/env python3
"""
Tamil Interview Transcription & Translation Script
Splits large audio file, transcribes via OpenAI API, and translates to English
"""

import os
import sys
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def split_audio(input_file, num_chunks=4):
    """Split audio file into equal chunks"""
    print(f"📂 Loading audio file: {input_file}")
    audio = AudioSegment.from_mp3(input_file)
    total_duration = len(audio)
    chunk_duration = total_duration // num_chunks

    chunks = []
    output_dir = Path(input_file).parent / "chunks"
    output_dir.mkdir(exist_ok=True)

    print(f"✂️ Splitting into {num_chunks} chunks (~{chunk_duration/1000/60:.1f} min each)")

    for i in range(num_chunks):
        start = i * chunk_duration
        end = start + chunk_duration if i < num_chunks - 1 else total_duration

        chunk = audio[start:end]
        chunk_path = output_dir / f"chunk_{i+1}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)

        size_mb = chunk_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Chunk {i+1}: {size_mb:.1f}MB ({(end-start)/1000/60:.1f} min)")

    return chunks

def transcribe_chunk(chunk_path, language="ta", max_retries=3):
    """Transcribe a single chunk with retry logic"""
    chunk_name = chunk_path.name

    for attempt in range(max_retries):
        try:
            print(f"🎙️ Transcribing {chunk_name} (attempt {attempt+1}/{max_retries})...")

            with open(chunk_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )

            print(f"  ✓ {chunk_name} complete ({len(transcript)} chars)")
            return transcript

        except Exception as e:
            print(f"  ✗ {chunk_name} failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"  ⏱️ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ {chunk_name} failed after {max_retries} attempts")
                raise

def transcribe_all_chunks(chunks, language="ta"):
    """Transcribe all chunks sequentially"""
    print(f"\n🎙️ Starting transcription ({len(chunks)} chunks, language: {language})")
    transcripts = []

    start_time = time.time()

    for i, chunk_path in enumerate(chunks, 1):
        transcript = transcribe_chunk(chunk_path, language=language)
        transcripts.append(transcript)
        print(f"  Progress: {i}/{len(chunks)} chunks complete")

    elapsed = time.time() - start_time
    print(f"\n✓ All transcription complete in {elapsed/60:.1f} minutes")

    return transcripts

def combine_transcripts(transcripts):
    """Combine all transcript chunks into single text"""
    print(f"\n📝 Combining {len(transcripts)} transcripts...")
    combined = "\n\n".join(transcripts)
    print(f"  ✓ Combined transcript: {len(combined)} chars")
    return combined

def translate_to_english(tamil_text, max_chunk_size=4000):
    """Translate Tamil text to English using GPT-4"""
    print(f"\n🌍 Translating to English...")

    # Split into chunks if text is too long
    chunks = []
    words = tamil_text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    print(f"  Translating in {len(chunks)} chunks...")

    translations = []
    for i, chunk in enumerate(chunks, 1):
        try:
            print(f"  Translating chunk {i}/{len(chunks)}...")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following Tamil text to English. Preserve the meaning, tone, and context. This is an interview transcript."},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.3
            )
            translation = response.choices[0].message.content
            translations.append(translation)
            print(f"    ✓ Chunk {i} translated ({len(translation)} chars)")
        except Exception as e:
            print(f"    ✗ Chunk {i} failed: {e}")
            # Add placeholder to maintain structure
            translations.append(f"[Translation failed for chunk {i}]")

    combined_translation = "\n\n".join(translations)
    print(f"  ✓ Translation complete: {len(combined_translation)} chars")
    return combined_translation

def save_transcripts(tamil_text, english_text, output_dir):
    """Save both Tamil and English transcripts"""
    print(f"\n💾 Saving transcripts to {output_dir}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save Tamil
    tamil_file = output_path / "aya_interview_tamil.txt"
    tamil_file.write_text(tamil_text, encoding='utf-8')
    print(f"  ✓ Tamil: {tamil_file}")

    # Save English
    english_file = output_path / "aya_interview_english.txt"
    english_file.write_text(english_text, encoding='utf-8')
    print(f"  ✓ English: {english_file}")

    return tamil_file, english_file

def cleanup_chunks(chunks):
    """Clean up temporary chunk files"""
    print(f"\n🧹 Cleaning up {len(chunks)} temporary chunk files...")
    for chunk in chunks:
        try:
            chunk.unlink()
            print(f"  ✓ Deleted {chunk.name}")
        except Exception as e:
            print(f"  ✗ Failed to delete {chunk.name}: {e}")

    # Remove chunks directory if empty
    chunks_dir = chunks[0].parent
    try:
        if not any(chunks_dir.iterdir()):
            chunks_dir.rmdir()
            print(f"  ✓ Removed empty directory: {chunks_dir}")
    except:
        pass

def main():
    # Configuration
    input_file = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/staging/251201_0526.mp3")
    output_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai/research/customer-interviews/legacy-interviews")

    print("=" * 60)
    print("Tamil Interview Transcription & Translation")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")
    print(f"Language: Tamil → English")
    print("=" * 60)

    try:
        # Step 1: Split audio into chunks
        chunks = split_audio(input_file, num_chunks=4)

        # Step 2: Transcribe all chunks (Tamil)
        transcripts = transcribe_all_chunks(chunks, language="ta")

        # Step 3: Combine transcripts
        tamil_text = combine_transcripts(transcripts)

        # Step 4: Translate to English
        english_text = translate_to_english(tamil_text)

        # Step 5: Save both versions
        tamil_file, english_file = save_transcripts(tamil_text, english_text, output_dir)

        # Step 6: Cleanup temporary files
        cleanup_chunks(chunks)

        print("\n" + "=" * 60)
        print("✅ COMPLETE")
        print("=" * 60)
        print(f"Tamil transcript: {tamil_file}")
        print(f"English translation: {english_file}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
