from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.plan.planner import TurnPlanner


def build_dialogue_engine() -> DialogueEngine:
    return DialogueEngine(
        planner=TurnPlanner()
    )
