#!/usr/bin/env python3
"""
Test workstream-specific configuration.
"""

import sys
from pathlib import Path

# Add mcp_server to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "mcp_server"))

from full_server import (
    find_project,
    suggest_files_for_workstream
)

print("=" * 70)
print("TESTING WORKSTREAM-SPECIFIC CONFIGURATION")
print("=" * 70)

# Test 1: Legacy AI - synthesis workstream
print("\n[TEST 1] Legacy AI - 'synthesis' workstream")
print("-" * 70)

project = find_project("Legacy AI")
if not project:
    print("❌ Project not found")
    sys.exit(1)

print(f"✅ Found project: {project['name']}")

# Check if workstream config exists
if "workstreams" in project and "synthesis" in project["workstreams"]:
    print("✅ Workstream config exists")
    ws_config = project["workstreams"]["synthesis"]
    print(f"   Description: {ws_config.get('description', 'N/A')}")
    print(f"   Always files: {ws_config.get('always_files', [])}")
    print(f"   Folders with latest: {ws_config.get('folders_with_latest', {})}")
else:
    print("❌ Workstream config NOT found")

# Get suggestions
print("\nGetting file suggestions...")
suggestions = suggest_files_for_workstream(project, "synthesis")

print(f"\n✅ Got {len(suggestions)} suggestions:")
for i, file_info in enumerate(suggestions, 1):
    print(f"   {i}. {file_info['name']}")
    print(f"      Path: {file_info['path']}")
    print(f"      Type: {file_info['type']}")

# Expected files:
expected_files = [
    "requirements-vision.md",
    "product-strategy.md",
    "segment-comparison-meta-analysis.md",
]

print("\n" + "-" * 70)
print("VALIDATION:")
print("-" * 70)

# Check if meta-analysis is included
meta_analysis_found = any("meta-analysis" in f["path"] for f in suggestions)
if meta_analysis_found:
    print("✅ Meta-analysis file found in suggestions")
else:
    print("❌ Meta-analysis file NOT found in suggestions")

# Check if we have 3 analyses files
analyses_files = [f for f in suggestions if "analyses/" in f["path"]]
if len(analyses_files) == 3:
    print(f"✅ Got exactly 3 files from analyses/ folder")
else:
    print(f"❌ Expected 3 analyses files, got {len(analyses_files)}")

# Check always files
always_found = [f for f in suggestions if f["type"] == "always"]
if len(always_found) >= 2:
    print(f"✅ Found {len(always_found)} always files")
else:
    print(f"❌ Expected at least 2 always files, got {len(always_found)}")

print("\n" + "=" * 70)

# Test 2: Legacy AI - interview-analysis workstream
print("\n[TEST 2] Legacy AI - 'interview-analysis' workstream")
print("-" * 70)

suggestions = suggest_files_for_workstream(project, "interview-analysis")
print(f"✅ Got {len(suggestions)} suggestions:")
for i, file_info in enumerate(suggestions, 1):
    print(f"   {i}. {file_info['name']}")

# Test 3: Legacy AI - unknown workstream (should fall back to heuristics)
print("\n[TEST 3] Legacy AI - 'unknown-workstream' (fallback to heuristics)")
print("-" * 70)

suggestions = suggest_files_for_workstream(project, "unknown-workstream")
print(f"✅ Got {len(suggestions)} suggestions (using generic heuristics)")
for i, file_info in enumerate(suggestions, 1):
    print(f"   {i}. {file_info['name']}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
