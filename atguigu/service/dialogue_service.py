from atguigu.domain.messages import UserMessage, ProcessResult
from atguigu.domain.state import DialogueState
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository


class DialogueService:
    def __init__(self, dialogue_repository: DialogueRepository,dialogue_engine:DialogueEngine):
        self.dialogue_repository = dialogue_repository
        self.dialogue_engine = dialogue_engine

    async def hand_dialogue(self, user_message: UserMessage) -> ProcessResult:
        """"
        【读写数据库：repository】/计算[engine]
        """
        # 1读取数据
        dialogue_state: DialogueState = await  self.dialogue_repository.load_dialogue(user_message.sender_id)

        # 2. 引擎层使用(修改DialogueState的状态)
        process_result: ProcessResult = await self.dialogue_engine.hand_message(user_message,dialogue_state)

        # 3.保存信息
        await self.dialogue_repository.save_dialogue(dialogue_state)
        return process_result
