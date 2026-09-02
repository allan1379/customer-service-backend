from typing import Any

from attr import dataclass


@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, command_dict: dict[str, Any]) -> "Command":
        command_type = command_dict['command']
        clz = COMMAND_TO_CLASS[command_type]
        return clz(**command_dict)


@dataclass
class StartFlowCommand(Command):
    flow: str  # 开启的业务流程ID


@dataclass
class ResumeFlowCommand(Command):
    flow: str | None = None


@dataclass
class CancelFlowCommand(Command):
    pass


@dataclass
class SetSlotsCommand(Command):
    slots: dict[str, Any]


COMMAND_TO_CLASS: dict[str, type[Command]] = {
    "start_flow": StartFlowCommand,
    "resume_flow": ResumeFlowCommand,
    "cancel_flow": CancelFlowCommand,
    "set_slots": SetSlotsCommand
}
