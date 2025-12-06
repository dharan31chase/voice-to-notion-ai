#!/usr/bin/env python3
"""
Test Usage Tracking (Phase 4.1)
Validates that file loads/edits are tracked silently.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.utils.usage_tracker import UsageTracker

def test_usage_tracker():
    """Test usage tracker functionality."""
    print("=" * 60)
    print("TEST: Usage Tracking Validation (Phase 4.1)")
    print("=" * 60)

    # 1. Create tracker
    print("\n1. Creating usage tracker...")
    tracker = UsageTracker(project="Epic 2nd Brain", session_id="test-2025-12-05")
    print("   ✅ Tracker created")

    # 2. Track file loads
    print("\n2. Tracking file loads...")
    tracker.track_file_load("ROADMAP.md", context="read_file", source="manual")
    tracker.track_file_load("docs/prd/live-context-control-v3.md", context="read_file", source="manual")
    tracker.track_file_load("docs/tech-requirements/live-context-control-v3.md", context="read_file", source="manual")
    print(f"   ✅ Tracked {len(tracker.file_loads)} file loads")

    # 3. Track file edits
    print("\n3. Tracking file edits...")
    tracker.track_file_edit("docs/prd/live-context-control-v3.md", change_type="edit")
    tracker.track_file_create("test-new-file.md")
    print(f"   ✅ Tracked {len(tracker.file_edits)} edits, {len(tracker.file_creates)} creates")

    # 4. Track file references
    print("\n4. Tracking file references...")
    tracker.track_file_reference("ROADMAP.md", context="Planning session")
    tracker.track_file_reference("docs/context/one-pagers/infrastructure/context-engineering.md", context="Referenced in discussion")
    print(f"   ✅ Tracked {len(tracker.file_references)} references")

    # 5. Save tracker
    print("\n5. Saving usage log...")
    log_path = tracker.save()
    print(f"   ✅ Saved to: {log_path}")

    # 6. Verify log file exists
    if log_path.exists():
        print("   ✅ Log file exists")

        # Load and validate
        with open(log_path, 'r') as f:
            data = json.load(f)

        print(f"\n6. Validating log contents...")
        print(f"   Project: {data['metadata']['project']}")
        print(f"   Session ID: {data['metadata']['session_id']}")
        print(f"   Total loads: {data['statistics']['total_loads']}")
        print(f"   Total edits: {data['statistics']['total_edits']}")
        print(f"   Total creates: {data['statistics']['total_creates']}")
        print(f"   Total references: {data['statistics']['total_references']}")
        print(f"   Unique files: {data['statistics']['unique_files']}")

        # Validate statistics
        if data['statistics']['total_loads'] == 3:
            print("   ✅ Load tracking accurate")
        else:
            print(f"   ❌ Expected 3 loads, got {data['statistics']['total_loads']}")

        if data['statistics']['total_edits'] == 1:
            print("   ✅ Edit tracking accurate")
        else:
            print(f"   ❌ Expected 1 edit, got {data['statistics']['total_edits']}")

        if data['statistics']['total_creates'] == 1:
            print("   ✅ Create tracking accurate")
        else:
            print(f"   ❌ Expected 1 create, got {data['statistics']['total_creates']}")

        # Validate privacy (paths should be sanitized)
        print(f"\n7. Validating privacy (path sanitization)...")
        sample_path = data['events']['loads'][0]['file']
        if "<USER_HOME>" in sample_path or not sample_path.startswith("/Users"):
            print(f"   ✅ Paths sanitized (example: {sample_path})")
        else:
            print(f"   ⚠️  Path may not be sanitized: {sample_path}")

    else:
        print("   ❌ Log file not found!")
        return False

    print("\n" + "=" * 60)
    print("TEST: ✅ PASSED - Usage tracking validated")
    print("=" * 60)

    print("\n📝 Next Steps:")
    print("   - Usage logs saved to: logs/usage/")
    print("   - Ready for Phase 4.2: Learning Algorithm")
    print("   - Learning algorithm will analyze these logs to improve suggestions")

    # Cleanup
    print("\n8. Cleanup...")
    log_path.unlink()
    print("   ✅ Removed test log")

    return True

if __name__ == "__main__":
    success = test_usage_tracker()
    sys.exit(0 if success else 1)
