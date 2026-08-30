from dataclasses import dataclass


@dataclass(slots=True)
class FlowStepLink:
    """"
    边的基类: 提供下一个step_id
    """
    target: str  # 指向下一个步骤ID


@dataclass(slots=True)
class FlowStepStaticLink(FlowStepLink):
    """"
    类似于  next: acknowledge  直接指向，什么都不做
    """
    pass


@dataclass(slots=True)
class FlowStepConditionLink(FlowStepLink):
    """"
    需要做条件判断的边
    next:
     - if: "context.get('reason') == 'clarification_rejected'"
     then: clarification_rejected
    """
    condition: str


@dataclass(slots=True)
class FlowFallBackLink(FlowStepLink):
    """"
    做条件边的失败兜底
     - else: ask_rephrase
    """
    pass
