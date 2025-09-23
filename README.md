# Advanced MCP (Server & Client) Practice Task

Python implementation for building AI Agent with MCP (Model Context Protocol) tools and MCP server/client architecture.

## 🎯 Task Overview

Create and run an MCP server with custom tools, then implement an AI Agent with MCP Client that utilizes tools from the created server. This task demonstrates the full MCP workflow from server implementation to client integration.

## 🎓 Learning Goals

By completing this project, you will learn:

- **MCP Protocol Implementation**: Understand the Model Context Protocol specification and JSON-RPC communication
- **Server-Side Tool Development**: Create custom tools that follow MCP standards
- **Client Integration**: Connect AI agents to MCP servers and handle tool execution
- **Session Management**: Implement proper session handling and state management
- **Streaming Responses**: Work with Server-Sent Events (SSE) for real-time communication
- **Error Handling**: Implement robust error handling in distributed systems

## 🏗️ Architecture

```
├── agent/                        # MCP Client Implementation
│   ├── clients/
│   │   ├── custom_mcp_client.py    🚧 TODO: Pure Python MCP client
│   │   ├── mcp_client.py           ✅ Complete: Framework-based client
│   │   └── dial_client.py          ✅ Complete: AI model integration
│   ├── models/           
│   │   └── message.py              ✅ Complete: Message structures
│   └── app.py                      🚧 TODO: Test it with MCPClient and CustomMCPClient
└── mcp_server/                   # MCP Server Implementation
    ├── models/
    │   ├── request.py              ✅ Complete: Request model
    │   └── response.py             ✅ Complete: Response model
    ├── services/
    │   └── mcp_server.py           🚧 TODO: Implement core server logic
    ├── tools/
    │   ├── base.py                 ✅ Complete: Abstract tool interface
    │   ├── calculator.py           ✅ Complete: Math operations tool
    │   └── web_search.py           🚧 TODO: Implement web search tool
    └── server.py                   🚧 TODO: Implement FastAPI server
```

## 📋 Requirements

- **Python**: 3.11 or higher
- **Dependencies**: Listed in `requirements.txt`
- **API Access**: DIAL API key with appropriate permissions
- **Network**: EPAM VPN connection for internal API access
- **Optional**: Postman for API testing

## 🔧 Setup Instructions

1. Create virtual environment
    ```bash
    python -m venv .venv
    ```
2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Environment Variables
> DIAL_API_KEY=your_dial_api_key

**Getting DIAL API Key:**
1. Connect to EPAM VPN
2. Visit: https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c
3. Follow the instructions to obtain your API key
---

# 🚀 Task:
### If the task in the main branch is hard for you, then switch to the `with-detailed-description` branch

## Create MCP Server:
1. Open [mcp_server](mcp_server) and review mcp server structure:
   - in [models](mcp_server/models) persist implemented request and response models, details about request and response [official documentation](https://modelcontextprotocol.io/specification/2025-06-18/basic)
   - in [services/mcp_server.py](mcp_server/services/mcp_server.py) you need to implement parts described in `TODO` sections
   - in [tools](mcp_server/tools) you will find simple tools. Please take a look at [BaseTool](mcp_server/tools/base.py), especially at `to_mcp_tool` method that collects tool JSON Schema
   - in [tools/web_search.py](mcp_server/tools/web_search.py) provide implementations described in `TODO` sections
   - lastly, in [server.py](mcp_server/server.py) provide implementations described in `TODO` sections
2. Run MCP server locally
3. Test it with Postman. Import [mcp.postman_collection.json](mcp.postman_collection.json) into postman. (`init` -> `init-notification` -> `tools/list` -> `tools/call`)
4. Open [agent/app.py](agent/app.py) and run it locally with MCPClient (it is implemented)
5. Test agent with queries below 👇
6. Provide implementations described in `TODO` sections for [custom_mcp_client.py](agent/clients/custom_mcp_client.py)
7. Test again agent with queries below 👇
```text
Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him
```

---
## 🔍 MCP Protocol Details

### JSON-RPC Structure

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "method_name",
  "params": {
    "parameter": "value"
  }
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": "matching-request-id",
  "result": {
    "data": "response_data"
  }
}
```

### MCP Session Flow

1. **Initialize**: Client sends `initialize` request
2. **Notification**: Client sends `notifications/initialized`
3. **Discovery**: Client calls `tools/list` to get available tools
4. **Operation**: Client calls `tools/call` with specific tool and arguments
5. **Shutdown**: `DELETE, {host}, Mcp-Session-Id: {Mcp-Session-Id}`, shutdown is not covered in this practice, but it's simple REST request

### Headers

- `Content-Type`: `application/json`
- `Accept`: `application/json, text/event-stream`
- `Mcp-Session-Id`: Session identifier (after initialization)

## 🎯 Implementation Tips

### Custom MCP Client Implementation

1. **Error Handling**: Always check for HTTP session initialization
2. **Session Management**: Store and reuse session IDs properly
3. **SSE Parsing**: Look for `data:` prefixed lines, ignore `[DONE]`
4. **JSON-RPC Errors**: Check for `error` field in responses
5. **Content Extraction**: Tool results are in `result.content[0].text`

### Common Issues

- **Missing Accept Header**: Server requires both JSON and SSE accept types
- **Session ID Missing**: Most operations require a valid session ID
- **Tool Arguments**: Arguments must be properly formatted as per tool schema
- **Async Context**: Use proper async/await patterns for HTTP requests


## 📚 Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---
# <img src="dialx-banner.png">