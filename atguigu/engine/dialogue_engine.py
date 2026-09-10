import time

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.clarify.responder import ClarifyResponser
from atguigu.domain.messages import ProcessResult, BotMessage, UserMessage, MessageType, FocusedObject
from atguigu.domain.state import DialogueState
import uuid

from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import TurnPlan, TurnPlanValidateResult, ClarifyReason
from atguigu.plan.validator import TurnPlanValidator
from atguigu.task.command.commands import Command, SetSlotsCommand
from atguigu.task.flow.flows import FlowsList
from atguigu.task.flow.steps import CollectFlowStep
from atguigu.task.handler import TaskHandler


class DialogueEngine:

    def __init__(self, planner: TurnPlanner,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowledgeHandler,
                 chitchat_handler: ChitChatHandler,
                 turn_plan_validator: TurnPlanValidator,
                 clarify_responder: ClarifyResponser
                 ):
        self.planner = planner
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler
        self.turn_plan_validator = turn_plan_validator
        self.clarify_responder = clarify_responder

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
            bot_msg: list[BotMessage] = await self._hand_text_msg(user_message, state, self.task_handler.flow_list,
                                                                  self.knowledge_handler.intents)
        else:  # 处理 卡片消息
            state.set_focused_object(user_message.object)
            bot_msg: list[BotMessage] = await  self._hand_obj_msg(user_message.object, state,
                                                                  self.task_handler.flow_list)

        # 保存到流程里面
        state.pending_turn.bot_messages = bot_msg
        # 提交机器人回答
        state.commit_pending_turn()

        return ProcessResult(sender_id="u1001", message_id=str(uuid.uuid4()),
                             messages=bot_msg)

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

    async def _hand_text_msg(self, user_message: UserMessage, state: DialogueState, flow_list: FlowsList,
                             intents: dict[str, KnowledgeIntent]) -> list[BotMessage]:

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

        # 1.调用进行意图识别
        turn_plan: TurnPlan = await self.planner.predict(user_message, state, flow_list, intents)
        # 2.利用校验器校验
        validate_result: TurnPlanValidateResult = self.turn_plan_validator.validate(turn_plan, state, flow_list,
                                                                                    intents)
        # 3. 判断校验结果
        if not validate_result.valid:
            # 做失败澄清逻辑
            return await self.clarify_responder.respond(validate_result.reason, state)

        # 4.对应轨道的处理器处理
        if turn_plan.task is not None:
            return await self.task_handler.hand(state, turn_plan.task.commands)
        elif turn_plan.knowledge is not None:
            return await self.knowledge_handler.hand(state, self.knowledge_handler.intents)
        else:
            return await self.chitchat_handler.hand(state)

    async def _hand_obj_msg(self,
                            obj_msg: FocusedObject,
                            state: DialogueState,
                            flow_list: FlowsList) -> list[BotMessage]:
        """
        能够将卡片的对象消息填入到槽位中去---->能够构建SetSlotsCommand
        1. 可以构建SetSlotsCommand(流程缺该槽位，正好点击卡片补充上)---继续推进流程的后续step步骤，（TaskHandler.hand(commands=[command]):1. 解析四种command 2.利用流程推挤器推进系统流程、业务流程）
        2. 不用构建SetSlotsCommand(流程不缺这个槽位，点击卡片)---继续推进流程的当前step步骤（TaskHandler.hand(command=[])）
        3. 不用构建SetSlotsCommand(没有流程，点击卡片) --- 让意图澄清器澄清到底点击这个对象，您想干嘛??
        :param obj_msg:
        :param state:
        :return:
        """

        # 1. 解析对象成为SetSlotsCommand
        command = self._resolve_object_command(
            obj_message=obj_msg,
            state=state,
            flows=flow_list,
        )

        # 2. 判断如果command存在
        if command:
            await self.task_handler.hand(state, commands=[command])

        # 3. command不存在，流程是否存在
        # 3.1 流程如果存在,继续处理流程的当前step
        if state.active_task is not None:
            return await self.task_handler.hand(state, commands=[])

        # 3.2 流程如果不存在，意图澄清
        return await self.clarify_responder.respond(reason=ClarifyReason.MISSING_FOCUSED_OBJECT, state=state)

    def _resolve_object_command(self,
                                obj_message: FocusedObject,
                                state: DialogueState,
                                flows: FlowsList) -> Command | None:
        """
        卡片类型是订单：SetSlotsCommand(slots={"order_number":obj_message.id})
        卡片类型是商品：SetSlotsCommand(slots={"product_number":obj_message.id})
        :param obj_message:
        :param state:
        :param flows:
        :return:
        """

        # 1. 判断消息的类型

        if obj_message.type == "order":

            if self._try_build_slots_command(state, flows, "order_number"):
                return SetSlotsCommand(command="start_flow", slots={"order_number": obj_message.id})

            return None

        if obj_message.type == "product":
            if self._try_build_slots_command(state, flows, "product_id"):
                SetSlotsCommand(command="start_flow", slots={"product_id": obj_message.id})
            return None

        return None

    def _try_build_slots_command(self,
                                 state: DialogueState,
                                 flows: FlowsList,
                                 slot_name: str) -> bool:

        # 1. 判断当前是否有业务流程
        activated_task = state.active_task
        if activated_task is None:
            return False

        # 2. 判断业务流程Flow(防御性代码:95)
        flow = flows.get_flow_by_id(activated_task.flow_id)
        if flow is None:
            return False

        # 3. 判断槽位是否已经填写过了。(幂等性校验)---防御性代码
        if activated_task.slots.get(slot_name):
            return False

        # 4. 判断你点击的卡片是不是当前step正在收集的槽位 （当前正在收集的槽位是refund_reason，点击了卡片）
        for step in flow.steps:
            if isinstance(step, CollectFlowStep) and step.slot_name == slot_name:
                return True

        return False
