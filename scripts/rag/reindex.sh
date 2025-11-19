#!/bin/bash
# Daily reindex script for Legacy AI RAG
# Run by launchd at 7am daily

# Set up logging
LOG_DIR="$HOME/.cache/legacy-ai-rag/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/reindex-$(date +%Y-%m-%d).log"

echo "=== Reindex started at $(date) ===" >> "$LOG_FILE"

# Change to project directory
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Run incremental reindex
/Users/dharanchandrahasan/.pyenv/versions/3.11.0/bin/python -m scripts.rag.indexer >> "$LOG_FILE" 2>&1

echo "=== Reindex completed at $(date) ===" >> "$LOG_FILE"

# Keep only last 7 days of logs
find "$LOG_DIR" -name "reindex-*.log" -mtime +7 -delete
