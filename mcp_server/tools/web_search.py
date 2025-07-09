from typing import Any

import requests

from mcp_server.tools.base import BaseTool


class WebSearchTool(BaseTool):

    @property
    def name(self) -> str:
        #TODO:
        # 1. Return `WEB_SEARCH` constant
        return "web_search"

    @property
    def description(self) -> str:
        #TODO:
        # 1. Return string description "Performs WEB search"
        return "Performs WEB search"

    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO:
        # 1. Return dictionary with schema structure:
        #       {
        #           "type": "object",
        #           "properties": {
        #               "request": {
        #                   "type": "string",
        #                   "description": "The search query or question to search for on the web"
        #               }
        #           },
        #           "required": ["request"]
        #       }
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
        #TODO:
        # 1. Assign `api_key` parameter to `self.api_key`
        # 2. Create `self.endpoint` by concatenating `endpoint` with "/openai/deployments/gemini-2.0-flash-exp-google-search/chat/completions"
        self.api_key = api_key
        self.endpoint = endpoint + "/openai/deployments/gemini-2.0-flash-exp-google-search/chat/completions"

    def execute(self, arguments: dict[str, Any]) -> str:
        #TODO:
        # 1. Create `headers` dictionary with:
        #       - "api-key": self.api_key
        #       - "Content-Type": "application/json"
        # 2. Create `request_data` dictionary with:
        #       - "messages": [{"role": "user", "content": str(arguments["request"])}]
        # 3. Make POST request using `requests.post()` with:
        #       - url=self.endpoint
        #       - headers=headers
        #       - json=request_data
        #       - Assign result to `response`
        # 4. Check if `response.status_code == 200`:
        #       - Get JSON data with `response.json()` and assign to `data`
        #       - If "error" key exists in `data`, return `data["error"]`
        #       - Otherwise return `data["choices"][0]["message"]["content"]`
        # 5. If status code is not 200, return formatted error string: f"Error: {response.status_code} {response.text}"
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
            ]
        }

        response = requests.post(url=self.endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                return data["error"]
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} {response.text}"