import time

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.domain.messages import ProcessResult, BotMessage, UserMessage, MessageType
from atguigu.domain.state import DialogueState
import uuid

from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import TurnPlan
from atguigu.task.flow.flows import FlowsList
from atguigu.task.handler import TaskHandler


class DialogueEngine:

    def __init__(self, planner: TurnPlanner,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowledgeHandler,
                 chitchat_handler: ChitChatHandler
                 ):
        self.planner = planner
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler

    async def hand_message(self, user_message: UserMessage, state: DialogueState) -> ProcessResult:
        """"
        引擎处理
        """
        # 1.准备session
        self._prepare_session(state)
        # 2.创建turn
        self._begin_turn(user_message, state)
        # 3. 判断消息类型
        if user_message.type is MessageType.TEXT:  # 处理文本消息
            await self._hand_text_msg(user_message, state,self.task_handler.flow_list)
        else:  # 处理 卡片消息
            self._hand_obj_msg(user_message, state)

        return ProcessResult(sender_id="u1001", message_id=str(uuid.uuid4()),
                             messages=[BotMessage(text="我是机器人AI")])

    def _prepare_session(self, state: DialogueState):
        """"
         确保session要有
        """
        # 判断当前是否有session
        current_session = state.current_session()
        if current_session is None:
            # 创建一个session
            state.start_session()
            return
        # session存在需要判断是否过期
        now = time.time()
        # 会话过期时间设定60分钟
        if now - current_session.last_activity_at > 60 * 60:
            # 关闭session
            state.close_session()
            state.current_session_id = None
            # 清空已经过期session的其他状态
            state.reset_running_state_for_new_session()
            state.start_session()
            return
        else:
            # 修改最后一次激活时间
            current_session.last_activity_at = now
        return

    def _begin_turn(self, user_message: UserMessage, state: DialogueState):
        """"
        创建一个轮次对话
        """
        state.start_turn(user_message)

    async def _hand_text_msg(self, user_message: UserMessage, state: DialogueState, flow_list: FlowsList) -> list[BotMessage]:

        """
        1. 调用大语言模型，目的：TurnPlanner根据任务路由对应的轨道(轨道一:业务任务轨道 轨道二:知识查询任务轨道 轨道三:闲聊任务轨道)
        2. TurnPlanValidator校验器校验大语言模型结果的'封装对象'
        # 2.1 校验失败---ClarifyResponder意图澄清器做意图澄清--内部自己产生了消息
        # 2.2 校验成功---根据对应的任务轨道，处理该轨道的逻辑(各自轨道的处理器：TaskHandler/KnowledgeHandler/ChitChatHandler)---内部产生机器人消息
        # 3. 提交turn
        # 4. 内部机器人的消息返回
        :param user_message:
        :param state:
        :return:
        调用LLM（1.给LLM什么数据 2.获取什么的数据）prompt的提示词---->程序自己根据业务定义的
        """

        # 调用进行意图识别
        turn_plan: TurnPlan = await self.planner.predict(user_message, state,flow_list)
        pass

    def _hand_obj_msg(self, user_message, state):
        pass
