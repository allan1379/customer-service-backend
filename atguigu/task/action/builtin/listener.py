from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionListener(Action):

    name = "action_listen"

    async def run(self,
            state: DialogueState,
            action_args: dict[str, Any]) -> ActionResult:

        return ActionResult(messages=[BotMessage(text="状态不错")])

