#!/usr/bin/env python3
"""
Analyze transcript file endings to understand metadata patterns.
"""

from pathlib import Path
import sys

failed_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/Failed/failed_transcripts")

# Get all 251*.txt files (recent ones)
files = sorted(failed_dir.glob("251*.txt"))

print(f"Found {len(files)} transcript files to analyze\n")
print("="*80)

for i, file_path in enumerate(files[:15], 1):  # Analyze first 15
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        words = len(content.split())
        lines = content.strip().split('\n')

        print(f"\n{i}. FILE: {file_path.name}")
        print(f"   WORDS: {words}")
        print(f"   LAST 10 LINES:")

        for line in lines[-10:]:
            print(f"      {line}")

        print("-"*80)

    except Exception as e:
        print(f"   ERROR: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
