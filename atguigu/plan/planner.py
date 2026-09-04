import json
from dataclasses import asdict
from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.history.builder import ChatHistoryBuilder
from atguigu.infrastructure.llm_client import llm_client
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan
from atguigu.prompts.loader import load_prompt_template
from atguigu.task.flow.flows import FlowsList


class TurnPlanner:
    """
    对话轮次规划器
    """

    async def predict(self, user_message: UserMessage, state: DialogueState, flow_list: FlowsList, intents: dict[str, KnowledgeIntent]) -> TurnPlan:
        # 1. 构建提示词模版要的内容（不需要构建提示词模版）
        prompt_inputs: dict[str, Any] = self._prepare_prompt_inputs(user_message, state, flow_list,intents)

        # 2. 调用大语言模型
        turn_plan = await self._predict_from_prompt_inputs(prompt_inputs)

        return turn_plan

    def _prepare_prompt_inputs(self, user_message: UserMessage, state: DialogueState, flow_list: FlowsList
                               , intents: dict[str, KnowledgeIntent]) -> dict[
        str, Any]:
        """"
        构建提示词填充字段
        """
        # 当前用户对话信息
        user_message = user_message.text
        # 历史10轮对话
        current_conversation = ChatHistoryBuilder.build(state.current_session().turns[-10:])
        # 卡片信息
        focused_object_json = json.dumps(state.focused_object.to_dict(),
                                         ensure_ascii=False) if state.focused_object else "null"
        # 中断的任务流程
        interrupted_tasks_json = json.dumps(
            [interrupted_active_task.to_dict() for interrupted_active_task in state.interrupted_active_tasks],
            ensure_ascii=False) if state.interrupted_active_tasks else "null"
        # 当前正在进行的任务
        active_task_json = json.dumps(state.active_task.to_dict(), ensure_ascii=False) if state.active_task else "null"
        # 当前有的业务流程轨道信息
        # 业务流程(只用提供业务流程给LLM :需要业务流程信息 不需要系统流程信息，且业务流程也不需要steps)
        available_flows_json = json.dumps({
            "flows": [
                {
                    k: v for k, v in asdict(flow).items() if k != "steps"
                } for flow in flow_list.flows if not flow.flow_id.startswith("system_")
            ]
        }, ensure_ascii=False)

        # 知识意图
        knowledge_intents_json = json.dumps(
            [{"id": intent.id, "description": intent.description} for intent in intents.values()],
            ensure_ascii=False
        )

        return {
            "user_message": user_message,
            "current_conversation": current_conversation,

            "focused_object_json": focused_object_json,

            "interrupted_tasks_json": interrupted_tasks_json,
            "active_task_json": active_task_json,

            "available_flows_json": available_flows_json,
            "knowledge_intents_json": knowledge_intents_json

        }

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
