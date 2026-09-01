from dataclasses import field
from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    sender_id: str
    text: str | None = None
    object: ChatObject | None = None


class ChatObject(BaseModel):
    """"
    前端传的卡片
    """
    id: str
    type: str
    title: str | None = None
    attributes: dict[str, Any] = {}


class ChatResponse(BaseModel):
    """"
    请求返回值
    """
    sender_id: str
    message_id: str
    messages: list[ChatBotMessage]


class ChatBotMessage(BaseModel):
    """"
    机器人的回答信息
    """
    text: str | None = None  # 文本信息可选
    object: ChatObject | None = None