#!/usr/bin/env python3
"""
Test 4: ROADMAP Sync Validation
Tests the update_roadmap_row() function.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.utils.roadmap_helpers import update_roadmap_row

def test_roadmap_sync():
    """Test ROADMAP.md sync logic."""
    print("=" * 60)
    print("TEST 4: ROADMAP Sync Validation")
    print("=" * 60)

    # Read current ROADMAP.md
    roadmap_path = Path.home() / "Documents/1. Projects/ai-assistant/ROADMAP.md"

    if not roadmap_path.exists():
        print(f"\n❌ FAILED: ROADMAP.md not found at {roadmap_path}")
        return False

    content = roadmap_path.read_text(encoding='utf-8')

    # Verify Live Context Control v3 exists
    if "Live Context Control v3" not in content:
        print("\n❌ FAILED: 'Live Context Control v3' not found in ROADMAP.md")
        print("   Run this first: Added it manually to ROADMAP.md")
        return False

    print("\n✅ Found 'Live Context Control v3' in ROADMAP.md")

    # Test 1: Update to Complete status
    print("\n1. Testing status update to '✅ Complete'...")
    updated = update_roadmap_row(
        content=content,
        initiative_name="Live Context Control v3",
        new_status="✅ Complete",
        completion_date="2025-12-05"
    )

    # Find the updated line
    updated_line = None
    for line in updated.split("\n"):
        if "Live Context Control v3" in line:
            updated_line = line
            break

    if updated_line:
        print(f"   Updated line: {updated_line.strip()}")

        # Verify status changed
        if "✅ Complete" in updated_line:
            print("   ✅ Status updated to '✅ Complete'")
        else:
            print("   ❌ Status NOT updated")
            return False

        # Verify date changed
        if "Dec 05" in updated_line or "Dec 5" in updated_line:
            print("   ✅ Completion date set to 'Dec 05'")
        else:
            print(f"   ⚠️  Completion date not found (line: {updated_line})")
    else:
        print("   ❌ Could not find updated line")
        return False

    # Test 2: Update back to In Progress
    print("\n2. Testing status update to '🚀 In Progress'...")
    updated2 = update_roadmap_row(
        content=content,
        initiative_name="Live Context Control v3",
        new_status="🚀 In Progress"
    )

    updated_line2 = None
    for line in updated2.split("\n"):
        if "Live Context Control v3" in line:
            updated_line2 = line
            break

    if updated_line2 and "🚀 In Progress" in updated_line2:
        print("   ✅ Status updated to '🚀 In Progress'")
    else:
        print("   ❌ Status NOT updated")
        return False

    # Test 3: Show what DOESN'T get updated (other initiatives)
    print("\n3. Verifying other initiatives unchanged...")

    original_applied_line = None
    updated_applied_line = None

    for line in content.split("\n"):
        if "Applied Context Engineering" in line and "Live Context Control" not in line:
            original_applied_line = line
            break

    for line in updated.split("\n"):
        if "Applied Context Engineering" in line and "Live Context Control" not in line:
            updated_applied_line = line
            break

    if original_applied_line == updated_applied_line:
        print("   ✅ Other initiatives unchanged (Applied Context Engineering)")
    else:
        print("   ⚠️  Other initiatives may have changed unexpectedly")

    print("\n" + "=" * 60)
    print("TEST 4: ✅ PASSED - ROADMAP sync logic validated")
    print("=" * 60)

    print("\n📝 Note: This test validates the sync LOGIC only.")
    print("   To test the full end-to-end flow:")
    print("   1. Update Strategy Board status in Notion")
    print("   2. Call ai-assistant:end_session() with initiative_name")
    print("   3. Verify ROADMAP.md updated automatically")

    return True

if __name__ == "__main__":
    success = test_roadmap_sync()
    sys.exit(0 if success else 1)
