#!/usr/bin/env python3
"""
Test Handoff Workflow (Phase 7.4)

Tests the complete handoff workflow:
1. Detection on start_session()
2. Accept handoff → context loaded
3. Reject handoff → marked as rejected
4. Complete handoff → marked as completed
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.utils.handoff_detector import HandoffDetector


def test_handoff_detection():
    """Test A: Handoff detection finds pending handoffs."""
    print("\n" + "=" * 80)
    print("TEST A: HANDOFF DETECTION")
    print("=" * 80)

    repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
    detector = HandoffDetector(repo_path)

    # Scan for pending handoffs
    handoffs = detector.scan_for_handoffs(agent="claude-code", status="pending")

    print(f"\nFound {len(handoffs)} pending handoff(s)")

    if handoffs:
        for i, handoff in enumerate(handoffs, 1):
            print(f"\nHandoff {i}:")
            print(f"  File: {handoff['file_name']}")
            print(f"  Summary: {handoff.get('summary', 'No summary')}")
            print(f"  Type: {handoff.get('type', 'unknown')}")
            print(f"  Priority: {handoff.get('priority', 'unknown')}")
            print(f"  From: {handoff.get('from', 'unknown')}")

            # Validate handoff
            validation = detector.validate_handoff(handoff)
            print(f"  Valid: {validation['valid']}")

            if validation['warnings']:
                print(f"  Warnings: {validation['warnings']}")

        print("\n✅ TEST A PASSED: Handoff detection working")
        return True, handoffs[0]  # Return first handoff for further testing
    else:
        print("\n⚠️  TEST A SKIPPED: No pending handoffs found")
        print("Create a test handoff file to run full workflow tests")
        return False, None


def test_accept_handoff(handoff):
    """Test B: Accept handoff and load context."""
    print("\n" + "=" * 80)
    print("TEST B: ACCEPT HANDOFF")
    print("=" * 80)

    repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
    detector = HandoffDetector(repo_path)

    handoff_path = handoff.get("file_path")

    print(f"\nAccepting handoff: {handoff['file_name']}")

    # Mark as accepted
    success = detector.mark_handoff_status(
        handoff_path,
        "accepted",
        notes="Accepted by test suite"
    )

    if not success:
        print("✗ TEST B FAILED: Could not update handoff status")
        return False

    print("✓ Handoff status updated to 'accepted'")

    # Get context files
    context_files = detector.get_handoff_context_files(handoff)

    print(f"\nContext files to load: {len(context_files)}")
    for cf in context_files:
        exists = "✓" if cf.exists() else "✗"
        print(f"  {exists} {cf.relative_to(repo_path)}")

    # Re-parse handoff to verify status change
    updated_handoff = detector.parse_handoff_frontmatter(handoff_path)

    if updated_handoff.get("status") == "accepted":
        print("\n✅ TEST B PASSED: Handoff accepted successfully")
        return True
    else:
        print(f"\n✗ TEST B FAILED: Status not updated (current: {updated_handoff.get('status')})")
        return False


def test_reject_handoff(handoff):
    """Test C: Reject handoff with reason."""
    print("\n" + "=" * 80)
    print("TEST C: REJECT HANDOFF")
    print("=" * 80)

    repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
    detector = HandoffDetector(repo_path)

    handoff_path = handoff.get("file_path")

    print(f"\nRejecting handoff: {handoff['file_name']}")

    # Mark as rejected
    success = detector.mark_handoff_status(
        handoff_path,
        "rejected",
        notes="Test rejection - PRD needs more detail"
    )

    if not success:
        print("✗ TEST C FAILED: Could not update handoff status")
        return False

    print("✓ Handoff status updated to 'rejected'")

    # Re-parse handoff to verify status change
    updated_handoff = detector.parse_handoff_frontmatter(handoff_path)

    if updated_handoff.get("status") == "rejected":
        if "status_notes" in updated_handoff:
            print(f"✓ Rejection reason recorded: {updated_handoff['status_notes']}")
        print("\n✅ TEST C PASSED: Handoff rejected successfully")
        return True
    else:
        print(f"\n✗ TEST C FAILED: Status not updated (current: {updated_handoff.get('status')})")
        return False


def test_complete_handoff(handoff):
    """Test D: Complete handoff."""
    print("\n" + "=" * 80)
    print("TEST D: COMPLETE HANDOFF")
    print("=" * 80)

    repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
    detector = HandoffDetector(repo_path)

    handoff_path = handoff.get("file_path")

    # First, set back to accepted (simulating accepted workflow)
    detector.mark_handoff_status(handoff_path, "accepted")

    print(f"\nCompleting handoff: {handoff['file_name']}")

    # Mark as completed
    success = detector.mark_handoff_status(
        handoff_path,
        "completed",
        notes="Test completion - all work finished"
    )

    if not success:
        print("✗ TEST D FAILED: Could not update handoff status")
        return False

    print("✓ Handoff status updated to 'completed'")

    # Re-parse handoff to verify status change
    updated_handoff = detector.parse_handoff_frontmatter(handoff_path)

    if updated_handoff.get("status") == "completed":
        if "completed_at" in updated_handoff:
            print(f"✓ Completion timestamp recorded: {updated_handoff['completed_at']}")
        print("\n✅ TEST D PASSED: Handoff completed successfully")
        return True
    else:
        print(f"\n✗ TEST D FAILED: Status not updated (current: {updated_handoff.get('status')})")
        return False


def test_workflow_complete():
    """Test E: Full workflow (pending → accepted → completed)."""
    print("\n" + "=" * 80)
    print("TEST E: FULL WORKFLOW")
    print("=" * 80)

    repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
    detector = HandoffDetector(repo_path)

    # Create a test handoff file
    test_handoff_path = repo_path / "docs/handoffs/TEST-handoff-workflow.md"

    test_content = """---
