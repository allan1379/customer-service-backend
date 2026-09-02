from dataclasses import field
from typing import Any

from attr import dataclass

from atguigu.task.command.commands import Command


@dataclass
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskTurnPlan":
        return cls(commands=[Command.from_dict(command_dict) for command_dict in data.get('commands', [])])


@dataclass
class KnowledgeTurnPlan:
    intents: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeTurnPlan":
        return cls(intents=data.get('intents', []))


@dataclass
class ChitChatTurnPlan:
    pass


@dataclass()
class TurnPlan:
    task: TaskTurnPlan | None = None
    knowledge: KnowledgeTurnPlan | None = None
    chitchat: ChitChatTurnPlan | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(data['task']) if data.get('task') else None,
            knowledge=KnowledgeTurnPlan.from_dict(data['knowledge']) if data.get('knowledge') else None,
            chitchat=ChitChatTurnPlan() if data.get('chitchat') else None
        )
