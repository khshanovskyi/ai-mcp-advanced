import json
import uuid
from typing import Optional, Any
import aiohttp


MCP_SESSION_ID_HEADER = "Mcp-Session-Id"

class CustomMCPClient:
    """Pure Python MCP client without external MCP libraries"""

    def __init__(self, ) -> None:
        self.server_url = None
        self.session_id: Optional[str] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def _send_request(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Send JSON-RPC request to MCP server"""
        if not self.http_session:
            raise RuntimeError("HTTP session not initialized")

        request_data: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method
        }

        if params:
            request_data["params"] = params

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # Add session ID header for non-initialize requests
        if method != "initialize" and self.session_id:
            headers[MCP_SESSION_ID_HEADER] = self.session_id

        async with self.http_session.post(
                self.server_url,
                json=request_data,
                headers=headers
        ) as response:
            if not self.session_id and response.headers.get(MCP_SESSION_ID_HEADER):
                self.session_id = response.headers[MCP_SESSION_ID_HEADER]

            if response.status == 204:
                return {}

            response_data = await self._parse_sse_response(response)

            if "error" in response_data:
                error = response_data["error"]
                raise RuntimeError(f"MCP Error {error['code']}: {error['message']}")

            return response_data

    async def _parse_sse_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        """Parse Server-Sent Events response"""
        content = await response.text()
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('data: '):
                data_part = line[6:]
                if data_part != '[DONE]':
                    return json.loads(data_part)

        raise RuntimeError("No valid data found in SSE response")

    async def connect(self, mcp_server_url: str) -> None:
        """Connect to MCP server and initialize session"""
        self.server_url = mcp_server_url
        self.http_session = aiohttp.ClientSession()

        try:
            init_params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "clientInfo": {
                    "name": "my-custom-mcp-client",
                    "version": "1.0.0"
                }
            }

            await self._send_request("initialize", init_params)
            await self._send_notification("notifications/initialized")
            print("MCP client connected and initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MCP server: {e}")

    async def _send_notification(self, method: str) -> None:
        """Send notification (no response expected)"""
        if not self.http_session:
            raise RuntimeError("HTTP session not initialized")

        request_data: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        if self.session_id:
            headers[MCP_SESSION_ID_HEADER] = self.session_id

        async with self.http_session.post(
                self.server_url,
                json=request_data,
                headers=headers
        ) as response:
            # Extract session ID from response headers if available
            if MCP_SESSION_ID_HEADER in response.headers:
                self.session_id = response.headers[MCP_SESSION_ID_HEADER]
                print(f"Session ID: {self.session_id}")

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get available tools from MCP server"""
        if not self.http_session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        response = await self._send_request("tools/list")
        tools = response["result"]["tools"]
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            for tool in tools
        ]

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server"""
        if not self.http_session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        print(f"    Calling `{tool_name}` with {tool_args}")

        params = {
            "name": tool_name,
            "arguments": tool_args
        }

        response = await self._send_request("tools/call", params)

        if content:= response["result"].get("content", []):
            if item := content[0]:
                text_result = item.get("text", "")
                print(f"    ⚙️: {text_result}\n")
                return text_result

        return "Unexpected error occurred!"