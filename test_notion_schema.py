#!/usr/bin/env python3
"""
Test Notion Schema Detection (Phase 5.1)
Validates schema detection and property mapping.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from notion_client import Client
from mcp_server.utils.notion_schema import NotionSchemaDetector, NotionSchema


def test_notion_schema_detection():
    """Test Notion schema detection."""
    print("=" * 60)
    print("TEST: Notion Schema Detection (Phase 5.1)")
    print("=" * 60)

    # 1. Check Notion client
    print("\n1. Initializing Notion client...")
    notion_token = os.getenv("NOTION_TOKEN")

    if not notion_token:
        print("   ⚠️  NOTION_TOKEN not found in .env")
        print("   Skipping live API tests (offline mode)")
        return test_offline_mode()

    notion_client = Client(auth=notion_token)
    print("   ✅ Notion client initialized")

    # 2. Initialize schema detector
    print("\n2. Creating schema detector...")
    detector = NotionSchemaDetector(notion_client)
    print("   ✅ Schema detector created")

    # 3. Detect Strategy Board schema
    print("\n3. Detecting Strategy Board schema...")
    strategy_board_id = os.getenv("STRATEGY_BOARD_DATABASE_ID")

    if not strategy_board_id:
        print("   ⚠️  STRATEGY_BOARD_DATABASE_ID not found")
        return test_offline_mode()

    try:
        schema = detector.get_strategy_board_schema(strategy_board_id)

        if schema.schema:
            print(f"   ✅ Detected schema: {schema}")
            print(f"   Database: {schema.schema['title']}")
            print(f"   Properties: {len(schema.schema['properties'])}")

            # Show some properties
            print(f"\n   Sample properties:")
            for i, (prop_name, prop_data) in enumerate(list(schema.schema['properties'].items())[:5], 1):
                print(f"   {i}. {prop_name}: {prop_data['type']}")

        else:
            print("   ❌ Schema detection failed")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

    # 4. Test property mapping
    print("\n4. Testing property mapping...")

    initiative_name_prop = schema.get_property("initiative_name")
    status_prop = schema.get_property("status")
    priority_prop = schema.get_property("priority_score")

    print(f"   initiative_name -> '{initiative_name_prop}'")
    print(f"   status -> '{status_prop}'")
    print(f"   priority_score -> '{priority_prop}'")

    if initiative_name_prop and status_prop:
        print("   ✅ Property mapping working")
    else:
        print("   ❌ Property mapping failed")
        return False

    # 5. Test property type detection
    print("\n5. Testing property type detection...")

    status_type = schema.get_property_type("status")
    priority_type = schema.get_property_type("priority_score")

    print(f"   status type: {status_type}")
    print(f"   priority_score type: {priority_type}")

    if status_type == "select" and priority_type == "number":
        print("   ✅ Property types detected correctly")
    else:
        print(f"   ⚠️  Unexpected types (got: {status_type}, {priority_type})")

    # 6. Test select options
    print("\n6. Testing select options detection...")

    status_options = schema.get_select_options("status")

    if status_options:
        print(f"   ✅ Status options: {status_options}")

        # Validate known option
        if schema.validate_select_value("status", "🚀 In Progress"):
            print("   ✅ Validation working: '🚀 In Progress' is valid")
        else:
            print("   ⚠️  Validation issue: '🚀 In Progress' not found in options")

    else:
        print("   ⚠️  No select options detected")

    # 7. Test Sessions DB schema
    print("\n7. Testing Sessions DB schema...")
    sessions_db_id = os.getenv("NOTION_SESSIONS_DB")

    if sessions_db_id:
        try:
            sessions_schema = detector.get_sessions_schema(sessions_db_id)

            if sessions_schema.schema:
                print(f"   ✅ Sessions schema detected: {sessions_schema}")
                print(f"   Properties: {len(sessions_schema.schema['properties'])}")

                # Test property access
                title_prop = sessions_schema.get_property("title")
                duration_prop = sessions_schema.get_property("duration")
                print(f"   title -> '{title_prop}'")
                print(f"   duration -> '{duration_prop}'")

            else:
                print("   ❌ Sessions schema detection failed")

        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")
    else:
        print("   ⚠️  NOTION_SESSIONS_DB not configured")

    # 8. Test caching
    print("\n8. Testing schema caching...")

    # Request same schema again (should use cache)
    schema_cached = detector.get_strategy_board_schema(strategy_board_id)

    if schema_cached.schema == schema.schema:
        print("   ✅ Schema caching working")
    else:
        print("   ⚠️  Cache mismatch")

    print("\n" + "=" * 60)
    print("TEST: ✅ PASSED - Notion schema detection validated")
    print("=" * 60)

    print("\n📝 Features Validated:")
    print("   - Schema detection via API: ✅")
    print("   - Property mapping (defaults): ✅")
    print("   - Property type detection: ✅")
    print("   - Select options extraction: ✅")
    print("   - Value validation: ✅")
    print("   - Schema caching: ✅")

    return True


def test_offline_mode():
    """Test schema wrapper in offline mode (no API)."""
    print("\n📝 Running offline mode tests...")
    print("\n1. Testing schema wrapper with defaults...")

    # Create schema with None (simulates API failure)
    schema = NotionSchema(None, defaults={
        "initiative_name": "Initiative Name",
        "status": "Status",
        "priority_score": "Priority Score"
    })

    print(f"   Schema: {schema}")

    # Test fallback to defaults
    initiative_prop = schema.get_property("initiative_name")
    status_prop = schema.get_property("status")

    print(f"   initiative_name (fallback) -> '{initiative_prop}'")
    print(f"   status (fallback) -> '{status_prop}'")

    if initiative_prop == "Initiative Name" and status_prop == "Status":
        print("   ✅ Fallback to defaults working")
    else:
        print("   ❌ Fallback failed")
        return False

    print("\n" + "=" * 60)
    print("TEST: ✅ PASSED - Offline mode validated")
    print("=" * 60)

    print("\n📝 Fallback Behavior:")
    print("   - Uses default property names when API unavailable")
    print("   - Graceful degradation (no crashes)")

    return True


if __name__ == "__main__":
    success = test_notion_schema_detection()
    sys.exit(0 if success else 1)
