from atguigu.domain.contexts import CanceledSystemContext
from atguigu.domain.state import DialogueState
from atguigu.task.command.commands import Command, StartFlowCommand, SetSlotsCommand, CancelFlowCommand, \
    ResumeFlowCommand
from atguigu.task.flow.flows import FlowsList


class CommandProcessor:
    """
        命令处理器
        作用：处理四种命令：
        StartFlowCommand: 我想查询订单状态---LLM根据自然语言【任务】以及提示词上下文----{"command":"start_flow": flow:"flow_id"}----【结构化的数据模型StartFlowCommand】
        ---->开启业务流程(应用) 开启业务流程（state.active_task） 开启一个开始的系统流程 state.active_system_task
        ResumedFlowCommand: 我想继续开始订单状态查询 -----  {"command": "resume_flow"}  {"command": "resume_flow", "flow": "flow_id"}
        CancelFlowCommand: 我不想开始订单状态查询-----{"command":"cancel_flow"}
        SetSlotsCommand: 我的订单号是A10001-----{"command":"set_slots","slots":{"slot_name":""}}


    """

    def run(self, state: DialogueState, flow_list: FlowsList, commands: list[Command]):
        for command in commands:
            # 判断具体的command类型是哪一种
            if isinstance(command, StartFlowCommand):  # 开启一个流程
                self._process_start_flow(command, state, flow_list)
            elif isinstance(command, SetSlotsCommand):  # 填槽任务
                self._process_set_slots(command, state)
            elif isinstance(command, CancelFlowCommand):  # 关闭任务
                self._process_cancel_flow(state, flow_list)
            elif isinstance(command, ResumeFlowCommand):  # 恢复一个任务
                self._process_resume_flow(command, state, flow_list)
            else:
                pass

        pass

    def _process_set_slots(self, command: SetSlotsCommand, state: DialogueState):
        """
                职责： 将command的slots获取出来，设置到当期业务流程上下文的slots属性
                :param command:
                :param state:
                :return:
        """
        state.set_slots(command.slots)

    def _process_cancel_flow(self, state: DialogueState, flow_list: FlowsList):
        """
        职责：
        1. 激活取消系统流程的开场白
        2. 清空所有流程(业务流程以及系统流程)
        :param state:
        :param flow_list:
        :return:
        """
        # 1. 获取取消系统流程对象以及开始步骤的步骤ID
        canceled_flow = flow_list.get_flow_by_id("system_task_canceled")
        start_step_id = canceled_flow.get_start_step().id
        # 2. 获取当前正在执行的业务流程(流程ID以及流程名字)
        canceled_flow_id = state.active_task.flow_id
        canceled_flow_name = flow_list.get_flow_by_id(state.active_task.flow_id).flow_name
        # 3. 激活取消系统流程
        state.start_active_system_task(CanceledSystemContext(
            system_flow_id="system_task_canceled",
            system_step_id=start_step_id,
            canceled_flow_id=canceled_flow_id,
            canceled_flow_name=canceled_flow_name
        ))
        # 4. 清空所有流程(业务流程、系统流程都清空)
        state.end_activating_task()
