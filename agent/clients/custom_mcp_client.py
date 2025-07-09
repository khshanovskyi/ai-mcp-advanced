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
        #TODO:
        # 1. Check if `self.http_session` is None, raise RuntimeError("HTTP session not initialized") if so
        # 2. Create `request_data` dictionary with:
        #       - "jsonrpc": "2.0"
        #       - "id": str(uuid.uuid4())
        #       - "method": method
        # 3. If `params` exists, add "params": params to `request_data`
        # 4. Create `headers` dictionary with:
        #       - "Content-Type": "application/json"
        #       - "Accept": "application/json, text/event-stream"
        # 5. Add session ID header for non-initialize requests:
        #       - If `method != "initialize"` and `self.session_id` exists, add `headers[MCP_SESSION_ID_HEADER] = self.session_id`
        # 6. Make async POST request using `self.http_session.post()` with:
        #       - url: self.server_url
        #       - json: request_data
        #       - headers: headers
        # 7. Inside the context manager:
        #       - If `not self.session_id` and `response.headers.get(MCP_SESSION_ID_HEADER)` exists, set `self.session_id = response.headers[MCP_SESSION_ID_HEADER]`
        #       - If `response.status == 204`, return empty dict `{}`
        #       - Call `await self._parse_sse_response(response)` and assign to `response_data`
        #       - If "error" in `response_data`, extract `error = response_data["error"]` and raise RuntimeError(f"MCP Error {error['code']}: {error['message']}")
        #       - Return `response_data`
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
        #TODO:
        # Response stream sample:
        # data: {
        #     "jsonrpc": "2.0",
        #     "id": 1,
        #     "result": {
        #         "content": [
        #             {
        #                 "type": "text",
        #                 "text": "some tool call result"
        #             }
        #         ]
        #     }
        # }
        # data: [DONE]
        # ---
        # 1. Get response content with `await response.text()` and assign to `content`
        # 2. Split content by newlines and strip whitespace: `lines = content.strip().split('\n')`
        # 3. Iterate through `lines`:
        #       - Strip each line: `line = line.strip()`
        #       - If line starts with 'data: ':
        #           - Extract data part: `data_part = line[6:]` (remove 'data: ' prefix)
        #           - If `data_part != '[DONE]'`, then `return json.loads(data_part)` (we just need first chunk since MCP tool returns response with 1 chunk)
        # 4. If no valid data found, raise RuntimeError("No valid data found in SSE response")
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
        #TODO:
        # 1. Set `self.server_url = mcp_server_url`
        # 2. Create new HTTP session: `self.http_session = aiohttp.ClientSession()`
        # 3. Try-except block:
        #       - Create `init_params` dictionary with:
        #           - "protocolVersion": "2024-11-05"
        #           - "capabilities": {"tools": {}}
        #           - "clientInfo": {"name": "my-custom-mcp-client", "version": "1.0.0"}
        #       - Call `await self._send_request("initialize", init_params)`
        #       - Call `await self._send_notification("notifications/initialized")`
        #       - Print "MCP client connected and initialized successfully"
        # 4. Catch Exception as `e` and raise RuntimeError(f"Failed to connect to MCP server: {e}")
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
        #TODO:
        # 1. Check if `self.http_session` is None, raise RuntimeError("HTTP session not initialized") if so
        # 2. Create `request_data` dictionary with:
        #       - "jsonrpc": "2.0"
        #       - "method": method
        # 3. Create `headers` dictionary with:
        #       - "Content-Type": "application/json"
        #       - "Accept": "application/json, text/event-stream" (Pay attention that it required both!)
        # 4. If `self.session_id` exists, add `headers[MCP_SESSION_ID_HEADER] = self.session_id`
        # 5. Make async POST request using `self.http_session.post()` with:
        #       - url: self.server_url
        #       - json: request_data
        #       - headers: headers
        # 6. Inside context manager:
        #       - If MCP_SESSION_ID_HEADER exists in `response.headers`, set `self.session_id = response.headers[MCP_SESSION_ID_HEADER]` and print session ID
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
        #TODO:
        # 1. Check if `self.http_session` is None, raise RuntimeError("MCP client not connected. Call connect() first.") if so
        # 2. Call `await self._send_request("tools/list")` and assign to `response`
        # 3. Extract tools from response: `tools = response["result"]["tools"]`
        # 4. Iterate through `tools` and return list comprehension that transforms each tool in tools to:
        #       {
        #           "type": "function",
        #           "function": {
        #               "name": tool["name"],
        #               "description": tool["description"],
        #               "parameters": tool["inputSchema"]
        #           }
        #       }
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
        #TODO:
        # 1. Check if `self.http_session` is None, raise RuntimeError("MCP client not connected. Call connect() first.") if so
        # 2. print(f"    Calling `{tool_name}` with {tool_args}")
        # 3. Create `params` dictionary with:
        #       - "name": tool_name
        #       - "arguments": tool_args
        # 4. Call `await self._send_request("tools/call", params)` and assign to `response`
        #       response sample: 
        #       {
        #           "jsonrpc": "2.0",
        #           "id": 1,
        #           "result": {
        #               "content": [
        #                   {
        #                       "type": "text",
        #                       "text": "some tool call result"
        #                   }
        #                ]
        #           }
        #       }
        # 5. Extract content using walrus operator: `if content:= response["result"].get("content", [])`
        # 6. Extract first item using walrus operator: `if item := content[0]`
        # 7. Extract text result: `text_result = item.get("text", "")`
        # 8. print(f"    ⚙️: {text_result}\n")
        # 9. Return `text_result`
        # 10. If no content found, return "Unexpected error occurred!"
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