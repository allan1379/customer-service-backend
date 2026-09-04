from atguigu.knowledge.intents import KnowledgeIntent


class KnowledgeHandler:

    def __init__(self, intents: dict[str, KnowledgeIntent]):
        self.intents = intents

    async def hand(self, state, intents):
        pass
