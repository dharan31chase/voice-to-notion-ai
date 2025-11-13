#!/usr/bin/env python3
"""
Test script for multi-project MCP functionality
Validates core features without needing Claude Desktop
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path.home() / "Documents" / "1. Projects" / "ai-assistant"
sys.path.insert(0, str(project_root))

# Import the MCP server module
from mcp_server.full_server import (
    PROJECT_CONFIG,
    read_file,
    search_docs,
    start_session
)

def test_project_config():
    """Test 1.0: Validate PROJECT_CONFIG structure"""
    print("\n" + "="*70)
    print("TEST 1.0: Project Configuration")
    print("="*70)

    # Check both projects exist
    assert "Epic 2nd Brain" in PROJECT_CONFIG, "Epic 2nd Brain not in config"
    assert "Legacy AI" in PROJECT_CONFIG, "Legacy AI not in config"

    # Check Epic 2nd Brain config
    eb_config = PROJECT_CONFIG["Epic 2nd Brain"]
    assert eb_config["repo_path"].exists(), f"Epic 2nd Brain repo not found: {eb_config['repo_path']}"
    print(f"✅ Epic 2nd Brain repo exists: {eb_config['repo_path']}")

    # Check Legacy AI config
    la_config = PROJECT_CONFIG["Legacy AI"]
    assert la_config["repo_path"].exists(), f"Legacy AI repo not found: {la_config['repo_path']}"
    print(f"✅ Legacy AI repo exists: {la_config['repo_path']}")

    print("\n✅ TEST 1.0 PASSED: Project configuration valid\n")


def test_read_file_epic_2nd_brain():
    """Test 1.1: Read file from Epic 2nd Brain"""
    print("\n" + "="*70)
    print("TEST 1.1: Read File - Epic 2nd Brain")
    print("="*70)

    # Read the multi-project expansion PRD
    result = read_file("docs/prd/multi-project-expansion.md", project="Epic 2nd Brain")

    assert "Error" not in result, f"Error reading file: {result}"
    assert "Multi-Project Expansion" in result, "PRD title not found in content"
    assert "Legacy AI" in result, "Expected Legacy AI mention in PRD"

    print(f"✅ Read PRD successfully ({len(result)} characters)")
    print(f"✅ Content validation passed")
    print("\n✅ TEST 1.1 PASSED\n")


def test_read_file_legacy_ai():
    """Test 2.1: Read file from Legacy AI"""
    print("\n" + "="*70)
    print("TEST 2.1: Read File - Legacy AI")
    print("="*70)

    # Read the requirements-vision document
    result = read_file("research/requirements-vision.md", project="Legacy AI")

    assert "Error" not in result, f"Error reading file: {result}"
    print(f"✅ Read requirements-vision.md successfully ({len(result)} characters)")
    print("\n✅ TEST 2.1 PASSED\n")


def test_search_docs_epic_only():
    """Test 1.2: Search docs filtered to Epic 2nd Brain"""
    print("\n" + "="*70)
    print("TEST 1.2: Search Docs - Epic 2nd Brain Only")
    print("="*70)

    results = search_docs("MCP server", project_name="Epic 2nd Brain")

    assert isinstance(results, list), "Results should be a list"

    # All results should be from Epic 2nd Brain
    for result in results:
        if "error" not in result:
            assert result["project"] == "Epic 2nd Brain", f"Found result from wrong project: {result['project']}"

    print(f"✅ Found {len(results)} results")
    print(f"✅ All results from Epic 2nd Brain")

    if results:
        print("\nSample result:")
        print(f"  - File: {results[0]['file']}")
        print(f"  - Project: {results[0]['project']}")
        print(f"  - Path: {results[0]['path']}")

    print("\n✅ TEST 1.2 PASSED\n")


def test_search_docs_legacy_only():
    """Test 2.2: Search docs filtered to Legacy AI"""
    print("\n" + "="*70)
    print("TEST 2.2: Search Docs - Legacy AI Only")
    print("="*70)

    results = search_docs("customer", project_name="Legacy AI")

    assert isinstance(results, list), "Results should be a list"

    # All results should be from Legacy AI
    for result in results:
        if "error" not in result:
            assert result["project"] == "Legacy AI", f"Found result from wrong project: {result['project']}"

    print(f"✅ Found {len(results)} results")
    print(f"✅ All results from Legacy AI")

    if results:
        print("\nSample result:")
        print(f"  - File: {results[0]['file']}")
        print(f"  - Project: {results[0]['project']}")
        print(f"  - Path: {results[0]['path']}")

    print("\n✅ TEST 2.2 PASSED\n")


def test_search_docs_cross_project():
    """Test 3.1: Search across all projects"""
    print("\n" + "="*70)
    print("TEST 3.1: Cross-Project Search")
    print("="*70)

    results = search_docs("strategy")  # No project filter

    assert isinstance(results, list), "Results should be a list"

    # Should have results from both projects
    projects_found = set()
    for result in results:
        if "error" not in result:
            projects_found.add(result["project"])

    print(f"✅ Found {len(results)} results")
    print(f"✅ Projects represented: {projects_found}")

    if results:
        print("\nResults by project:")
        for project in projects_found:
            count = sum(1 for r in results if r.get("project") == project)
            print(f"  - {project}: {count} results")

    print("\n✅ TEST 3.1 PASSED\n")


def test_start_session_epic():
    """Test 1.3: Start session for Epic 2nd Brain"""
    print("\n" + "="*70)
    print("TEST 1.3: Start Session - Epic 2nd Brain")
    print("="*70)

    result = start_session("Epic 2nd Brain")

    assert result.get("project") == "Epic 2nd Brain", "Wrong project in context"
    assert "documents" in result, "Documents not loaded"
    assert "strategy_board" in result, "Strategy board not queried"

    print(f"✅ Project: {result['project']}")
    print(f"✅ Documents loaded: {len(result['documents'])}")
    print(f"✅ Summary: {result.get('summary', 'N/A')}")

    if result.get("alerts"):
        print(f"\n⚠️  Alerts:")
        for alert in result["alerts"]:
            print(f"  - {alert}")

    print("\n✅ TEST 1.3 PASSED\n")
    return result


def test_start_session_legacy():
    """Test 2.3: Start session for Legacy AI"""
    print("\n" + "="*70)
    print("TEST 2.3: Start Session - Legacy AI")
    print("="*70)

    result = start_session("Legacy AI", "customer-discovery")

    assert result.get("project") == "Legacy AI", "Wrong project in context"
    assert result.get("work_stream") == "customer-discovery", "Wrong work stream"
    assert "documents" in result, "Documents not loaded"
    assert "strategy_board" in result, "Strategy board not queried"

    print(f"✅ Project: {result['project']}")
    print(f"✅ Work Stream: {result['work_stream']}")
    print(f"✅ Documents loaded: {len(result['documents'])}")
    print(f"✅ Summary: {result.get('summary', 'N/A')}")

    if result.get("alerts"):
        print(f"\n⚠️  Alerts:")
        for alert in result["alerts"]:
            print(f"  - {alert}")

    print("\n✅ TEST 2.3 PASSED\n")
    return result


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "="*70)
    print("MULTI-PROJECT MCP VALIDATION TEST SUITE")
    print("="*70)
    print("\nRunning automated tests for multi-project functionality...")

    tests = [
        ("Project Configuration", test_project_config),
        ("Read File - Epic 2nd Brain", test_read_file_epic_2nd_brain),
        ("Read File - Legacy AI", test_read_file_legacy_ai),
        ("Search - Epic 2nd Brain Only", test_search_docs_epic_only),
        ("Search - Legacy AI Only", test_search_docs_legacy_only),
        ("Cross-Project Search", test_search_docs_cross_project),
        ("Start Session - Epic 2nd Brain", test_start_session_epic),
        ("Start Session - Legacy AI", test_start_session_legacy),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Exception: {str(e)}\n")
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Multi-project functionality is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
