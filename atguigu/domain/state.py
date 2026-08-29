"""
整个对话的完整信息（聚合根） DDD(领域数据模型)
存储某个一个用户的对话完整信息

三个部分：
1.流程相关
2.卡片相关
3.会话相关：Session:会话  开启一次会话创建一个Session对象（会话的额外信息：会话时间、关闭时间... 核心信息：用户对话内容（Q->A）Turn:属性：turns:List[Turn] Turn:user_message bot_message列表）

"""
from dataclasses import field
from typing import Any

from attr import dataclass

from atguigu.domain.contexts import TaskContext, SystemContext
from atguigu.domain.messages import UserMessage, BotMessage, FocusedObject


@dataclass(slots=True)
class Turn:
    """"
    轮次
    """
    turn_id: str  # 轮次ID
    user_message: UserMessage
    bot_messages: list[BotMessage]

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict() if self.user_message else None,
            "bot_messages": [bot_message.to_dict() for bot_message in self.bot_messages]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data["turn_id"],
            user_message=UserMessage.from_dict(data["user_message"]),
            bot_messages=[BotMessage().from_dict(bot_message_dict) for bot_message_dict in data.get('bot_messages', [])]
        )


@dataclass(slots=True)
class Session:
    """"
    会话：存活时间（1.会话超时[60分钟],重新创建session 2.扩展：手动触发session失效，重新创建新的session ）
    """
    session_id: str
    started_at: float  # 会话开启时间
    last_activity_at: float  # session最后一次激活时间（超时判定）
    closed_at: float | None = None  # 会话关闭时间
    turns: list[Turn] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activity_at": self.last_activity_at,
            "closed_at": self.closed_at,
            "turns": [turn.to_dict() for turn in self.turns]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            last_activity_at=data["last_activity_at"],
            closed_at=data["closed_at"],
            turns=[Turn.from_dict(turn_dict) for turn_dict in data.get("turns", [])]
        )


@dataclass(slots=True)
class DialogueState:
    """"
    1.流程相关
    2.卡片相关
    3.会话相关
    """
    sender_id: str  # 用户ID

    active_task: TaskContext | None = None  # 当前业务流程
    interrupt_tasks: list[TaskContext] = field(default_factory=list)  # 当前中断的业务流程
    active_system_task: SystemContext | None = None  # 当前系统流程

    focused_object: FocusedObject | None = None  # 卡片对象

    current_session_id: str | None = None
    sessions: list[Session] = field(default_factory=list)  # 会话
    pending_turn: Turn | None = None  # 中间缓存turn

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "interrupt_tasks": [interrupt_task.to_dict() for interrupt_task in self.interrupt_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "focused_object": self.focused_object.to_dict() if self.focused_object else None,
            "current_session_id": self.current_session_id,
            "sessions": [session_dict.to_dict() for session_dict in self.sessions],
            "pending_turn": self.pending_turn.to_dict() if self.pending_turn else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DialogueState":
        return cls(
            sender_id=data["sender_id"],
            active_task=TaskContext.from_dict(data['active_task']) if data.get('active_task') else None,
            interrupt_tasks=[TaskContext.from_dict(interrupt_task_dict) for interrupt_task_dict in
                             data.get("interrupt_tasks", [])],
            active_system_task=SystemContext.from_dict(data['active_system_task']) if data.get(
                'active_system_task') else None,
            focused_object=FocusedObject.from_dict(data['focused_object']) if data.get('focused_object') else None,
            current_session_id=data['current_session_id'] if data.get('current_session_id') else None,
            sessions=[Session.from_dict(session_dict) for session_dict in data.get("sessions", [])],
            pending_turn=Turn.from_dict(data['pending_turn']) if data.get('pending_turn') else None
        )
