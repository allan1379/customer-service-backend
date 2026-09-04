from atguigu.task.flow.flows import FlowsList


class TaskHandler:
    def __init__(self, flow_list: FlowsList):
        self.flow_list = flow_list

    async def hand(self, state, commands):
        pass
