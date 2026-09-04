from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import TurnPlanValidateResult, TurnPlan, ClarifyReason
from atguigu.task.command.commands import StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumeFlowCommand
from atguigu.task.flow.flows import FlowsList


class TurnPlanValidator:
    """"
    做意图识别之后的校验逻辑
    """
    pass

    def validate(self, turn_plan: TurnPlan, state: DialogueState, flow_list: FlowsList) -> TurnPlanValidateResult:
        """
        分为两大校验类型
        校验外层轨道数【一条轨道没命中、命中了多条轨道】
        校验内层的轨道约束【校验业务轨道、知识检索轨道】闲聊轨道不校验
        :param flow_list:
        :param turn_plan:
        :param state:
        :return:
        """
        # 1. 获取turn_plan中的轨道数
        tracks = turn_plan.activated_tracks()
        # 2. 校验轨道是否未命中
        if not tracks:
            return self.reject(reason=ClarifyReason.MISSING_TRACK)
        # 3. 校验轨道是否命中了多条
        if len(tracks) > 1:
            return self.reject(reason=ClarifyReason.MULTIPLE_TRACKS)
        # 4. 校验唯一的那一条轨道
        selected_track = tracks[0]
        # 4.1 校验任务轨道
        if selected_track == "task":
            return self._validate_task_track(turn_plan, flow_list)
        # 4.2 校验知识检索轨道
        if selected_track == "knowledge":
            return self._validate_knowledge_track(turn_plan, state)
        # 4.3 闲聊轨道(真实公司中不允许闲聊)
        return TurnPlanValidateResult(valid=True)  # 代表闲聊或者校验通过

    def reject(self, reason: ClarifyReason) -> TurnPlanValidateResult:
        return TurnPlanValidateResult(valid=False, reason=reason)

    def _validate_task_track(self, turn_plan: TurnPlan, flow_list: FlowsList) -> TurnPlanValidateResult:
        """
        四重校验(TODO 众多的校验--->扩展点)
        1. 校验commands(是否有对应的命令)是否存在
        2. 校验commands中各个command的类型(白名单机制)
        3. 校验是否存在多个StartedFlowCommand(开启多个业务流程)
        4. 校验业务流程是否存在(根据流程ID 找流程)
        :param turn_plan:
        :return:
        """
        task_track = turn_plan.task
        # 1. 校验一：校验commands是否存在
        if not task_track.commands:
            return self.reject(reason=ClarifyReason.MISSING_TASK_COMMANDS)
        # 2.校验二：检验command的类型
        allowed_command = (StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand)
        if not all(isinstance(command, allowed_command) for command in task_track.commands):
            return self.reject(reason=ClarifyReason.INVALID_TASK_COMMANDS)

        # 3. 校验三: 校验多个StartedFlowCommand
        started_flow_cmds = [command for command in task_track.commands if isinstance(command, StartFlowCommand)]
        if len(started_flow_cmds) > 1:
            return self.reject(reason=ClarifyReason.MULTIPLE_TASK_FLOWS)

        # 4. 4.1 有且只有一个StartedFlowCommand 4.2 一个都没有(单独给一个SetSlowsCommand/CancelFlowCommand/ResumedFlowCommand)
        if started_flow_cmds:
            started_flow = started_flow_cmds[0]
            flow = flow_list.get_flow_by_id(started_flow.flow)
            if flow is None:
                return self.reject(reason=ClarifyReason.UNKNOWN_TASK_FLOW)

        return TurnPlanValidateResult(valid=True)

    def _validate_knowledge_track(self, turn_plan: TurnPlan, state: DialogueState) -> TurnPlanValidateResult:
        pass
