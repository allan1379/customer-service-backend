from dataclasses import dataclass, field
from typing import Any

from cryptography.utils import Enum

from atguigu.task.flow.links import FlowStepLink


@dataclass(slots=True)
class ResponseDefinition:
    text: str  # 响应的内容  如果mode是static或者没有，直接将text内容渲染出去  如果mode是rephrase，text内容利用LLM根据prompt提示词改写之后的内容
    mode: str = "static"
    prompt: str | None = None


@dataclass(slots=True)
class SlotValidation:
    """"
    针对收集到的信息进行校验
    """
    condition: str
    failure_response: ResponseDefinition = field(default_factory=ResponseDefinition)


class FlowStepType(Enum):
    START = "start"
    END = "end"
    COLLECT = "collect"  # 业务流程需要补充槽位---填写槽位(collect的类型一定出现在业务流程中，因为只有业务流程才知道自己要什么信息)
    ACTION = "action"  # action_listen 1. 让执行引擎停下来 action_response 2. 告诉用户要填写什么信息 action_xxx 3. 找外部要数据  # 系统流程的step类型有action的，且action的名字有且只有两种情况：  action_response(作用：告诉用户一些信息【开场白、槽位填写什么】) action_listen(作用：把控制权从应用层面交给用户层面，让用户填写槽位) action_xxx永远不会出现在系统流程中（因为找外部要数据是业务方决定的）业务流程一定会有step类型是action的，且还会有名字action_xxx(业务找外部要数据)、以及action_response(填写的槽位以及外部数据给用户看) 但是一定没有action_listen(能让流程停下来，不继续推进的只有系统流程，且这个系统流程名字system_collect_information)


@dataclass(slots=True)
class FlowStep:
    """"
     步骤基类：提供四种步骤类型的通用字段 start,end,collect,action
    """
    id: str  # 步骤ID
    type: FlowStepType
    next: list[FlowStepLink] = field(default_factory=list)  # 相当于条件边的意思


@dataclass(slots=True)
class StartFlowStep(FlowStep):
    """"
    开始步骤
    """
    pass


@dataclass(slots=True)
class EndFlowStep(FlowStep):
    """"
    结束步骤
    """
    pass


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    """"
    动作步骤 步骤三种 action_listen  action_response action_xxx
    """
    action: str = ""  # 行动的名字(三种action的名字:action_listen  action_response action_xxx)  必填字段
    args: dict[str, Any] = field(default_factory=dict)  # 参数指的是给外部【第三方接口【数据、{order_id}】、前端【渲染内容】】提供的数据


@dataclass(slots=True)
class CollectFlowStep(FlowStep):
    """"
    信息收集步骤
    """
    slot_name: str = ""  # 收集的槽位名字
    response: ResponseDefinition = field(default_factory=ResponseDefinition)  # 回复的信息
    validate: SlotValidation = field(default_factory=SlotValidation)  # 槽位信息校验
