import os
import uuid
import asyncio

from mcp_server.models.request import MCPRequest
from mcp_server.models.response import MCPResponse, ErrorResponse
from mcp_server.tools.calculator import CalculatorTool
from mcp_server.tools.web_search import WebSearchTool


class MCPSession:
    """Represents an MCP session with state management"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.ready_for_operation = False
        self.created_at = asyncio.get_event_loop().time()
        self.last_activity = self.created_at


class MCPServer:

    def __init__(self):
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "mcp-tools-server",
            "version": "1.0.0"
        }

        # Session management
        self.sessions: dict[str, MCPSession] = {}
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available tools"""
        calculator = CalculatorTool()
        self.tools[calculator.name] = calculator

        web_search = WebSearchTool(
            api_key=os.getenv("DIAL_API_KEY"),
            endpoint=os.getenv("DIAL_ENDPOINT", "https://ai-proxy.lab.epam.com")
        )
        self.tools[web_search.name] = web_search

    def _validate_protocol_version(self, client_version: str) -> str:
        """Validate and negotiate protocol version"""
        supported_versions = ["2024-11-05"]
        if client_version in supported_versions:
            return client_version
        return self.protocol_version

    def get_session(self, session_id: str) -> MCPSession | None:
        """Get an existing session"""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = asyncio.get_event_loop().time()
        return session

    def handle_initialize(self, request: MCPRequest) -> tuple[MCPResponse, str]:
        """Handle initialization request with session creation"""
        #TODO:
        # 1. Create and assign to new `session_id` session ID as `str(uuid.uuid4()).replace("-", "")`
        # 2. Create MCPSession with `session_id` and assign to `session`
        # 3. Handle protocol version and assign to `protocol_version` variable:
        #       `request.params.get("protocolVersion") if request.params else self.protocol_version`
        # 4. Create MCPResponse:
        #       - id=request.id
        #       - result={
        #                 "protocolVersion": protocol_version,
        #                 "capabilities": {
        #                     "tools": {},
        #                     "resources": {},
        #                     "prompts": {}
        #                 },
        #                 "serverInfo": self.server_info
        #             }
        # 5. Return created MCP response and `session_id`
        session_id = str(uuid.uuid4()).replace("-", "")
        session = MCPSession(session_id)
        self.sessions[session_id] = session

        protocol_version = request.params.get("protocolVersion") if request.params else self.protocol_version
        response = MCPResponse(
            id=request.id,
            result={
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": self.server_info
            }
        )

        return response, session_id

    def handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        #TODO:
        # 1. Create `tools_list` by iterating through `self.tools.values()` and calling `to_mcp_tool()` on each tool
        # 2. Create MCPResponse:
        #       - id=request.id
        #       - result={"tools": tools_list}
        # 3. Return created MCP response
        tools_list = [tool.to_mcp_tool() for tool in self.tools.values()]
        return MCPResponse(
            id=request.id,
            result={"tools": tools_list}
        )

    def handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request with proper MCP-compliant response format"""
        #TODO:
        # 1. Check if `request.params` exists, if not return MCPResponse with error:
        #       - id=request.id
        #       - error=ErrorResponse(code=-32602, message="Missing parameters")
        # 2. Extract `tool_name` from `request.params.get("name")` and `arguments` from `request.params.get("arguments", {})`
        # 3. Check if `tool_name` exists, if not return MCPResponse with error:
        #       - id=request.id
        #       - error=ErrorResponse(code=-32602, message="Missing required parameter: name")
        # 4. Check if `tool_name` exists in `self.tools`, if not return MCPResponse with error:
        #       - id=request.id
        #       - error=ErrorResponse(code=-32601, message=f"Tool '{tool_name}' not found")
        # 5. Get `tool` from `self.tools[tool_name]`
        # 6. Try to execute tool with arguments:
        #       - Call `tool.execute(arguments)` and assign result to `result_text`
        #       - Return MCPResponse with id=request.id and result={"content": [{"type": "text", "text": result_text}]}
        # 7. Handle exceptions by returning MCPResponse with:
        #       - id=request.id
        #       - result={"content": [{"type": "text", "text": f"Tool execution error: {str(tool_error)}"}], "isError": True}

        if not request.params:
            return MCPResponse(
                id=request.id,
                error=ErrorResponse(
                    code=-32602,
                    message="Missing parameters"
                )
            )

        # Extract tool name and arguments according to MCP spec
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})

        if not tool_name:
            return MCPResponse(
                id=request.id,
                error=ErrorResponse(
                    code=-32602,
                    message="Missing required parameter: name"
                )
            )

        if tool_name not in self.tools:
            return MCPResponse(
                id=request.id,
                error=ErrorResponse(
                    code=-32601,
                    message=f"Tool '{tool_name}' not found"
                )
            )

        tool = self.tools[tool_name]

        try:
            result_text = tool.execute(arguments)
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            )
        except Exception as tool_error:
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tool execution error: {str(tool_error)}"
                        }
                    ],
                    "isError": True
                }
            )
