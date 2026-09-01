from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.infrastructure import db
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.service.dialogue_service import DialogueService


async def get_session():
    async with db.session_factory() as session:
        yield session  # FASTAPI 处理完请求（业务用完了）自动进入到该位置


RepositorySessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_engine():
    return DialogueEngine()


DialogueEngineDep = Annotated[DialogueEngine, Depends(get_engine)]


def get_repository(session: RepositorySessionDep):
    return DialogueRepository(session=session)


DialogueRepositoryDep = Annotated[DialogueRepository, Depends(get_repository)]


def get_dialogue_service(dialogue_repository: DialogueRepositoryDep, dialogue_engine: DialogueEngineDep):
    return DialogueService(dialogue_repository=dialogue_repository, dialogue_engine=dialogue_engine)


# Annotated:将类型以及类型的元素  依赖注入
DialogueServiceDep = Annotated[DialogueService, Depends(get_dialogue_service)]
