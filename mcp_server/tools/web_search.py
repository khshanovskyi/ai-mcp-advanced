from typing import Any

import requests

from mcp_server.tools.base import BaseTool


class WebSearchTool(BaseTool):

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Performs WEB search"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web"
                }
            },
            "required": ["request"]
        }

    def __init__(self, api_key: str, endpoint: str) -> None:
        self.api_key = api_key
        self.endpoint = endpoint + "/openai/deployments/gemini-2.5-pro/chat/completions"

    def execute(self, arguments: dict[str, Any]) -> str:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": str(arguments["request"])
                }
            ],
            "tools": [
                {
                    "type": "static_function",
                    "static_function": {
                        "name": "google_search",
                        "description": "Grounding with Google Search",
                        "configuration": {}
                    }
                }
            ],
            "temperature": 0
        }

        response = requests.post(url=self.endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                return data["error"]
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} {response.text}"