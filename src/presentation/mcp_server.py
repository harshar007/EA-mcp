"""
Electronics RAG Model Context Protocol (MCP) Server.
Clean Architecture - Presentation Layer.
Exposes electronics domain knowledge tools over standard stdio / JSON-RPC / SSE for AI Agents.
"""
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
from src.application.mcp_service import MCPService
from src.infrastructure.config import settings


class ElectronicsMCPServer:
    """Standard Model Context Protocol (MCP) Server for Electronics RAG."""

    def __init__(self):
        self.service = MCPService()

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches tool execution to the application service."""
        if tool_name == "query_electronics_knowledge":
            query = arguments.get("query", "")
            category = arguments.get("category")
            top_k = int(arguments.get("top_k", 4))
            return self.service.query_electronics(query=query, category=category, top_k=top_k)

        elif tool_name == "list_electronics_categories":
            return self.service.list_categories()

        elif tool_name == "get_system_health":
            return self.service.get_health()

        elif tool_name == "trigger_ingestion_pipeline":
            source_dir = arguments.get("source_directory")
            return self.service.run_ingestion(source_dir=source_dir)

        else:
            raise ValueError(f"Unknown MCP tool requested: '{tool_name}'")

    def run_stdio(self):
        """Runs the MCP server over standard input/output (stdio JSON-RPC)."""
        sys.stderr.write(f"[{settings.MCP_SERVER_NAME}] Electronics RAG MCP Server initialized (stdio transport).\n")
        sys.stderr.flush()

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                line_str = line.strip()
                if not line_str:
                    continue

                try:
                    request = json.loads(line_str)
                except json.JSONDecodeError:
                    continue

                req_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})

                # Handle MCP Protocol Methods
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": settings.MCP_SERVER_NAME,
                                "version": "1.0.0"
                            }
                        }
                    }

                elif method == "notifications/initialized":
                    continue  # Notification, no response needed

                elif method == "tools/list":
                    tools = self.service.get_registered_tools()
                    tools_list = [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema
                        }
                        for t in tools
                    ]
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": tools_list
                        }
                    }

                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    try:
                        result_data = self.handle_tool_call(tool_name, arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result_data, indent=2)
                                    }
                                ],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Error executing {tool_name}: {str(e)}"
                                    }
                                ],
                                "isError": True
                            }
                        }

                elif method == "ping":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {}
                    }

                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found"
                        }
                    }

                # Send JSON-RPC response
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except Exception as ex:
                sys.stderr.write(f"Server loop error: {ex}\n")
                sys.stderr.flush()


def main():
    server = ElectronicsMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
