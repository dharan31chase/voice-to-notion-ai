#!/usr/bin/env python3
"""
Test 2: Backup System Validation (Phase 1)
Validates auto-backup before overwriting files.
"""

import os
import sys
from pathlib import Path

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.full_server import write_file

def test_backup_system():
    """Test auto-backup functionality."""
    print("=" * 60)
    print("TEST 2: Backup System Validation")
    print("=" * 60)

    # 1. Create test file
    print("\n1. Creating initial test file...")
    result1 = write_file("test-backup.md", "Version 1 content", project="Epic 2nd Brain")
    print(f"   ✅ Created: {result1['message']}")

    # 2. Overwrite it (should create backup)
    print("\n2. Overwriting file (should trigger backup)...")
    result2 = write_file("test-backup.md", "Version 2 content", project="Epic 2nd Brain")
    print(f"   Result: {result2}")

    # 3. Check if backup was created
    if "backup_created" in result2:
        print(f"\n   ✅ Backup created: {result2['backup_created']}")
    else:
        print("\n   ❌ FAILED: No backup was created!")
        return False

    # 4. Verify backup exists
    print("\n3. Verifying backup file exists...")
    backup_dir = Path.home() / "Documents/1. Projects/ai-assistant/.backups"

    if backup_dir.exists():
        backups = list(backup_dir.glob("test-backup.md.*"))
        print(f"   Found {len(backups)} backup(s):")
        for backup in backups:
            print(f"   - {backup.name}")

        if backups:
            print("\n   ✅ Backup system working correctly!")

            # 5. Verify backup content
            backup_content = backups[0].read_text()
            if backup_content == "Version 1 content":
                print("   ✅ Backup contains original content (Version 1)")
            else:
                print(f"   ⚠️  Backup content mismatch: {backup_content}")

            return True
        else:
            print("\n   ❌ FAILED: Backup directory exists but no backups found!")
            return False
    else:
        print(f"\n   ❌ FAILED: Backup directory doesn't exist: {backup_dir}")
        return False

if __name__ == "__main__":
    success = test_backup_system()

    print("\n" + "=" * 60)
    if success:
        print("TEST 2: ✅ PASSED - Backup system validated successfully")
    else:
        print("TEST 2: ❌ FAILED - Backup system not working")
    print("=" * 60)

    # Cleanup
    print("\n4. Cleanup...")
    test_file = Path.home() / "Documents/1. Projects/ai-assistant/test-backup.md"
    if test_file.exists():
        test_file.unlink()
        print("   ✅ Removed test file")

    backup_dir = Path.home() / "Documents/1. Projects/ai-assistant/.backups"
    if backup_dir.exists():
        for backup in backup_dir.glob("test-backup.md.*"):
            backup.unlink()
            print(f"   ✅ Removed backup: {backup.name}")

    sys.exit(0 if success else 1)
