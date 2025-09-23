from abc import ABC

from mcp_server.tools.base import BaseTool
from mcp_server.tools.users.user_client import UserClient


class BaseUserServiceTool(BaseTool, ABC):

    def __init__(self, user_client: UserClient):
        super().__init__()
        self._user_client = user_client
