"""
MCP Server for Legacy AI RAG

Exposes RAG tools via Model Context Protocol for Claude Chat integration.
"""

import json
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to stderr only (MCP requires clean stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Suppress structlog output to stdout
import structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

from .mcp_tools import get_rag
from .storage import VectorStore

# Store last search results for dive deeper functionality
_last_search_results = []


def search_legacy_corpus(
    query: str,
    top_k: int = 5,
    content_type: str = None,
    customer_name: str = None
) -> str:
    """Search the Legacy AI corpus and return formatted results with metadata for dive deeper."""
    global _last_search_results

    rag = get_rag()
    results = rag.search(
        query=query,
        top_k=top_k,
        content_type=content_type,
        customer_name=customer_name,
        use_reranker=True
    )

    # Store for dive deeper
    _last_search_results = results

    if not results:
        return f"No results found for query: '{query}'"

    # Format results with metadata for dive deeper
    output = [f"## Search Results for: '{query}'\n"]
    output.append(f"Found {len(results)} relevant chunks:\n")

    for i, result in enumerate(results, 1):
        meta = result["metadata"]

        output.append(f"### Result {i}")
        output.append(f"**Source**: {meta['document_title']}")
        output.append(f"**Customer**: {meta['customer_name']}")
        output.append(f"**Type**: {meta['content_type']}")
        output.append(f"**Section**: {meta['section_header']}")

        if "score" in result:
            output.append(f"**Score**: {result['score']:.4f}")

        # Include metadata for dive deeper
        output.append(f"**Chunk ID**: `{result['id']}`")
        output.append(f"**File**: `{meta['source_file']}`")

        output.append(f"\n{result['text']}\n")
        output.append("---\n")

    output.append("\n*To dive deeper, use `get_chunk_context` with the Chunk ID or `read_source_document` with the File path.*")

    return "\n".join(output)


def get_chunk_context(chunk_id: str, lines_before: int = 30, lines_after: int = 30) -> str:
    """Get surrounding context for a chunk from its source file."""
    global _last_search_results

    # Find the chunk in last results or fetch from storage
    chunk_meta = None
    chunk_text = None

    for result in _last_search_results:
        if result["id"] == chunk_id:
            chunk_meta = result["metadata"]
            chunk_text = result["text"]
            break

    if not chunk_meta:
        # Fetch from storage
        rag = get_rag()
        config = rag._config
        store = VectorStore(
            persist_directory=config["storage"]["persist_directory"],
            collection_name=config["storage"]["collection_name"]
        )
        chunk = store.get_by_id(chunk_id)
        if chunk:
            chunk_meta = chunk["metadata"]
            chunk_text = chunk["text"]
        else:
            return f"Chunk not found: {chunk_id}"

    # Read source file
    source_file = Path(chunk_meta["source_file"])
    if not source_file.exists():
        return f"Source file not found: {source_file}"

    content = source_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the chunk text in the file
    chunk_first_line = chunk_text.split("\n")[0][:50]  # First 50 chars of chunk

    start_line = 0
    for i, line in enumerate(lines):
        if chunk_first_line in line:
            start_line = i
            break

    # Get surrounding context
    context_start = max(0, start_line - lines_before)
    context_end = min(len(lines), start_line + lines_after)

    context_lines = lines[context_start:context_end]

    output = [
        f"## Context for Chunk: {chunk_id}\n",
        f"**Source**: {chunk_meta['document_title']}",
        f"**Section**: {chunk_meta['section_header']}",
        f"**File**: `{chunk_meta['source_file']}`",
        f"**Lines**: {context_start + 1} - {context_end}\n",
        "---\n",
        "\n".join(context_lines),
        "\n---\n",
        f"*Showing {len(context_lines)} lines. Use `read_source_document` to see the full file.*"
    ]

    return "\n".join(output)


def read_source_document(file_path: str, max_lines: int = 500) -> str:
    """Read a source document from the corpus."""
    path = Path(file_path).expanduser()

    if not path.exists():
        return f"File not found: {file_path}"

    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    if len(lines) > max_lines:
        truncated = lines[:max_lines]
        output = [
            f"## Document: {path.name}\n",
            f"**Full path**: `{path}`",
            f"**Total lines**: {len(lines)} (showing first {max_lines})\n",
            "---\n",
            "\n".join(truncated),
            f"\n\n... [Truncated - {len(lines) - max_lines} more lines] ..."
        ]
    else:
        output = [
            f"## Document: {path.name}\n",
            f"**Full path**: `{path}`",
            f"**Total lines**: {len(lines)}\n",
            "---\n",
            content
        ]

    return "\n".join(output)


def get_customer_info(customer_name: str) -> str:
    """Get comprehensive information about a specific customer."""
    rag = get_rag()
    return rag.get_customer_context(customer_name)


def list_interview_customers() -> str:
    """List all interviewed customers."""
    rag = get_rag()
    customers = rag.list_customers()

    if not customers:
        return "No customers found in the corpus."

    output = ["## Interviewed Customers\n"]
    for customer in customers:
        output.append(f"- {customer}")

    return "\n".join(output)


def get_corpus_stats() -> str:
    """Get corpus statistics."""
    rag = get_rag()
    stats = rag.stats()

    output = [
        "## Legacy AI Corpus Statistics\n",
        f"- **Total Chunks**: {stats['total_chunks']}",
        f"- **Total Documents**: {stats['total_documents']}",
        f"- **Total Tokens**: {stats['total_tokens']:,}",
        "\n### Content Types:"
    ]

    for ct, count in stats.get("content_types", {}).items():
        output.append(f"- {ct}: {count} chunks")

    return "\n".join(output)


# MCP Tool Definitions
TOOLS = [
    {
        "name": "search_legacy_corpus",
        "description": """Search the Legacy AI customer discovery corpus.

Searches through customer interviews, analyses, and insights. Returns results with Chunk IDs and File paths that can be used with get_chunk_context or read_source_document to dive deeper.

Example queries:
- "What are the main customer pain points?"
- "How do customers organize photos?"
- "Tell me about Ripanshi"
- "Product requirements across customers" """,
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results (default: 5)",
                    "default": 5
                },
                "content_type": {
                    "type": "string",
                    "description": "Filter: 'transcript', 'analysis', 'insight', 'guide'",
                    "enum": ["transcript", "analysis", "insight", "guide"]
                },
                "customer_name": {
                    "type": "string",
                    "description": "Filter by customer name"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_chunk_context",
        "description": """Get surrounding context for a search result.

Use this to "dive deeper" on a specific result. Pass the Chunk ID from search results to see more context from the source file (30 lines before and after by default).""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chunk_id": {
                    "type": "string",
                    "description": "The Chunk ID from search results (e.g., 'a1b2c3d4_001_002')"
                },
                "lines_before": {
                    "type": "integer",
                    "description": "Lines of context before (default: 30)",
                    "default": 30
                },
                "lines_after": {
                    "type": "integer",
                    "description": "Lines of context after (default: 30)",
                    "default": 30
                }
            },
            "required": ["chunk_id"]
        }
    },
    {
        "name": "read_source_document",
        "description": """Read a full source document from the corpus.

Use this to read an entire interview transcript, analysis, or other document. Pass the File path from search results.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Full path to the document"
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum lines to return (default: 500)",
                    "default": 500
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "get_customer_info",
        "description": """Get comprehensive information about a specific interviewed customer.

Retrieves all relevant context including profile, transcripts, analysis, and key insights.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer name (e.g., 'Ripanshi', 'Rob Halpern')"
                }
            },
            "required": ["customer_name"]
        }
    },
    {
        "name": "list_interview_customers",
        "description": "List all customers who have been interviewed.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_corpus_stats",
        "description": "Get statistics about the Legacy AI corpus (chunks, documents, tokens).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_tool_call(name: str, arguments: dict) -> str:
    """Handle a tool call and return the result."""
    try:
        if name == "search_legacy_corpus":
            return search_legacy_corpus(
                query=arguments["query"],
                top_k=arguments.get("top_k", 5),
                content_type=arguments.get("content_type"),
                customer_name=arguments.get("customer_name")
            )
        elif name == "get_chunk_context":
            return get_chunk_context(
                chunk_id=arguments["chunk_id"],
                lines_before=arguments.get("lines_before", 30),
                lines_after=arguments.get("lines_after", 30)
            )
        elif name == "read_source_document":
            return read_source_document(
                file_path=arguments["file_path"],
                max_lines=arguments.get("max_lines", 500)
            )
        elif name == "get_customer_info":
            return get_customer_info(arguments["customer_name"])
        elif name == "list_interview_customers":
            return list_interview_customers()
        elif name == "get_corpus_stats":
            return get_corpus_stats()
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        logger.error("tool_call_failed", tool=name, error=str(e))
        return f"Error executing {name}: {str(e)}"


def read_message() -> dict:
    """Read a JSON-RPC message from stdin."""
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)


def write_message(message: dict):
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def main():
    """Main MCP server loop."""
    logger.info("mcp_server_started")

    while True:
        try:
            message = read_message()
            if message is None:
                break

            method = message.get("method")
            msg_id = message.get("id")
            params = message.get("params", {})

            if method == "initialize":
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "legacy-ai-rag",
                            "version": "0.1.0"
                        }
                    }
                })

            elif method == "tools/list":
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": TOOLS
                    }
                })

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)

                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                })

            elif method == "notifications/initialized":
                pass

            else:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })

        except Exception as e:
            logger.error("mcp_server_error", error=str(e))
            if msg_id:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                })


if __name__ == "__main__":
    main()
