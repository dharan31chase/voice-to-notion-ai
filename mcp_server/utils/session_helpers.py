"""
Session Helper Functions

Provides utilities for session management:
- High-signal session template generation
- Initiative detection and validation
"""

from datetime import datetime
from typing import List, Optional, Dict
from notion_client import Client


def generate_high_signal_session_template(
    summary: str,
    what_worked: Optional[List[str]] = None,
    what_didnt_work: Optional[List[str]] = None,
    decisions: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    initiative_name: Optional[str] = None,
    session_duration_hours: Optional[float] = None
) -> str:
    """
    Generate high-signal session log template.

    Template structure:
    1. Session metadata (date, duration, initiative)
    2. Summary (1-2 sentences)
    3. What Worked (successes, wins)
    4. What Didn't Work (blockers, issues)
    5. Decisions Made
    6. Next Steps

    Args:
        summary: Brief summary of session (1-2 sentences)
        what_worked: List of things that worked well
        what_didnt_work: List of blockers or issues
        decisions: List of key decisions made
        next_steps: List of recommended next actions
        initiative_name: Name of linked initiative
        session_duration_hours: Session duration in hours

    Returns:
        Formatted session log markdown
    """
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Format lists with proper markdown
    what_worked_text = "\n".join(f"- {item}" for item in (what_worked or ["None documented"])) if what_worked else "- None documented"
    what_didnt_work_text = "\n".join(f"- {item}" for item in (what_didnt_work or ["None documented"])) if what_didnt_work else "- None documented"
    decisions_text = "\n".join(f"{i}. {d}" for i, d in enumerate(decisions or [], 1)) if decisions else "None documented"
    next_steps_text = "\n".join(f"{i}. {s}" for i, s in enumerate(next_steps or [], 1)) if next_steps else "See linked documents for details"

    # Build duration line
    duration_line = f"**Duration**: {session_duration_hours}h\n" if session_duration_hours else ""

    # Build initiative line
    initiative_line = f"**Initiative**: {initiative_name}\n" if initiative_name else ""

    template = f"""# Session: {date_str} - Claude Chat

**Project**: Epic 2nd Brain
{initiative_line}{duration_line}**Status**: Complete
**Session Type**: Planning

---

## Summary

{summary}

---

## What Worked ✅

{what_worked_text}

---

## What Didn't Work ⚠️

{what_didnt_work_text}

---

## Decisions Made

{decisions_text}

---

## Next Steps

{next_steps_text}

---

*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return template


def check_initiative_exists(
    notion_client: Client,
    initiative_name: str,
    project_name: str,
    strategy_board_db_id: str
) -> Dict:
    """
    Check if initiative exists in Strategy Board, prompt if not.

    Args:
        notion_client: Notion client instance
        initiative_name: Name of initiative to check
        project_name: Project name for filtering
        strategy_board_db_id: Strategy Board database ID

    Returns:
        Dict with initiative_found, message, options, and initiative data

    Example:
        >>> result = check_initiative_exists(
        ...     notion_client,
        ...     "Context Engineering",
        ...     "Epic 2nd Brain",
        ...     "strategy_board_db_id"
        ... )
        >>> if not result["initiative_found"]:
        ...     print(result["options"])
    """
    try:
        # Query Strategy Board for initiative
        response = notion_client.databases.query(
            database_id=strategy_board_db_id,
            filter={
                "property": "Initiative Name",
                "title": {
                    "contains": initiative_name
                }
            }
        )

        results = response.get("results", [])

        if not results:
            # Initiative not found - return options
            return {
                "initiative_found": False,
                "message": f"Initiative '{initiative_name}' not found in Strategy Board.",
                "options": [
                    "1. Create new initiative in Strategy Board",
                    "2. Search for similar initiatives (maybe typo?)",
                    "3. Proceed without linking to Strategy Board (ad-hoc session)"
                ],
                "action_required": "Choose option 1, 2, or 3"
            }

        # Found - return first match (or multiple if ambiguous)
        if len(results) == 1:
            initiative = results[0]
            initiative_id = initiative["id"]

            # Extract initiative name
            title_prop = initiative["properties"].get("Initiative Name", {})
            name = ""
            if title_prop.get("title"):
                name = title_prop["title"][0]["text"]["content"]

            # Extract status
            status_prop = initiative["properties"].get("Status", {}).get("select", {})
            status = status_prop.get("name", "Unknown")

            return {
                "initiative_found": True,
                "initiative": {
                    "id": initiative_id,
                    "name": name,
                    "status": status,
                    "url": initiative.get("url", "")
                },
                "message": f"Found initiative: {name} (Status: {status})"
            }

        else:
            # Multiple matches - let user choose
            initiatives_list = []
            for initiative in results[:5]:  # Show max 5
                title_prop = initiative["properties"].get("Initiative Name", {})
                name = title_prop["title"][0]["text"]["content"] if title_prop.get("title") else "Unnamed"

                status_prop = initiative["properties"].get("Status", {}).get("select", {})
                status = status_prop.get("name", "Unknown")

                initiatives_list.append({
                    "id": initiative["id"],
                    "name": name,
                    "status": status
                })

            return {
                "initiative_found": False,
                "ambiguous": True,
                "message": f"Found {len(results)} initiatives matching '{initiative_name}'.",
                "initiatives": initiatives_list,
                "action_required": "Choose which initiative to link, or proceed without linking"
            }

    except Exception as e:
        return {
            "initiative_found": False,
            "error": True,
            "message": f"Error checking initiative: {str(e)}",
            "action_required": "Proceed without linking (Notion unavailable)"
        }


def search_similar_initiatives(
    notion_client: Client,
    search_query: str,
    strategy_board_db_id: str,
    limit: int = 5
) -> List[Dict]:
    """
    Search for similar initiatives in Strategy Board.

    Args:
        notion_client: Notion client instance
        search_query: Search query
        strategy_board_db_id: Strategy Board database ID
        limit: Max results to return

    Returns:
        List of initiative dicts with id, name, status

    Example:
        >>> results = search_similar_initiatives(
        ...     notion_client,
        ...     "context engineering",
        ...     "strategy_board_db_id"
        ... )
        >>> for initiative in results:
        ...     print(f"{initiative['name']} - {initiative['status']}")
    """
    try:
        # Query Strategy Board with partial match
        response = notion_client.databases.query(
            database_id=strategy_board_db_id,
            filter={
                "property": "Initiative Name",
                "title": {
                    "contains": search_query
                }
            },
            page_size=limit
        )

        results = []
        for page in response.get("results", []):
            title_prop = page["properties"].get("Initiative Name", {})
            name = ""
            if title_prop.get("title"):
                name = title_prop["title"][0]["text"]["content"]

            status_prop = page["properties"].get("Status", {}).get("select", {})
            status = status_prop.get("name", "Unknown")

            results.append({
                "id": page["id"],
                "name": name,
                "status": status,
                "url": page.get("url", "")
            })

        return results

    except Exception as e:
        return []


def create_initiative_in_strategy_board(
    notion_client: Client,
    initiative_name: str,
    project_name: str,
    strategy_board_db_id: str,
    projects_db_id: Optional[str] = None,
    priority_score: int = 50,
    category: str = "Enhancement"
) -> Dict:
    """
    Create new initiative in Strategy Board.

    Args:
        notion_client: Notion client instance
        initiative_name: Name of initiative
        project_name: Project name
        strategy_board_db_id: Strategy Board database ID
        projects_db_id: Projects database ID (for relation)
        priority_score: Initial priority score (default: 50)
        category: Initiative category (default: "Enhancement")

    Returns:
        Dict with status, initiative_id, and url

    Example:
        >>> result = create_initiative_in_strategy_board(
        ...     notion_client,
        ...     "New Feature Implementation",
        ...     "Epic 2nd Brain",
        ...     "strategy_board_db_id"
        ... )
        >>> if result["status"] == "success":
        ...     print(f"Created: {result['url']}")
    """
    try:
        # Build properties
        properties = {
            "Initiative Name": {
                "title": [{"text": {"content": initiative_name}}]
            },
            "Status": {
                "select": {"name": "🟡 Needs Decision"}
            },
            "Priority Score": {
                "number": priority_score
            },
            "Category": {
                "select": {"name": category}
            }
        }

        # Add project relation if Projects DB provided
        if projects_db_id:
            try:
                # Find project page ID
                projects_response = notion_client.databases.query(
                    database_id=projects_db_id,
                    filter={
                        "property": "Name",
                        "title": {"equals": project_name}
                    }
                )

                if projects_response.get("results"):
                    project_page_id = projects_response["results"][0]["id"]
                    properties["Project"] = {
                        "relation": [{"id": project_page_id}]
                    }
            except Exception:
                # Proceed without project relation if lookup fails
                pass

        # Create page
        page = notion_client.pages.create(
            parent={"database_id": strategy_board_db_id},
            properties=properties
        )

        return {
            "status": "success",
            "initiative_id": page["id"],
            "url": page.get("url", ""),
            "message": f"Created initiative: {initiative_name}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating initiative: {str(e)}"
        }
