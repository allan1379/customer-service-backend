""""
用户消息 机器消息模型
"""
from dataclasses import field
from typing import Any

from attr import dataclass
from cryptography.utils import Enum


@dataclass(slots=True)
class FocusedObject:
    id: str
    type: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)  # 如果为空给一个默认dick

    def to_dict(self) -> dict[str, Any]:
        """
        将实例对象转成字典结构
        :return:
        """
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'attributes': dict(self.attributes)  # 浅拷贝 数据做隔离(可变对象会受到影响) copy.deepcopy()深拷贝
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FocusedObject':
        return cls(
            id=data['id'],
            type=data['type'],
            title=data['title'],
            attributes=dict(data.get('attributes'))
        )


class MessageType(Enum):
    TEXT = "text",
    OBJECT = "object"


@dataclass(slots=True)  # 1. 访问速度快__slots__  __dict__() 2. 占用内存空间更小 3.对象的属性个数固定住
class UserMessage:
    """
    用户角色的消息
    """
    sender_id: str
    message_id: str
    type: MessageType  # 消息类型(文本以及对象类型)
    text: str | None = None  # 可选
    object: FocusedObject | None = None  # 可选

    def to_dict(self) -> dict[str, Any]:
        return {
            'sender_id': self.sender_id,
            'message_id': self.message_id,
            "type": self.type.value,
            'text': self.text,
            'object': self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMessage":
        return cls(
            sender_id=data['sender_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data.get('text'),
            object=FocusedObject.from_dict(data['object']) if data.get('object') else None
        )


@dataclass(slots=True)
class BotMessage:
    """"
    机器人信息
    """
    text: str | None = None  # 文本信息可选
    object: FocusedObject | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            'text': self.text,
            'object': self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BotMessage':
        return cls(
            text=data['text'],
            object=FocusedObject(data['object']) if data['object'] else None
        )

@dataclass(slots=True)
class ProcessResult:
    sender_id: str
    message_id: str
    messages: list[BotMessage]
