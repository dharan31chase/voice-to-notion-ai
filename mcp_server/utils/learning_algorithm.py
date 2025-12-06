"""
Learning Algorithm Module (Phase 4.2)

Analyzes usage logs to improve context suggestions:
- Score files by load frequency, recency, co-occurrence
- Update context-profiles.json with learned patterns
- Rank suggestions by score (target: 80% accuracy)

Usage:
    from mcp_server.utils.learning_algorithm import analyze_usage_logs, get_file_recommendations

    # Analyze all usage logs
    scores = analyze_usage_logs(project="Epic 2nd Brain")

    # Get top recommendations for a workstream
    recommendations = get_file_recommendations(
        project="Epic 2nd Brain",
        workstream="context-engineering",
        top_k=10
    )
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import math


def analyze_usage_logs(
    project: str = "Epic 2nd Brain",
    logs_dir: Optional[Path] = None,
    lookback_days: int = 30
) -> Dict[str, float]:
    """
    Analyze usage logs to score files by frequency, recency, co-occurrence.

    Algorithm:
    1. Frequency Score: # of loads / total sessions
    2. Recency Score: Exponential decay (recent loads score higher)
    3. Co-occurrence Score: Files loaded together in same session

    Final Score = (0.4 * frequency) + (0.3 * recency) + (0.3 * co-occurrence)

    Args:
        project: Project name
        logs_dir: Optional logs directory (default: logs/usage/)
        lookback_days: Only analyze logs from last N days

    Returns:
        Dict[file_path, score] sorted by score (descending)
    """
    # Default logs directory
    if logs_dir is None:
        logs_dir = Path.home() / "Documents/1. Projects/ai-assistant/logs/usage"

    if not logs_dir.exists():
        return {}

    # Get logs from last N days
    cutoff_date = datetime.now() - timedelta(days=lookback_days)
    log_files = []

    for log_file in logs_dir.glob("*.json"):
        # Parse timestamp from filename (YYYY-MM-DD-HH-MM-SS.json)
        try:
            filename = log_file.stem  # Remove .json
            # Extract date part (YYYY-MM-DD)
            date_str = "-".join(filename.split("-")[:3])
            log_date = datetime.strptime(date_str, "%Y-%m-%d")

            if log_date >= cutoff_date:
                log_files.append(log_file)
        except (ValueError, IndexError):
            # Skip files with invalid timestamps
            continue

    if not log_files:
        return {}

    # Data structures for scoring
    file_load_counts = Counter()  # file -> # of loads
    file_last_accessed = {}  # file -> last access timestamp
    file_sessions = defaultdict(set)  # file -> set of session IDs
    session_files = defaultdict(set)  # session_id -> set of files

    total_sessions = 0

    # Parse all logs
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)

            # Filter by project
            if data["metadata"]["project"] != project:
                continue

            session_id = data["metadata"]["session_id"]
            total_sessions += 1

            # Track file loads
            for load in data["events"]["loads"]:
                file_path = load["file"]
                timestamp = load["timestamp"]

                file_load_counts[file_path] += 1
                file_sessions[file_path].add(session_id)
                session_files[session_id].add(file_path)

                # Update last accessed timestamp
                if file_path not in file_last_accessed or timestamp > file_last_accessed[file_path]:
                    file_last_accessed[file_path] = timestamp

        except (json.JSONDecodeError, KeyError) as e:
            # Skip corrupted logs
            continue

    if total_sessions == 0:
        return {}

    # Compute scores
    file_scores = {}

    for file_path in file_load_counts:
        # 1. Frequency Score (0-1): # of sessions with file / total sessions
        session_count = len(file_sessions[file_path])
        frequency_score = session_count / total_sessions

        # 2. Recency Score (0-1): Exponential decay from last access
        last_access_str = file_last_accessed.get(file_path)
        if last_access_str:
            try:
                last_access = datetime.fromisoformat(last_access_str)
                days_ago = (datetime.now() - last_access).days
                # Exponential decay: score = exp(-days/half_life)
                # half_life = 7 days (score drops to 0.5 after 1 week)
                recency_score = math.exp(-days_ago / 7.0)
            except ValueError:
                recency_score = 0.0
        else:
            recency_score = 0.0

        # 3. Co-occurrence Score (0-1): Avg # of co-loaded files
        # Files that appear with many other files score higher (indicative of importance)
        co_occurrence_count = 0
        for session_id in file_sessions[file_path]:
            co_occurrence_count += len(session_files[session_id]) - 1  # -1 to exclude self

        if session_count > 0:
            avg_co_occurrence = co_occurrence_count / session_count
            # Normalize by max (assume max 20 files per session)
            co_occurrence_score = min(avg_co_occurrence / 20.0, 1.0)
        else:
            co_occurrence_score = 0.0

        # Combine scores (weighted average)
        final_score = (
            0.4 * frequency_score +
            0.3 * recency_score +
            0.3 * co_occurrence_score
        )

        file_scores[file_path] = final_score

    # Sort by score (descending)
    sorted_scores = dict(sorted(file_scores.items(), key=lambda x: x[1], reverse=True))

    return sorted_scores


def get_file_recommendations(
    project: str = "Epic 2nd Brain",
    workstream: Optional[str] = None,
    top_k: int = 10,
    min_score: float = 0.1
) -> List[Dict]:
    """
    Get file recommendations based on usage patterns.

    Args:
        project: Project name
        workstream: Optional workstream filter (e.g., "context-engineering")
        top_k: Number of recommendations to return
        min_score: Minimum score threshold

    Returns:
        List of dicts with file, score, reason
    """
    # Analyze usage logs
    scores = analyze_usage_logs(project=project)

    # Filter by workstream if provided
    if workstream:
        # Filter files that match workstream keywords
        workstream_keywords = workstream.lower().replace("-", " ").split()
        filtered_scores = {}

        for file_path, score in scores.items():
            file_lower = file_path.lower()
            # Check if any keyword appears in file path
            if any(keyword in file_lower for keyword in workstream_keywords):
                filtered_scores[file_path] = score

        scores = filtered_scores

    # Build recommendations
    recommendations = []
    for file_path, score in list(scores.items())[:top_k]:
        if score < min_score:
            break

        # Generate reason
        if score > 0.7:
            reason = "Frequently accessed (high confidence)"
        elif score > 0.5:
            reason = "Recently accessed"
        elif score > 0.3:
            reason = "Often loaded with other files"
        else:
            reason = "Previously accessed"

        recommendations.append({
            "file": file_path,
            "score": round(score, 3),
            "reason": reason
        })

    return recommendations


def update_context_profile_with_learned_patterns(
    project: str = "Epic 2nd Brain",
    workstream: str = "context-engineering",
    config_path: Optional[Path] = None
) -> Dict:
    """
    Update context-profiles.json with learned patterns from usage logs.

    Args:
        project: Project name
        workstream: Workstream name
        config_path: Optional path to context-profiles.json

    Returns:
        Dict with update status
    """
    # Default config path
    if config_path is None:
        config_path = Path.home() / "Documents/1. Projects/ai-assistant/docs/config/context-profiles.json"

    # Load existing profile
    if config_path.exists():
        with open(config_path, 'r') as f:
            profiles = json.load(f)
    else:
        profiles = {}

    # Get recommendations
    recommendations = get_file_recommendations(
        project=project,
        workstream=workstream,
        top_k=20  # Get top 20 for profile
    )

    # Update profile
    if project not in profiles:
        profiles[project] = {}

    if workstream not in profiles[project]:
        profiles[project][workstream] = {}

    # Add learned files
    learned_files = [rec["file"] for rec in recommendations]

    profiles[project][workstream]["learned_files"] = learned_files
    profiles[project][workstream]["last_updated"] = datetime.now().isoformat()
    profiles[project][workstream]["total_recommendations"] = len(learned_files)

    # Save updated profile
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "project": project,
        "workstream": workstream,
        "learned_files_count": len(learned_files),
        "config_path": str(config_path)
    }


def get_co_occurrence_matrix(
    project: str = "Epic 2nd Brain",
    logs_dir: Optional[Path] = None
) -> Dict[str, Dict[str, int]]:
    """
    Build co-occurrence matrix: which files are loaded together.

    Returns:
        Dict[file_a, Dict[file_b, count]]
        Example: {"ROADMAP.md": {"docs/prd/x.md": 5, "docs/tech-requirements/y.md": 3}}
    """
    if logs_dir is None:
        logs_dir = Path.home() / "Documents/1. Projects/ai-assistant/logs/usage"

    if not logs_dir.exists():
        return {}

    co_occurrence = defaultdict(lambda: defaultdict(int))

    # Parse all logs
    for log_file in logs_dir.glob("*.json"):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)

            # Filter by project
            if data["metadata"]["project"] != project:
                continue

            # Get files loaded in this session
            files_in_session = set(load["file"] for load in data["events"]["loads"])

            # Build co-occurrence pairs
            for file_a in files_in_session:
                for file_b in files_in_session:
                    if file_a != file_b:
                        co_occurrence[file_a][file_b] += 1

        except (json.JSONDecodeError, KeyError):
            continue

    # Convert to regular dict
    return {k: dict(v) for k, v in co_occurrence.items()}


def suggest_related_files(
    file_path: str,
    project: str = "Epic 2nd Brain",
    top_k: int = 5
) -> List[Dict]:
    """
    Suggest files that are often loaded together with the given file.

    Args:
        file_path: File to find related files for
        project: Project name
        top_k: Number of suggestions

    Returns:
        List of dicts with file, co_occurrence_count, reason
    """
    co_matrix = get_co_occurrence_matrix(project=project)

    if file_path not in co_matrix:
        return []

    # Sort by co-occurrence count
    related = sorted(
        co_matrix[file_path].items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    suggestions = []
    for related_file, count in related:
        suggestions.append({
            "file": related_file,
            "co_occurrence_count": count,
            "reason": f"Often loaded together ({count} times)"
        })

    return suggestions
