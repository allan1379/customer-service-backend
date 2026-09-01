from atguigu.domain.messages import ProcessResult, BotMessage
from atguigu.domain.state import DialogueState


class DialogueEngine:

    def hand_message(self, dialogue_state: DialogueState) -> ProcessResult:
        """"
        引擎处理
        """
        import uuid
        return ProcessResult(sender_id="u1001",message_id=str(uuid.uuid4()),messages=[BotMessage(text="我是机器人AI")])