to: claude-code
from: claude-chat
initiative_id: 2a68369c7305802ebbe6c355a80d65e5
prd_path: docs/prd/live-context-control-v3.3.md
priority: P2
type: implementation
status: pending
---

# Test Handoff: Workflow Testing

This is a test handoff created by the test suite to validate workflow.
"""

    # Create test handoff
    test_handoff_path.write_text(test_content, encoding='utf-8')
    print(f"✓ Created test handoff: {test_handoff_path.name}")

    # Step 1: Detect
    handoffs = detector.scan_for_handoffs(agent="claude-code", status="pending")
    test_handoff = None
    for h in handoffs:
        if h.get("file_name") == "TEST-handoff-workflow.md":
            test_handoff = h
            break

    if not test_handoff:
        print("✗ TEST E FAILED: Test handoff not detected")
        return False

    print(f"✓ Step 1: Detected test handoff (status: {test_handoff['status']})")

    # Step 2: Accept
    detector.mark_handoff_status(test_handoff_path, "accepted", notes="Test acceptance")
    updated = detector.parse_handoff_frontmatter(test_handoff_path)

    if updated.get("status") != "accepted":
        print("✗ TEST E FAILED: Accept step failed")
        return False

    print(f"✓ Step 2: Accepted (status: {updated['status']})")

    # Step 3: Complete
    detector.mark_handoff_status(test_handoff_path, "completed", notes="Test completion")
    updated = detector.parse_handoff_frontmatter(test_handoff_path)

    if updated.get("status") != "completed":
        print("✗ TEST E FAILED: Complete step failed")
        return False

    print(f"✓ Step 3: Completed (status: {updated['status']})")

    # Cleanup: Delete test handoff
    test_handoff_path.unlink()
    print("✓ Cleanup: Deleted test handoff")

    print("\n✅ TEST E PASSED: Full workflow working correctly")
    return True


def main():
    """Run all handoff workflow tests."""
    print("\n" + "=" * 80)
    print("HANDOFF WORKFLOW TEST SUITE (Phase 7.4)")
    print("=" * 80)

    results = {}

    # Test A: Detection
    detected, handoff = test_handoff_detection()
    results["Detection"] = detected

    if detected and handoff:
        # Tests B-D require an actual handoff
        # Note: These modify the handoff status, so we test in order:
        # B (accept), C (reject from accepted), D (complete from accepted)

        # Test B: Accept
        results["Accept"] = test_accept_handoff(handoff)

        # Test C: Reject (from accepted state)
        results["Reject"] = test_reject_handoff(handoff)

        # Test D: Complete (from accepted state)
        results["Complete"] = test_complete_handoff(handoff)

        # Restore handoff to pending state
        repo_path = Path.home() / "Documents/1. Projects/ai-assistant"
        detector = HandoffDetector(repo_path)
        detector.mark_handoff_status(handoff.get("file_path"), "pending", notes="Reset by test suite")
        print("\n✓ Restored handoff to 'pending' state")

    # Test E: Full workflow (independent test)
    results["Full Workflow"] = test_workflow_complete()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED: Handoff workflow working correctly")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED: Review results above")
        sys.exit(1)


if __name__ == "__main__":
    main()
