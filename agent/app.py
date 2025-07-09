import asyncio
import json
import os

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.mcp_client import MCPClient
from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role


async def main():
    mcp_client = MCPClient()

    await mcp_client.connect(mcp_server_url="http://localhost:8006/mcp")
    tools: list[dict] = await mcp_client.get_tools()
    for tool in tools:
        print(f"{json.dumps(tool, indent=2)}")

    dial_client = DialClient(
        api_key=os.getenv("DIAL_API_KEY"),
        endpoint="https://ai-proxy.lab.epam.com",
        tools=tools,
        mcp_client=mcp_client
    )

    messages: list[Message] = [
        Message(
            role=Role.SYSTEM,
            content="You are an advanced AI agent. Your goal is to assist user with his questions."
        )
    ]

    print("MCP-based Agent is ready! Type your query or 'exit' to exit.")
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == 'exit':
            break

        messages.append(
            Message(
                role=Role.USER,
                content=user_input
            )
        )

        ai_message: Message = await dial_client.get_completion(messages)
        messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())
