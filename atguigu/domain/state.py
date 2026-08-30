"""
整个对话的完整信息（聚合根） DDD(领域数据模型)
存储某个一个用户的对话完整信息

三个部分：
1.流程相关
2.卡片相关
3.会话相关：Session:会话  开启一次会话创建一个Session对象（会话的额外信息：会话时间、关闭时间... 核心信息：用户对话内容（Q->A）Turn:属性：turns:List[Turn] Turn:user_message bot_message列表）

"""
import time
import uuid
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

    # ==========================流程相关==========================
    def start_active_system_task(self, system_context: SystemContext):
        """
        开启并激活系统流程(任务)
        :return:
        """
        self.active_system_task = system_context

    def end_activating_system_task(self):
        """
        结束正在激活的系统流程(任务)
        :return:
        """
        self.active_system_task = None

    def start_active_business_task(self, task_context: TaskContext):
        """
        开启并激活业务流程(任务)
        :param task_context:
        :return:
        """
        self.active_task = task_context

    def end_active_business_task(self):
        """
        结束正在激活的业务流程(任务))
        :return:
        """
        self.active_task = None

    def end_activating_task(self):
        """
        结束正在运行的流程（清空业务流程和系统流程）
        :return:
        """
        self.active_system_task = None
        self.active_task = None

    def interrupted_activating_task(self):
        """"
        中断正在运行的业务流程
        """
        # 1. 将正在运行的业务流程存储到栈中
        self.interrupt_tasks.append(self.active_task)
        self.active_task = None

    def resumed_interrupted_business_task(self, flow_id: str | None = None) -> bool:
        """"
        恢复中断的业务流程
        """
        # 1. 检验栈中是否有元素
        if not self.interrupt_tasks:
            return False
        # 2.判断 flow_id是否有值
        if flow_id:
            for i, interrupt_task in enumerate(self.interrupt_tasks):
                if interrupt_task.flow_id == flow_id:
                    self.active_task = interrupt_task
                    del self.interrupt_tasks[i]
                    return True
        else:
            interrupt_task = self.interrupt_tasks.pop()
            self.active_task = interrupt_task
            return True

        return False

    def current_activating_task(self):
        """"
        当前正在运行的流程(业务流程、系统流程？)
        业务流程有 系统流程没有：获取业务流程
        系统流程有 业务流程没有：获取系统流程
        系统流程有 业务流程也有： 优先获取系统流程：
        """
        return self.active_system_task or self.active_task

    # ==========================槽位相关==========================
    def set_sorts(self, sorts: dict[str, Any]):
        """"
        设置槽位
        """
        if self.active_task:
            self.active_task.slots.update(sorts)

    def get_sorts(self, sort_name: str) -> Any:
        """"
        根据槽位名读取槽位的值
        """
        if self.active_task:
            return self.active_task.slots.get(sort_name)
        else:
            return None

    # ==========================卡片相关==========================
    def set_focused_object(self, focused_object: FocusedObject):
        """"
        添加聚焦卡片
        """
        self.focused_object = focused_object

    # ==========================session(会话)相关=================
    def current_session(self) -> Session | None:
        """"
        返回当前会话
        """
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session

        return None

    def start_session(self):
        """"
        创建一个新会话
        """
        import time
        now = time.time()
        session = Session(session_id=str(uuid.uuid4()), started_at=now, last_activity_at=now)
        self.current_session_id = session.session_id
        self.sessions.append(session)

    def close_session(self):
        """"
        关闭session对象
        """
        if self.current_session():
            # 1. 修改session的关闭时间
            self.current_session().closed_at = time.time()
            self.current_session_id = None

    def reset_running_state_for_new_session(self):
        """"
        session超时(session超时时间是60min)
        """
        # 1.清除任务相关
        self.active_task = None
        self.interrupt_tasks = list()
        self.active_system_task = None
        # 2.清除卡片
        self.focused_object = None
        # 3.清空缓存区
        self.pending_turn = None

    # ==========================Turn(轮次)相关====================
    def start_turn(self, user_message: UserMessage):
        """"
        开启一个轮次
        """
        if self.current_session():
            turn = Turn(turn_id=str(uuid.uuid4()), user_message=user_message, bot_messages=list())
            self.pending_turn = turn

    def commit_pending_turn(self):
        """"
        提交turn缓冲区
        """
        if self.current_session():
            self.current_session().turns.append(self.pending_turn)
            self.pending_turn = None
