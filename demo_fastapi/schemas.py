from typing import Any, Literal

from pydantic import BaseModel, Field


# 客户端需要传入参数
class ToolRequest(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any]

#服务器预览接口返回参数
class ToolPreviewResponse(BaseModel):
    status: Literal["received"]
    name: str
    arguments: dict[str, Any]


class PostCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    user_id: int = Field(ge=1)
    published: bool = False

class PostUpdate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    published: bool = False

class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    email: str = Field(min_length=1)
