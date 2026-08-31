from pathlib import Path
from typing import Any

import yaml

from atguigu.task.flow.flows import FlowsList, Flow, FlowSlot
from atguigu.task.flow.steps import FlowStep, CollectFlowStep


class FlowLoader:

    def load_many_yml(self, paths: list[str | Path]) -> FlowsList:
        """"
        解析多个ymal
        """
        flows: list[Flow] = []
        slots: dict[str, FlowSlot] = {}
        for path in paths:
            loaded = self.load_yml(path)
            flows.extend(loaded.flows)
            slots.update(loaded.slots)
        return FlowsList(flows=flows, slots=slots)

    def load_yml(self, path: Path) -> FlowsList:
        """"
        解析单个yml文件成对象
        """
        # 1. 读取yaml文件加载为dict对象
        with open(path, 'r', encoding='utf-8') as f:
            dict_data = yaml.safe_load(f)
        # 2.解析slots
        slots: dict[str, FlowSlot] = self.load_slots(dict_data.get('slots', {}))
        # 3.解析flows
        flows: list[Flow] = self.load_flows(dict_data.get('flows', {}), slots)

        return FlowsList(flows=flows, slots=slots)

    def load_slots(self, slots: dict[str, Any]) -> dict[str, FlowSlot]:
        """"
        解析slots
        """
        loaded_slots: dict[str, FlowSlot] = {}
        for slot_name, slot_dict in slots.items():
            loaded_slots[slot_name] = FlowSlot(
                name=slot_name,
                type=slot_dict["type"],
                label=slot_dict["label"],
                description=slot_dict["description"]
            )
        return loaded_slots

    def load_flows(self, flows: dict[str, Any], slots: dict[str, FlowSlot]) -> list[Flow]:
        """"
        解析flows
        """
        loaded_flows: list[Flow] = []
        for flow_id, flow_dict in flows.items():
            # 解析steps
            steps: list[FlowStep] = [FlowStep.from_dict(step_dict) for step_dict in flow_dict.get("steps", {})]
            flow = Flow(
                flow_id=flow_id,
                flow_name=flow_dict["name"],
                description=flow_dict["description"],
                steps=steps,
                slots=self._load_flow_slot(steps, slots)
            )
            loaded_flows.append(flow)
        return loaded_flows

    def _load_flow_slot(self, steps: list[FlowStep], slots: dict[str, FlowSlot]) -> dict[str, FlowSlot]:
        """"
        查找步骤里面需要填槽的点
        """
        flow_slots: dict[str, FlowSlot] = {}
        for step in steps:
            if isinstance(step, CollectFlowStep):
                flow_slot_name = step.slot_name
                slot_definition = slots.get(flow_slot_name)
                if slot_definition is not None:
                    flow_slots[flow_slot_name] = slot_definition

        return flow_slots


if __name__ == '__main__':
    # yml_path = Path(__file__).resolve().parents[2] / "flow_config" / "user_flows.yml"
    yml_path = Path(__file__).resolve().parents[2] / "flow_config" / "system_flows.yml"

    # 1. 读取yaml文件加载为dict对象
    # with open(yml_path, 'r', encoding='utf-8') as f:
    #     dict_data = yaml.safe_load(f)
    #
    # print(dict_data)

    flows_list: FlowsList = FlowLoader().load_yml(yml_path)
    print(flows_list)
