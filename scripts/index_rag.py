#!/usr/bin/env python3
"""
RAG Indexing Script (Phase 6)

Index documents for Legacy AI and Epic 2nd Brain RAG collections.
Run this script before using RAG search tools.

Usage:
    python scripts/index_rag.py                    # Index both projects
    python scripts/index_rag.py --legacy-ai        # Index Legacy AI only
    python scripts/index_rag.py --epic-2nd-brain   # Index Epic 2nd Brain only
    python scripts/index_rag.py --force            # Force re-indexing
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.rag.legacy_ai_rag import LegacyAIRAG
from mcp_server.rag.epic_2nd_brain_rag import Epic2ndBrainRAG


def index_legacy_ai(force_reindex: bool = False):
    """Index Legacy AI documents."""
    print("\n" + "=" * 80)
    print("INDEXING LEGACY AI")
    print("=" * 80)

    try:
        rag = LegacyAIRAG()

        print(f"\nProject: {rag.project_name}")
        print(f"Collection: {rag.chroma_collection}")
        print(f"Embedding Model: {rag.embedding_model}")
        print(f"Chunk Size: {rag.chunk_size} chars")
        print(f"Chunk Overlap: {rag.chunk_overlap} chars")
        print(f"Reranking: {rag.reranking_enabled}")

        print("\nIndex Paths:")
        for path in rag.get_index_paths():
            exists = "✓" if path.exists() else "✗"
            print(f"  {exists} {path}")

        print("\nStarting indexing...")
        print("(This may take a few minutes depending on document count)")

        result = rag.index_documents(force_reindex=force_reindex)

        if result.get("status") == "skipped":
            print(f"\n⚠️  Indexing skipped: {result.get('message')}")
            print(f"Existing chunks: {result.get('existing_chunks', 0)}")
            print("Use --force to re-index")
            return True

        if result.get("status") == "success":
            print(f"\n✅ Indexing complete!")
            print(f"   Total documents: {result.get('total_documents', 0)}")
            print(f"   Total chunks: {result.get('total_chunks', 0)}")

            # Show sample of indexed files
            files = result.get('files_processed', [])
            if files:
                print(f"\n   Sample files indexed ({min(5, len(files))} of {len(files)}):")
                for file in files[:5]:
                    print(f"     - {file}")

            return True
        else:
            print(f"\n✗ Indexing failed: {result}")
            return False

    except Exception as e:
        print(f"\n✗ Error indexing Legacy AI: {e}")
        import traceback
        traceback.print_exc()
        return False


def index_epic_2nd_brain(force_reindex: bool = False):
    """Index Epic 2nd Brain documents."""
    print("\n" + "=" * 80)
    print("INDEXING EPIC 2ND BRAIN")
    print("=" * 80)

    try:
        rag = Epic2ndBrainRAG()

        print(f"\nProject: {rag.project_name}")
        print(f"Collection: {rag.chroma_collection}")
        print(f"Embedding Model: {rag.embedding_model}")
        print(f"Chunk Size: {rag.chunk_size} chars")
        print(f"Chunk Overlap: {rag.chunk_overlap} chars")
        print(f"Reranking: {rag.reranking_enabled}")

        print("\nIndex Paths:")
        for path in rag.get_index_paths():
            exists = "✓" if path.exists() else "✗"
            print(f"  {exists} {path}")

        print("\nStarting indexing...")
        print("(This may take a few minutes depending on document count)")

        result = rag.index_documents(force_reindex=force_reindex)

        if result.get("status") == "skipped":
            print(f"\n⚠️  Indexing skipped: {result.get('message')}")
            print(f"Existing chunks: {result.get('existing_chunks', 0)}")
            print("Use --force to re-index")
            return True

        if result.get("status") == "success":
            print(f"\n✅ Indexing complete!")
            print(f"   Total documents: {result.get('total_documents', 0)}")
            print(f"   Total chunks: {result.get('total_chunks', 0)}")

            # Show sample of indexed files
            files = result.get('files_processed', [])
            if files:
                print(f"\n   Sample files indexed ({min(5, len(files))} of {len(files)}):")
                for file in files[:5]:
                    print(f"     - {file}")

            return True
        else:
            print(f"\n✗ Indexing failed: {result}")
            return False

    except Exception as e:
        print(f"\n✗ Error indexing Epic 2nd Brain: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main indexing function."""
    parser = argparse.ArgumentParser(description="Index RAG collections")
    parser.add_argument("--legacy-ai", action="store_true", help="Index Legacy AI only")
    parser.add_argument("--epic-2nd-brain", action="store_true", help="Index Epic 2nd Brain only")
    parser.add_argument("--force", action="store_true", help="Force re-indexing")

    args = parser.parse_args()

    # Check dependencies
    try:
        import chromadb
        import openai
    except ImportError as e:
        print(f"\n✗ ERROR: Missing dependencies: {e}")
        print("Install with: pip install chromadb openai sentence-transformers")
        sys.exit(1)

    # Check OPENAI_API_KEY
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("\n✗ ERROR: OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("RAG INDEXING SCRIPT (Phase 6)")
    print("=" * 80)

    results = {}

    # Index based on arguments
    if args.legacy_ai:
        results["Legacy AI"] = index_legacy_ai(force_reindex=args.force)
    elif args.epic_2nd_brain:
        results["Epic 2nd Brain"] = index_epic_2nd_brain(force_reindex=args.force)
    else:
        # Index both by default
        results["Legacy AI"] = index_legacy_ai(force_reindex=args.force)
        results["Epic 2nd Brain"] = index_epic_2nd_brain(force_reindex=args.force)

    # Summary
    print("\n" + "=" * 80)
    print("INDEXING SUMMARY")
    print("=" * 80)

    for project, success in results.items():
        status = "✅ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {project}")

    all_success = all(results.values())

    if all_success:
        print("\n🎉 All collections indexed successfully")
        print("\nNext steps:")
        print("  1. Run tests: python tests/test_rag_separation.py")
        print("  2. Use MCP tools: search_legacy_ai() and search_epic_2nd_brain()")
        sys.exit(0)
    else:
        print("\n❌ Some collections failed to index")
        sys.exit(1)


if __name__ == "__main__":
    main()
