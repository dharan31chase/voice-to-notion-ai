#!/usr/bin/env python3
"""
Manual test script for context loader functions.
Run with: python test_context_manual.py
"""

import sys
from pathlib import Path

# Add mcp_server to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "mcp_server"))

from full_server import (
    parse_user_selection,
    classify_file_type,
    find_project
)

print("=" * 60)
print("TESTING CONTEXT LOADER FUNCTIONS")
print("=" * 60)

# Test 1: parse_user_selection
print("\n[TEST 1] parse_user_selection")
print("-" * 40)

options = [{"path": "file1.md"}, {"path": "file2.md"}, {"path": "file3.md"}]

try:
    result = parse_user_selection("1,2,3", options)
    assert result == [0, 1, 2], f"Expected [0,1,2], got {result}"
    print("✅ Test '1,2,3': PASS")
except AssertionError as e:
    print(f"❌ Test '1,2,3': FAIL - {e}")

try:
    result = parse_user_selection("all", options)
    assert result == [0, 1, 2], f"Expected [0,1,2], got {result}"
    print("✅ Test 'all': PASS")
except AssertionError as e:
    print(f"❌ Test 'all': FAIL - {e}")

try:
    result = parse_user_selection("", options)
    assert result == [0, 1, 2], f"Expected [0,1,2], got {result}"
    print("✅ Test '' (empty): PASS")
except AssertionError as e:
    print(f"❌ Test '' (empty): FAIL - {e}")

try:
    result = parse_user_selection("1,3", options)
    assert result == [0, 2], f"Expected [0,2], got {result}"
    print("✅ Test '1,3': PASS")
except AssertionError as e:
    print(f"❌ Test '1,3': FAIL - {e}")

try:
    parse_user_selection("1,5", options)
    print("❌ Test invalid index: FAIL - Should have raised ValueError")
except ValueError:
    print("✅ Test invalid index: PASS (ValueError raised)")

# Test 2: classify_file_type
print("\n[TEST 2] classify_file_type")
print("-" * 40)

tests = [
    ("requirements-vision.md", "always"),
    ("docs/roadmap.md", "always"),
    ("product-strategy.md", "always"),
    ("interview-guide-exemplar.md", "exemplar"),
    ("bob-missy-analysis.md", "exemplar"),
    ("segment-meta-analysis.md", "synthesis"),
    ("comparison-report.md", "synthesis"),
    ("random-notes.md", "optional"),
]

for file_path, expected_type in tests:
    result = classify_file_type(file_path)
    if result == expected_type:
        print(f"✅ {file_path} → {expected_type}: PASS")
    else:
        print(f"❌ {file_path} → Expected {expected_type}, got {result}: FAIL")

# Test 3: find_project
print("\n[TEST 3] find_project")
print("-" * 40)

test_cases = [
    ("Legacy AI", "Legacy AI"),
    ("customer discovery", "Legacy AI"),
    ("legacy ai", "Legacy AI"),
    ("legacy", "Legacy AI"),
    ("Epic 2nd Brain", "Epic 2nd Brain"),
    ("ai-assistant", "Epic 2nd Brain"),
    ("mcp", "Epic 2nd Brain"),
]

for input_name, expected_name in test_cases:
    project = find_project(input_name)
    if project and project["name"] == expected_name:
        print(f"✅ '{input_name}' → {expected_name}: PASS")
    elif project is None:
        print(f"❌ '{input_name}' → Expected {expected_name}, got None: FAIL")
    else:
        print(f"❌ '{input_name}' → Expected {expected_name}, got {project['name']}: FAIL")

# Test not found
project = find_project("Nonexistent Project")
if project is None:
    print("✅ 'Nonexistent Project' → None: PASS")
else:
    print(f"❌ 'Nonexistent Project' → Expected None, got {project['name']}: FAIL")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All core functions tested. Check results above.")
print("If all tests pass, implementation is ready for MCP server integration.")
print("=" * 60)
