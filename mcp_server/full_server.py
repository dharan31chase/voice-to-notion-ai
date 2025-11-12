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
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path.home() / "Documents" / "1. Projects" / "ai-assistant"
sys.path.insert(0, str(project_root))

# Initialize MCP server
mcp = FastMCP(name="ai-assistant-full")

# Initialize Notion client
notion_token = os.getenv("NOTION_TOKEN")
notion_client = Client(auth=notion_token) if notion_token else None

# Status constants for Strategy Board
VALID_STATUSES = [
    "🟡 Needs Decision",
    "🚀 In Progress",
    "✅ Complete",
    "🔴 Blocked"
]

# Multi-Project Configuration
PROJECT_CONFIG = {
    "Epic 2nd Brain": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "ai-assistant",
        "context_folders": ["docs/prd", "docs/tech-requirements", "docs/sessions"],
        "session_log_path": "docs/sessions/claude-chat",
        "strategy_board_view": "Epic 2nd Brain Only"
    },
    "Legacy AI": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "legacy-ai",
        "context_folders": ["research", "product", "business", "sessions"],
        "session_log_path": "sessions/customer-discovery",
        "strategy_board_view": "Legacy AI Only"
    }
}

# ============================================================================
# TOOL 1: Read Files
# ============================================================================

@mcp.tool()
def read_file(path: str, project: str = "Epic 2nd Brain") -> str:
    """
    Read a file from a project repo.

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
        project: Project name (default: "Epic 2nd Brain")
                 Options: "Epic 2nd Brain", "Legacy AI"

    Returns:
        File contents as string

    Examples:
        - read_file("README.md")
        - read_file("docs/prd/context-sync-bridge.md")
        - read_file("research/requirements-vision.md", project="Legacy AI")
    """
    # Get project repo path
    if project not in PROJECT_CONFIG:
        return f"Error: Unknown project '{project}'. Valid options: {list(PROJECT_CONFIG.keys())}"

    repo_path = PROJECT_CONFIG[project]["repo_path"]
    full_path = repo_path / path

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
def write_file(path: str, content: str, project: str = "Epic 2nd Brain") -> dict:
    """
    Write a file to a project repo.

    This enables Claude (chat) to create PRDs, session logs, and other
    docs directly in the repo without using /mnt/user-data/outputs workaround.

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
        content: Full file content to write
        project: Project name (default: "Epic 2nd Brain")
                 Options: "Epic 2nd Brain", "Legacy AI"

    Returns:
        Dict with status and file path

    Security:
        - Only allows writes within project repos
        - Creates parent directories if needed
        - Overwrites existing files (use with caution)

    Examples:
        - write_file("docs/prd/new-feature.md", "# PRD: New Feature...")
        - write_file("research/requirements-vision.md", "# Requirements...", project="Legacy AI")
    """
    # Get project repo path
    if project not in PROJECT_CONFIG:
        return {
            "status": "error",
            "message": f"Unknown project '{project}'. Valid options: {list(PROJECT_CONFIG.keys())}"
        }

    repo_path = PROJECT_CONFIG[project]["repo_path"]
    full_path = repo_path / path

    # Security: Ensure path is within project
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(repo_path)):
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
def start_session(project_name: str = "Epic 2nd Brain", work_stream: Optional[str] = None) -> dict:
    """
    Load all context needed for a Claude chat session.

    Multi-project support: Loads context from correct repo based on PROJECT_CONFIG.

    Fetches:
    - Top 3 prioritized initiatives from Strategy Board (filtered by project)
    - Latest documents (PRDs, requirements, analyses, etc.)
    - Recent session logs (last 3)
    - Roadmap (project-specific)
    - Critical alerts

    Args:
        project_name: Name of project (default: "Epic 2nd Brain")
                      Options: "Epic 2nd Brain", "Legacy AI"
        work_stream: Optional work stream for Legacy AI
                     Examples: "customer-discovery", "prototype", "funding"

    Returns:
        Dict with all context

    Examples:
        - start_session("Epic 2nd Brain")
        - start_session("Legacy AI", "customer-discovery")
    """
    # Validate project
    if project_name not in PROJECT_CONFIG:
        return {
            "status": "error",
            "message": f"Unknown project '{project_name}'. Valid options: {list(PROJECT_CONFIG.keys())}"
        }

    config = PROJECT_CONFIG[project_name]
    repo_path = config["repo_path"]

    context = {
        "project": project_name,
        "work_stream": work_stream,
        "timestamp": datetime.now().isoformat(),
        "strategy_board": {},
        "documents": [],
        "recent_sessions": [],
        "roadmap": {},
        "alerts": []
    }

    # Query Strategy Board (filtered by project)
    try:
        board_result = query_strategy_board(limit=3, project_name=project_name)
        if board_result["status"] == "success":
            context["strategy_board"] = board_result
        else:
            context["alerts"].append(f"⚠️ Strategy Board unavailable: {board_result.get('message', 'Unknown error')}")
    except Exception as e:
        context["alerts"].append(f"⚠️ Strategy Board query failed: {str(e)}")

    # Load documents from context_folders
    for folder_rel in config["context_folders"]:
        folder_path = repo_path / folder_rel
        if not folder_path.exists():
            continue

        # Recursively find all markdown files
        md_files = sorted(folder_path.rglob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        for md_file in md_files[:10]:  # Limit to 10 most recent per folder
            if md_file.name in ["TEMPLATE.md", ".gitkeep"]:
                continue

            try:
                with open(md_file, encoding='utf-8') as f:
                    content = f.read()
                    context["documents"].append({
                        "file": md_file.name,
                        "folder": folder_rel,
                        "path": str(md_file.relative_to(repo_path)),
                        "preview": content[:500] + "..." if len(content) > 500 else content
                    })
            except Exception as e:
                context["alerts"].append(f"Error reading {md_file.name}: {str(e)}")

    # Load roadmap (different paths for each project)
    roadmap_paths = [
        repo_path / "docs" / "roadmap.md",  # Legacy AI
        repo_path / "docs" / "context" / "roadmap.md"  # Epic 2nd Brain
    ]
    for roadmap_file in roadmap_paths:
        if roadmap_file.exists():
            try:
                with open(roadmap_file, encoding='utf-8') as f:
                    roadmap_content = f.read()
                    context["roadmap"] = {
                        "file": str(roadmap_file.relative_to(repo_path)),
                        "preview": roadmap_content[:1000] + "..." if len(roadmap_content) > 1000 else roadmap_content
                    }
                break
            except Exception as e:
                context["alerts"].append(f"Error reading roadmap: {str(e)}")

    # Add helpful summary
    initiative_count = context["strategy_board"].get("count", 0)
    context["summary"] = f"Loaded {initiative_count} top initiatives from Strategy Board, {len(context['documents'])} documents, {len(context['recent_sessions'])} recent sessions"

    return context


# ============================================================================
# TOOL 4: End Session (MODIFIED)
# ============================================================================

@mcp.tool()
def end_session(
    project_name: str,
    summary: str,
    decisions: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    create_handoff: bool = False,  # NEW
    handoff_initiative_id: Optional[str] = None,  # NEW
    handoff_prd_path: Optional[str] = None,  # NEW
    handoff_one_pager_location: Optional[str] = None  # NEW
) -> dict:
    """
    Log Claude chat session to docs/ and prepare for Notion sync.

    NEW: Optionally creates handoff prompt for Claude Code and updates Strategy Board status.

    Args:
        project_name: Project name
        summary: Brief summary of session
        decisions: List of key decisions made
        next_steps: List of recommended next actions
        create_handoff: If True, create handoff prompt in docs/handoffs/ (NEW)
        handoff_initiative_id: Notion page ID for Strategy Board initiative (NEW)
        handoff_prd_path: Path to PRD file (e.g., "docs/prd/feature.md") (NEW)
        handoff_one_pager_location: Notion URL or repo path to one-pager (NEW)

    Returns:
        Dict with log path, handoff path (if created), and next steps

    Examples:
        - end_session("Epic 2nd Brain", "Completed MCP server", ["Use FastMCP API"], ["Test all 5 tools"])
        - end_session("Epic 2nd Brain", "PRD approved", create_handoff=True, handoff_initiative_id="page123", handoff_prd_path="docs/prd/feature.md")
    """
    decisions = decisions or []
    next_steps = next_steps or []

    # Validate project
    if project_name not in PROJECT_CONFIG:
        return {
            "status": "error",
            "message": f"Unknown project '{project_name}'. Valid options: {list(PROJECT_CONFIG.keys())}"
        }

    config = PROJECT_CONFIG[project_name]
    repo_path = config["repo_path"]

    # Generate session log filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    topic = summary.lower().replace(" ", "-")[:30]
    # Clean topic for filename
    topic = "".join(c for c in topic if c.isalnum() or c == "-")
    filename = f"{date_str}-{topic}.md"

    # Route to correct project's session log folder
    log_path = repo_path / config["session_log_path"] / filename

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

        result = {
            "status": "success",
            "log_path": str(log_path.relative_to(repo_path)),
            "full_path": str(log_path),
            "reminder": f"Don't forget to commit this session log to {project_name} repo!",
            "next_action": f"Run: cd {repo_path} && git add . && git commit -m '[ROADMAP-X] Session: {summary}'"
        }

        # NEW: Create handoff prompt if requested
        # Note: Handoffs always go to ai-assistant repo (where Context Sync Bridge lives)
        if create_handoff:
            date_str = datetime.now().strftime("%Y-%m-%d")
            topic = summary.lower().replace(" ", "-")[:30]
            topic = "".join(c for c in topic if c.isalnum() or c == "-")
            handoff_filename = f"{date_str}-to-claude-code-{topic}.md"
            ai_assistant_repo = PROJECT_CONFIG["Epic 2nd Brain"]["repo_path"]
            handoff_path = ai_assistant_repo / "docs" / "handoffs" / handoff_filename

            # Ensure handoffs directory exists
            handoff_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate handoff content
            handoff_content = generate_handoff_template(
                summary=summary,
                decisions=decisions,
                next_steps=next_steps,
                prd_path=handoff_prd_path or "NOT_PROVIDED",
                one_pager_location=handoff_one_pager_location or "NOT_PROVIDED",
                initiative_id=handoff_initiative_id or "NOT_PROVIDED"
            )

            # Write handoff prompt
            with open(handoff_path, 'w', encoding='utf-8') as f:
                f.write(handoff_content)

            result["handoff_path"] = str(handoff_path.relative_to(ai_assistant_repo))
            result["handoff_full_path"] = str(handoff_path)

        # NEW: Update Strategy Board if initiative ID provided
        if handoff_initiative_id:
            try:
                date_str = datetime.now().strftime("%Y-%m-%d")
                update_result = update_initiative_status(
                    page_id=handoff_initiative_id,
                    new_status="🚀 In Progress",
                    decision_notes=f"PRD approved. Handed off to Claude Code for implementation."
                )
                result["notion_updated"] = update_result["status"] == "success"
                if update_result["status"] == "success":
                    result["notion_message"] = "Strategy Board updated to 🚀 In Progress"
                else:
                    result["notion_error"] = update_result.get("message", "Unknown error")
            except Exception as e:
                result["notion_updated"] = False
                result["notion_error"] = str(e)

        return result

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
    doc_types: Optional[List[str]] = None,
    project_name: Optional[str] = None
) -> list:
    """
    Search across project documentation.

    Multi-project support: Search single project or all projects.

    Args:
        query: Search query (keywords or phrase)
        doc_types: Types to search (default: all)
                   Options: "prd", "tech-req", "sessions", "context", "research", "product"
        project_name: Filter to specific project (default: None = search all projects)
                      Options: "Epic 2nd Brain", "Legacy AI"

    Returns:
        List of relevant doc snippets with context

    Examples:
        - search_docs("MCP server")  # Search all projects
        - search_docs("customer pain points", project_name="Legacy AI")  # Legacy AI only
        - search_docs("git hooks", ["tech-req"], "Epic 2nd Brain")  # Epic 2nd Brain tech-req only
    """
    doc_types = doc_types or ["prd", "tech-req", "sessions", "context", "research", "product", "business"]
    results = []

    # Determine which projects to search
    if project_name:
        if project_name not in PROJECT_CONFIG:
            return [{
                "error": f"Unknown project '{project_name}'. Valid options: {list(PROJECT_CONFIG.keys())}"
            }]
        projects_to_search = [project_name]
    else:
        projects_to_search = list(PROJECT_CONFIG.keys())

    # Search each project
    for proj in projects_to_search:
        config = PROJECT_CONFIG[proj]
        repo_path = config["repo_path"]

        # Map doc types to folders for this project
        folder_map = {
            "prd": repo_path / "docs" / "prd",
            "tech-req": repo_path / "docs" / "tech-requirements",
            "sessions": repo_path / "docs" / "sessions",
            "context": repo_path / "docs" / "context",
            "research": repo_path / "research",
            "product": repo_path / "product",
            "business": repo_path / "business"
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
                                "project": proj,  # NEW: Project indicator
                                "file": md_file.name,
                                "path": str(md_file.relative_to(repo_path)),
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
# TOOL 6: Query Strategy Board (NEW)
# ============================================================================

@mcp.tool()
def query_strategy_board(
    filter_status: Optional[List[str]] = None,
    limit: int = 3,
    project_name: Optional[str] = None
) -> dict:
    """
    Query Notion Strategy Board for prioritized initiatives.

    Multi-project support: Filter by project when provided.

    Args:
        filter_status: Status values to EXCLUDE (default: ["✅ Complete", "🔴 Blocked"])
        limit: Max initiatives to return (default: 3)
        project_name: Filter by project (default: None = all projects)
                      Options: "Epic 2nd Brain", "Legacy AI"

    Returns:
        Dict with initiatives list and metadata

    Examples:
        - query_strategy_board()  # Top 3, exclude Complete/Blocked, all projects
        - query_strategy_board(limit=5)  # Top 5
        - query_strategy_board(project_name="Legacy AI")  # Legacy AI initiatives only
    """
    # Check Notion client initialized
    if not notion_client:
        return {
            "status": "error",
            "message": "Notion client not initialized. Check NOTION_TOKEN in .env"
        }

    # Get Strategy Board database ID
    db_id = os.getenv("STRATEGY_BOARD_DATABASE_ID")
    if not db_id:
        return {
            "status": "error",
            "message": "STRATEGY_BOARD_DATABASE_ID not found in .env"
        }

    # Default filter: exclude Complete and Blocked
    if filter_status is None:
        filter_status = ["✅ Complete", "🔴 Blocked"]

    try:
        # Build filter query
        filter_conditions = []

        # Add status filters
        for status in filter_status:
            filter_conditions.append({
                "property": "Status",
                "select": {"does_not_equal": status}
            })

        # Add project filter if specified (NEW)
        if project_name:
            filter_conditions.append({
                "property": "Project",
                "select": {"equals": project_name}
            })

        query_filter = {"and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0] if filter_conditions else None

        # Query database
        response = notion_client.databases.query(
            database_id=db_id,
            filter=query_filter,
            sorts=[{"property": "Priority Score", "direction": "descending"}],
            page_size=limit
        )

        # Parse results
        initiatives = []
        for page in response.get("results", []):
            props = page.get("properties", {})

            # Extract initiative name (title property)
            name_prop = props.get("Initiative Name", {})
            name = ""
            if name_prop.get("title"):
                name = name_prop["title"][0]["text"]["content"]

            # Extract priority score
            priority_score = props.get("Priority Score", {}).get("number", 0)

            # Extract status
            status_prop = props.get("Status", {}).get("select", {})
            status = status_prop.get("name", "Unknown")

            # Extract category
            category_prop = props.get("Category", {}).get("select", {})
            category = category_prop.get("name", "Unknown")

            # Extract project (NEW)
            project_prop = props.get("Project", {}).get("select", {})
            project = project_prop.get("name", "Unknown")

            initiatives.append({
                "name": name,
                "priority_score": priority_score,
                "status": status,
                "category": category,
                "project": project,  # NEW
                "url": page.get("url", ""),
                "page_id": page.get("id", "")
            })

        return {
            "status": "success",
            "count": len(initiatives),
            "initiatives": initiatives,
            "query_time": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Notion API error: {str(e)}"
        }


# ============================================================================
# TOOL 7: Update Initiative Status (NEW)
# ============================================================================

@mcp.tool()
def update_initiative_status(
    page_id: str,
    new_status: Optional[str] = None,
    decision_notes: Optional[str] = None,
    launch_notes: Optional[str] = None,
    completed_date: Optional[str] = None
) -> dict:
    """
    Update Notion Strategy Board initiative.

    Args:
        page_id: Notion page ID
        new_status: One of ["🟡 Needs Decision", "🚀 In Progress", "✅ Complete", "🔴 Blocked"]
        decision_notes: Text to APPEND to Decision Notes field
        launch_notes: Summary of what shipped (for Complete status, max 150 chars)
        completed_date: ISO date string (default: today if status=Complete)

    Returns:
        Dict with update confirmation

    Examples:
        - update_initiative_status("page123", new_status="🚀 In Progress")
        - update_initiative_status("page123", decision_notes="PRD approved", new_status="🚀 In Progress")
        - update_initiative_status("page123", new_status="✅ Complete", launch_notes="Built 3 tools")
    """
    # Check Notion client initialized
    if not notion_client:
        return {
            "status": "error",
            "message": "Notion client not initialized. Check NOTION_TOKEN in .env"
        }

    # Validate status if provided
    if new_status and new_status not in VALID_STATUSES:
        return {
            "status": "error",
            "message": f"Invalid status. Must be one of: {VALID_STATUSES}"
        }

    try:
        # Build properties to update
        properties = {}
        updated_props = []

        # Update status
        if new_status:
            properties["Status"] = {"select": {"name": new_status}}
            updated_props.append("Status")

        # Update launch notes
        if launch_notes:
            properties["Launch Notes"] = {
                "rich_text": [{"text": {"content": launch_notes[:150]}}]
            }
            updated_props.append("Launch Notes")

        # Update completed date (auto-set if status is Complete and no date provided)
        if new_status == "✅ Complete":
            if not completed_date:
                completed_date = datetime.now().date().isoformat()
            properties["Completed Date"] = {"date": {"start": completed_date}}
            updated_props.append("Completed Date")

        # Handle decision notes (append logic)
        if decision_notes:
            # First, retrieve existing notes
            try:
                page = notion_client.pages.retrieve(page_id=page_id)
                existing_notes_prop = page.get("properties", {}).get("Decision Notes", {})
                existing_notes = ""
                if existing_notes_prop.get("rich_text"):
                    existing_notes = existing_notes_prop["rich_text"][0]["text"]["content"]

                # Append new notes with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d")
                new_notes = f"{existing_notes}\n\n[{timestamp}] {decision_notes}" if existing_notes else f"[{timestamp}] {decision_notes}"

                properties["Decision Notes"] = {
                    "rich_text": [{"text": {"content": new_notes}}]
                }
                updated_props.append("Decision Notes")
            except Exception as e:
                # If can't read existing notes, just write new ones
                timestamp = datetime.now().strftime("%Y-%m-%d")
                properties["Decision Notes"] = {
                    "rich_text": [{"text": {"content": f"[{timestamp}] {decision_notes}"}}]
                }
                updated_props.append("Decision Notes")

        # Update page
        if properties:
            notion_client.pages.update(page_id=page_id, properties=properties)

        return {
            "status": "success",
            "page_id": page_id,
            "updated_properties": updated_props,
            "message": f"Initiative updated successfully ({', '.join(updated_props)})"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Notion API error: {str(e)}"
        }


# ============================================================================
# TOOL 8: Write to Page Content (NEW)
# ============================================================================

@mcp.tool()
def write_to_page_content(
    page_id: str,
    content: str,
    fallback_path: Optional[str] = None
) -> dict:
    """
    Write markdown to Notion page content with graceful degradation.

    Args:
        page_id: Notion page ID
        content: Markdown content to write
        fallback_path: Repo path to save if Notion fails (e.g., "docs/context/one-pagers/initiative.md")

    Returns:
        Dict with write location (Notion URL or repo path)

    Examples:
        - write_to_page_content("page123", "# One-Pager\n\nContent here", "docs/context/one-pagers/feature.md")
    """
    # Check Notion client initialized
    if not notion_client:
        # Fall back to repo immediately if no Notion client
        if fallback_path:
            result = write_file(fallback_path, content)
            if result["status"] == "success":
                return {
                    "status": "success",
                    "location": "repo",
                    "path": fallback_path,
                    "message": "⚠️ Notion client not initialized. One-pager saved to repo."
                }
        return {
            "status": "error",
            "message": "Notion client not initialized and no fallback path provided."
        }

    try:
        # Convert markdown to Notion blocks (simple V1 implementation)
        blocks = markdown_to_notion_blocks(content)

        # Try to write to Notion
        notion_client.blocks.children.append(block_id=page_id, children=blocks)

        # Get page URL
        page = notion_client.pages.retrieve(page_id=page_id)
        page_url = page.get("url", "")

        return {
            "status": "success",
            "location": "notion",
            "url": page_url,
            "message": "One-pager written to Notion"
        }

    except Exception as e:
        # Graceful degradation: fall back to repo
        if fallback_path:
            result = write_file(fallback_path, content)
            if result["status"] == "success":
                return {
                    "status": "success",
                    "location": "repo",
                    "path": fallback_path,
                    "message": f"⚠️ Notion write failed ({str(e)}). One-pager saved to repo."
                }

        return {
            "status": "error",
            "message": f"Notion write failed and no fallback path provided. Error: {str(e)}"
        }


# ============================================================================
# Helper: Markdown to Notion Blocks
# ============================================================================

def markdown_to_notion_blocks(content: str) -> list:
    """
    Convert markdown to Notion blocks (simple V1 implementation).

    Supports:
    - Headings (# ## ###)
    - Paragraphs
    - Bulleted lists (- or *)
    - Code blocks (```)

    Does NOT support (V1 limitation):
    - Tables
    - Images
    - Embeds
    """
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading 1
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                }
            })
            i += 1

        # Heading 2
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                }
            })
            i += 1

        # Heading 3
        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                }
            })
            i += 1

        # Bulleted list
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()}}]
                }
            })
            i += 1

        # Code block
        elif line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": "plain text"
                }
            })
            i += 1

        # Paragraph (default)
        else:
            if line.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line.strip()}}]
                    }
                })
            i += 1

    return blocks


