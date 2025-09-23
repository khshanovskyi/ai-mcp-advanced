from typing import Any

from mcp_server.models.user_info import UserUpdate
from mcp_server.tools.users.base import BaseUserServiceTool


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        #TODO: Provide tool name as `update_user`
        raise NotImplementedError()

    @property
    def description(self) -> str:
        #TODO: Provide description of this tool
        raise NotImplementedError()

    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO:
        # Provide tool params Schema:
        # - id: number, required, User ID that should be updated.
        # - new_info: UserUpdate.model_json_schema()
        raise NotImplementedError()

    def execute(self, arguments: dict[str, Any]) -> str:
        #TODO:
        # 1. Get user `id` from `arguments`
        # 2. Get `new_info` from `arguments` and create `UserUpdate` via pydentic `UserUpdate.model_validate`
        # 3. Call user_client update_user and return its results (it is async, don't forget to await)
        raise NotImplementedError()

