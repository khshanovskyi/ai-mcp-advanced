from enum import StrEnum
from typing import Any
from pydantic import BaseModel


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    AI = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {"role": str(self.role.value)}
        if self.content:
            result["content"] = self.content
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result
