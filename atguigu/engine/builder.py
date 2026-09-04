from pathlib import Path

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.clarify.responder import ClarifyResponser
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnPlanValidator
from atguigu.task.flow.flows import FlowsList
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.task.loader import FlowLoader


def build_dialogue_engine() -> DialogueEngine:
    user_path = Path(__file__).resolve().parents[2] / "flow_config" / "user_flows.yml"
    system_path = Path(__file__).resolve().parents[2] / "flow_config" / "system_flows.yml"
    flow_list: FlowsList = FlowLoader().load_many_yml([user_path, system_path])

    return DialogueEngine(
        planner=TurnPlanner(),
        task_handler=TaskHandler(flow_list=flow_list),
        knowledge_handler=KnowledgeHandler(intents=KNOWLEDGE_INTENTS),
        chitchat_handler=ChitChatHandler(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponser()
    )
