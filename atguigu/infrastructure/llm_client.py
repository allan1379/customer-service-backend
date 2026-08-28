""""
llm
"""
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import _ConfigurableModel
from langchain_core.language_models import BaseChatModel

from atguigu.conf.config import settings

llm_client:BaseChatModel | _ConfigurableModel = init_chat_model(
    model=settings.llm_model,
    model_provider="openai",
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    temperature=0,
    timeout=120
)

if __name__ == '__main__':
    response = llm_client.invoke("给我讲一个笑话")
    print(response.content)
