#!/usr/bin/env python3
"""
Analyze successful processed transcripts to understand patterns.
"""

import json
from pathlib import Path

processed_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/processed")

# Get JSON files
files = sorted(processed_dir.glob("*.json"))[:10]

print(f"Found {len(files)} successful transcripts to analyze\n")
print("="*80)

for i, file_path in enumerate(files, 1):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        content = data.get('content', '')
        category = data.get('category', 'unknown')
        words = len(content.split())
        lines = content.strip().split('\n')

        print(f"\n{i}. FILE: {file_path.name}")
        print(f"   CATEGORY: {category}")
        print(f"   WORDS: {words}")
        print(f"   LAST 8 LINES:")

        for line in lines[-8:]:
            print(f"      {line}")

        print("-"*80)

    except Exception as e:
        print(f"   ERROR: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
