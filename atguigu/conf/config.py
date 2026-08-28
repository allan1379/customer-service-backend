""""
读取.env配置
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parents[2] / ".env"


class Settings(BaseSettings):
    """"
    LLM_MODEL=qwen-plus
    LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
    LLM_API_KEY=sk-ws-H.EIMRRXD.k3TM.MEUCIQCnket_fN0eWl_eCGD7lrNtzcNc6ssti_PjsudGzZTImgIgKVvwmIB0Bnn4P_eaXp_ESa-BuI9UocAzfuYM67GSlqw

    COMMERCE_API_BASE_URL=http://localhost:18081

    DATABASE_URL=mysql+aiomysql://root:root@localhost:3306/customer_service?charset=utf8mb4

    APP_HOST=0.0.0.0
    APP_PORT=18082
    """
    # LLM 配置信息
    llm_model: str
    llm_base_url: str
    llm_api_key: str
    # 商城API地址
    commerce_api_base_url: str
    # 数据库配置信息
    database_url: str
    # 服务器
    app_host: str
    app_port: int

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding='utf-8', extra='ignore')  # extra="ignore"


# 实例化
settings = Settings()

if __name__ == '__main__':
    print(settings.llm_base_url)