# ============================================================================
# Helper: Generate Handoff Template
# ============================================================================

def generate_handoff_template(
    summary: str,
    decisions: List[str],
    next_steps: List[str],
    prd_path: str,
    one_pager_location: str,
    initiative_id: str
) -> str:
    """
    Generate standardized handoff prompt for Claude Code.

    Template structure:
    1. Git commands (at top)
    2. Implementation mode (INTERACTIVE)
    3. What to build (goals, success criteria)
    4. Documents to reference (PRD, one-pager)
    5. High-level context
    6. Clarifying questions
    """
    # Generate topic for branch name
    topic = summary.lower().replace(" ", "-")[:30]
    topic = "".join(c for c in topic if c.isalnum() or c == "-")

    # Format decisions and next steps
    decisions_text = "\n".join(f"{i}. {d}" for i, d in enumerate(decisions, 1)) if decisions else "None documented"
    next_steps_text = "\n".join(f"{i}. {s}" for i, s in enumerate(next_steps, 1)) if next_steps else "See PRD for details"

    template = f"""# Handoff to Claude Code: {summary}

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**From**: Claude Chat (Sonnet 4.5)
**To**: Claude Code
**Project**: Epic 2nd Brain

---

## 🚀 Git Commands - RUN THESE FIRST

```bash
# Navigate to repo
cd ~/Documents/1.\\ Projects/ai-assistant/

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/{topic}

# Commit session log and handoff
git add docs/sessions/claude-chat/* docs/handoffs/*
git commit -m "feat: {summary}

Ref: Notion Strategy Board initiative"

# Push to remote
git push origin feature/{topic}
```

---

## 🎯 Implementation Mode: INTERACTIVE

**CRITICAL**: This is an **interactive implementation**, not autonomous coding.

**Your protocol**:
1. Read the PRD and one-pager thoroughly
2. Present **2-3 architectural options** for each major decision
3. **Wait for Dharan's choice** before proceeding
4. Only after alignment, create tech requirements
5. Only after tech requirements approved, start coding
6. After coding complete, **update documentation** (roadmap, tech req, implementation plan)

---

## 📋 What to Build

**Summary**: {summary}

**Decisions Made**:
{decisions_text}

**Next Steps**:
{next_steps_text}

---

## 📚 Documents to Reference

**Primary Documents**:
- **PRD**: `{prd_path}`
- **One-Pager**: `{one_pager_location}` (Notion URL or repo path)
- **Notion Initiative**: `https://www.notion.so/{initiative_id}`

---

## 🔑 High-Level Context

This handoff was generated from Claude Chat after PRD approval. The Strategy Board initiative has been updated to "🚀 In Progress".

**Why This Matters**:
- Aligns with current priorities (from Strategy Board)
- PRD reviewed and approved
- One-pager provides strategic context

---

## ❓ Clarifying Questions Before You Code

Before creating tech requirements, ask Dharan these questions:

1. **Tool Configurability**: Should new tools have hardcoded defaults or configurable parameters?
2. **Error Handling Strategy**: Fail-fast or retry with backoff when external APIs fail?
3. **Testing Strategy**: Mock external dependencies or test with real services?
4. **Integration Assumptions**: Any assumptions about git hooks, dependencies, or existing systems?
5. **Performance vs Simplicity**: Any trade-offs to discuss (e.g., sequential vs parallel processing)?

---

## 📝 Next Steps

1. Read PRD and one-pager thoroughly
2. Ask clarifying questions above
3. Create tech requirements document
4. Get approval on tech requirements
5. Implement features
6. Update documentation (roadmap, tech req, implementation plan)
7. Create session log and commit

---

**End of Handoff Prompt**
"""

    return template


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    mcp.run()
