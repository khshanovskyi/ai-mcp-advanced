from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        #TODO: Provide tool name as `search_users`
        raise NotImplementedError()

    @property
    def description(self) -> str:
        #TODO: Provide description of this tool
        raise NotImplementedError()

    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO:
        # Provide tool params Schema:
        # - name: str
        # - surname: str
        # - email: str
        # - gender: str
        # None of them are required (see UserClient.search_users method)
        raise NotImplementedError()

    async def execute(self, arguments: dict[str, Any]) -> str:
        #TODO:
        # Call user_client search_users (with `**arguments`) and return its results (it is async, don't forget to await)
        raise NotImplementedError()