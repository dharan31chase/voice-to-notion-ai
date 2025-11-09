#!/usr/bin/env python3
"""
Full MCP Server for AI Assistant Project

Provides tools for Claude to:
1. Read project documentation
2. Write files (create PRDs, session logs, etc.)
3. Start sessions (auto-load context)
4. End sessions (auto-log work)
5. Search across docs (basic RAG)

Usage:
    Configured in Claude Desktop config to run automatically
"""

from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

# Add project root to path
project_root = Path.home() / "Documents" / "1. Projects" / "ai-assistant"
sys.path.insert(0, str(project_root))

# Initialize MCP server
mcp = FastMCP(name="ai-assistant-full")

# ============================================================================
# TOOL 1: Read Files
# ============================================================================

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read a file from the ai-assistant repo.

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')

    Returns:
        File contents as string

    Examples:
        - read_file("README.md")
        - read_file("docs/prd/context-sync-bridge.md")
        - read_file("docs/sessions/claude-code/2025-11-08-mcp-poc-and-templates.md")
    """
    full_path = project_root / path

    if not full_path.exists():
        return f"Error: File not found at {full_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ============================================================================
# TOOL 2: Write Files (NEW - Critical for Claude Chat)
# ============================================================================

@mcp.tool()
def write_file(path: str, content: str) -> dict:
    """
    Write a file to the ai-assistant repo.

    This enables Claude (chat) to create PRDs, session logs, and other
    docs directly in the repo without using /mnt/user-data/outputs workaround.

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
        content: Full file content to write

    Returns:
        Dict with status and file path

    Security:
        - Only allows writes within project_root
        - Creates parent directories if needed
        - Overwrites existing files (use with caution)

    Examples:
        - write_file("docs/prd/new-feature.md", "# PRD: New Feature...")
        - write_file("docs/sessions/claude-chat/2025-11-08-planning.md", "# Session...")
    """
    full_path = project_root / path

    # Security: Ensure path is within project
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(project_root)):
            return {
                "status": "error",
                "message": f"Path {path} is outside project root"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Invalid path: {str(e)}"
        }

    # Create parent directories if needed
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating directories: {str(e)}"
        }

    # Write file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "path": str(full_path),
            "relative_path": path,
            "message": f"File written successfully: {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing file: {str(e)}"
        }


# ============================================================================
# TOOL 3: Start Session
# ============================================================================

@mcp.tool()
def start_session(project_name: str = "Epic 2nd Brain") -> dict:
    """
    Load all context needed for a Claude chat session.

    Fetches:
    - Latest PRD(s) for this project
    - Latest tech requirements
    - Recent session logs (last 3)
    - Open roadmap items (from docs)
    - Critical alerts

    Args:
        project_name: Name of project (default: "Epic 2nd Brain")

    Returns:
        Dict with all context

    Examples:
        - start_session("Epic 2nd Brain")
        - start_session("Legacy AI")
    """
    context = {
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "prds": [],
        "tech_requirements": [],
        "recent_sessions": [],
        "roadmap": {},
        "alerts": []
    }

    # Load PRDs
    prd_dir = project_root / "docs" / "prd"
    if prd_dir.exists():
        prd_files = sorted(prd_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for prd_file in prd_files:
            if prd_file.name != "TEMPLATE.md":
                try:
                    with open(prd_file, encoding='utf-8') as f:
                        content = f.read()
                        context["prds"].append({
                            "file": prd_file.name,
                            "path": str(prd_file.relative_to(project_root)),
                            "preview": content[:500] + "..." if len(content) > 500 else content
                        })
                    if len(context["prds"]) >= 2:  # Max 2 PRDs
                        break
                except Exception as e:
                    context["alerts"].append(f"Error reading PRD {prd_file.name}: {str(e)}")

    # Load tech requirements
    tech_dir = project_root / "docs" / "tech-requirements"
    if tech_dir.exists():
        tech_files = sorted(tech_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for tech_file in tech_files:
            if tech_file.name != "TEMPLATE.md":
                try:
                    with open(tech_file, encoding='utf-8') as f:
                        content = f.read()
                        context["tech_requirements"].append({
                            "file": tech_file.name,
                            "path": str(tech_file.relative_to(project_root)),
                            "preview": content[:500] + "..." if len(content) > 500 else content
                        })
                    if len(context["tech_requirements"]) >= 2:
                        break
                except Exception as e:
                    context["alerts"].append(f"Error reading tech req {tech_file.name}: {str(e)}")

    # Load recent sessions
    sessions_dir = project_root / "docs" / "sessions"
    session_count = 0
    for agent_dir in ["claude-chat", "claude-code"]:
        agent_path = sessions_dir / agent_dir
        if agent_path.exists():
            session_files = sorted(agent_path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
            for session_file in session_files:
                if session_file.name != "TEMPLATE.md":
                    try:
                        with open(session_file, encoding='utf-8') as f:
                            content = f.read()
                            context["recent_sessions"].append({
                                "file": session_file.name,
                                "agent": agent_dir,
                                "path": str(session_file.relative_to(project_root)),
                                "preview": content[:300] + "..." if len(content) > 300 else content
                            })
                        session_count += 1
                        if session_count >= 3:  # Max 3 sessions total
                            break
                    except Exception as e:
                        context["alerts"].append(f"Error reading session {session_file.name}: {str(e)}")
        if session_count >= 3:
            break

    # Load roadmap (from docs/context/roadmap.md)
    roadmap_file = project_root / "docs" / "context" / "roadmap.md"
    if roadmap_file.exists():
        try:
            with open(roadmap_file, encoding='utf-8') as f:
                roadmap_content = f.read()
                context["roadmap"] = {
                    "file": "docs/context/roadmap.md",
                    "preview": roadmap_content[:1000] + "..." if len(roadmap_content) > 1000 else roadmap_content
                }
        except Exception as e:
            context["alerts"].append(f"Error reading roadmap: {str(e)}")

    # Add helpful summary
    context["summary"] = f"Loaded {len(context['prds'])} PRDs, {len(context['tech_requirements'])} tech requirements, {len(context['recent_sessions'])} recent sessions"

    return context


# ============================================================================
# TOOL 4: End Session
# ============================================================================

@mcp.tool()
def end_session(
    project_name: str,
    summary: str,
    decisions: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None
) -> dict:
    """
    Log Claude chat session to docs/ and prepare for Notion sync.

    Args:
        project_name: Project name
        summary: Brief summary of session
        decisions: List of key decisions made
        next_steps: List of recommended next actions

    Returns:
        Dict with log path and next steps

    Examples:
        - end_session("Epic 2nd Brain", "Completed MCP server", ["Use FastMCP API"], ["Test all 5 tools"])
    """
    decisions = decisions or []
    next_steps = next_steps or []

    # Generate session log filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    topic = summary.lower().replace(" ", "-")[:30]
    # Clean topic for filename
    topic = "".join(c for c in topic if c.isalnum() or c == "-")
    filename = f"{date_str}-{topic}.md"

    log_path = project_root / "docs" / "sessions" / "claude-chat" / filename

    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Write session log
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"# Session: {date_str} - Claude Chat\n\n")
            f.write(f"**Project**: {project_name}\n")
            f.write(f"**Status**: Complete\n")
            f.write(f"**Session Type**: Planning\n\n")
            f.write(f"---\n\n")
            f.write(f"## Summary\n\n{summary}\n\n")

            if decisions:
                f.write(f"## Decisions Made\n\n")
                for i, decision in enumerate(decisions, 1):
                    f.write(f"{i}. {decision}\n")
                f.write("\n")

            if next_steps:
                f.write(f"## Next Steps\n\n")
                for i, step in enumerate(next_steps, 1):
                    f.write(f"{i}. {step}\n")
                f.write("\n")

            f.write(f"---\n\n")
            f.write(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return {
            "status": "success",
            "log_path": str(log_path.relative_to(project_root)),
            "full_path": str(log_path),
            "reminder": "Don't forget to commit this session log!",
            "next_action": "Run: git add . && git commit -m '[ROADMAP-X] Session: {summary}'"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing session log: {str(e)}"
        }


# ============================================================================
# TOOL 5: Search Docs (Basic RAG)
# ============================================================================

@mcp.tool()
def search_docs(
    query: str,
    doc_types: Optional[List[str]] = None
) -> list:
    """
    Search across project documentation.

    Args:
        query: Search query (keywords or phrase)
        doc_types: Types to search (default: all)
                   Options: "prd", "tech-req", "sessions", "context"

    Returns:
        List of relevant doc snippets with context

    Examples:
        - search_docs("MCP server")
        - search_docs("git hooks", ["tech-req"])
        - search_docs("PARITY approach", ["prd", "sessions"])
    """
    doc_types = doc_types or ["prd", "tech-req", "sessions", "context"]
    results = []

    # Map doc types to folders
    folder_map = {
        "prd": project_root / "docs" / "prd",
        "tech-req": project_root / "docs" / "tech-requirements",
        "sessions": project_root / "docs" / "sessions",
        "context": project_root / "docs" / "context"
    }

    # Simple keyword search (can enhance with semantic search later)
    query_lower = query.lower()

    for doc_type in doc_types:
        folder = folder_map.get(doc_type)
        if not folder or not folder.exists():
            continue

        # Search all markdown files
        for md_file in folder.rglob("*.md"):
            if md_file.name == "TEMPLATE.md":
                continue

            try:
                with open(md_file, encoding='utf-8') as f:
                    content = f.read()
                    content_lower = content.lower()

                    # Check if query appears
                    if query_lower in content_lower:
                        # Find context around match
                        idx = content_lower.find(query_lower)
                        start = max(0, idx - 100)
                        end = min(len(content), idx + 200)
                        snippet = content[start:end]

                        # Determine relevance based on position
                        relevance = "high" if idx < 500 else "medium"

                        results.append({
                            "file": md_file.name,
                            "path": str(md_file.relative_to(project_root)),
                            "doc_type": doc_type,
                            "snippet": f"...{snippet}...",
                            "relevance": relevance
                        })

                        # Limit results per file to avoid spam
                        break
            except Exception as e:
                # Skip files that can't be read
                pass

    # Sort by relevance and return top 10
    results.sort(key=lambda x: (x["relevance"] == "high", x["doc_type"]), reverse=True)
    return results[:10]


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    mcp.run()
