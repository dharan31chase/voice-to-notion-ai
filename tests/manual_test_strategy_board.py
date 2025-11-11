#!/usr/bin/env python3
"""
Manual test for Strategy Board Notion tools.
Run this to verify Notion integration works before running MCP server.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path.home() / "Documents" / "1. Projects" / "ai-assistant"
sys.path.insert(0, str(project_root))

# Import the tools
from mcp_server.full_server import query_strategy_board, update_initiative_status

def test_query_strategy_board():
    """Test querying Strategy Board"""
    print("\n" + "="*60)
    print("TEST: Query Strategy Board (Top 3 Initiatives)")
    print("="*60)

    result = query_strategy_board()

    if result["status"] == "success":
        print(f"✅ Query successful! Found {result['count']} initiatives")
        print(f"\nTop Initiatives:")
        for i, init in enumerate(result["initiatives"], 1):
            print(f"\n{i}. {init['name']}")
            print(f"   Priority Score: {init['priority_score']}")
            print(f"   Status: {init['status']}")
            print(f"   Category: {init['category']}")
            print(f"   URL: {init['url']}")
    else:
        print(f"❌ Query failed: {result['message']}")
        return False

    return True

def test_query_with_custom_limit():
    """Test querying with custom limit"""
    print("\n" + "="*60)
    print("TEST: Query Strategy Board (Top 1 Only)")
    print("="*60)

    result = query_strategy_board(limit=1)

    if result["status"] == "success" and result["count"] <= 1:
        print(f"✅ Custom limit works! Found {result['count']} initiative(s)")
    else:
        print(f"❌ Custom limit test failed")
        return False

    return True

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MANUAL TEST: Strategy Board Notion Tools")
    print("="*60)
    print("\nThis will test the Notion integration with your Strategy Board.")
    print("Make sure:")
    print("1. NOTION_TOKEN is set in .env")
    print("2. STRATEGY_BOARD_DATABASE_ID is set in .env")
    print("3. Integration has access to Strategy Board database")

    input("\nPress Enter to continue...")

    # Run tests
    test1_passed = test_query_strategy_board()
    test2_passed = test_query_with_custom_limit()

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Query Strategy Board: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Custom Limit: {'✅ PASS' if test2_passed else '❌ FAIL'}")

    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Notion integration is working.")
        print("\nNext steps:")
        print("1. Write unit tests (with mocks)")
        print("2. Modify start_session() and end_session()")
        print("3. Test full workflow")
    else:
        print("\n⚠️ Some tests failed. Check:")
        print("1. NOTION_TOKEN in .env")
        print("2. STRATEGY_BOARD_DATABASE_ID in .env")
        print("3. Integration has access to database")
        print("4. Property names match (Initiative Name, Priority Score, etc.)")
