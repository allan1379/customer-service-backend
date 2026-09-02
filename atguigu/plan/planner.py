from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.infrastructure.llm_client import llm_client
from atguigu.plan.turn_plan import TurnPlan
from atguigu.prompts.loader import load_prompt_template


class TurnPlanner:
    """
    对话轮次规划器
    """

    async def predict(self, user_message: UserMessage, state: DialogueState) -> TurnPlan:
        # 1. 构建提示词模版要的内容（不需要构建提示词模版）

        prompt_inputs: dict[str, Any] = self._prepare_prompt_inputs(user_message, state=state)

        # 2. 调用大语言模型
        turn_plan = await self._predict_from_prompt_inputs(prompt_inputs)

        return turn_plan

    def _prepare_prompt_inputs(self, user_message, state):
        pass

    async def _predict_from_prompt_inputs(self, prompt_inputs: dict[str, Any]) -> TurnPlan:
        """"
        调用大模型
        """
        # 加载提示词模板
        task_prompt_template = load_prompt_template("turn_plan")
        # 解析
        prompt_template = PromptTemplate.from_template(template=task_prompt_template, template_format="jinja2")

        # 构建调用链
        chain = prompt_template | llm_client | JsonOutputParser()

        result = await chain.ainvoke(prompt_inputs)

        return TurnPlan.from_dict(result)
