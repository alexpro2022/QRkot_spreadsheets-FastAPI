from http import HTTPStatus
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import Base
from app.models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    OBJECT_ALREADY_EXISTS = 'Object with such a unique values already exists'

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def has_permission(self, obj: ModelType, user: User) -> None:
        raise NotImplementedError('has_permission()` must be implemented.')

    def is_update_allowed(self, obj: ModelType, payload: Dict) -> None:
        raise NotImplementedError('is_update_allowed()` must be implemented.')

    def is_delete_allowed(self, obj: ModelType) -> None:
        raise NotImplementedError('is_delete_allowed()` must be implemented.')

    async def __save(self, session: AsyncSession, obj: ModelType) -> ModelType:
        session.add(obj)
        try:
            await session.commit()
        except exc.IntegrityError:
            session.rollback()
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                self.OBJECT_ALREADY_EXISTS)
        await session.refresh(obj)
        return obj

    async def __get_by_attribute(
        self,
        session: AsyncSession,
        attr_name: str,
        attr_value: Any,
    ):
        return await session.scalars(
            select(self.model).where(
                getattr(self.model, attr_name) == attr_value))

    async def get_all_by_attr(
        self,
        session: AsyncSession,
        attr_name: str,
        attr_value: Any,
    ) -> Optional[List[ModelType]]:
        objs = await self.__get_by_attribute(
            session, attr_name, attr_value)
        return objs.all()

    async def get_by_attr(
        self,
        session: AsyncSession,
        attr_name: str,
        attr_value: Any,
    ) -> Optional[ModelType]:
        objs = await self.__get_by_attribute(
            session, attr_name, attr_value)
        return objs.first()

    async def get(
        self, session: AsyncSession, pk: int,
    ) -> Optional[ModelType]:
        return await self.get_by_attr(session, 'id', pk)

    async def get_or_404(
        self, session: AsyncSession, pk: int,
        msg: str = 'Object not found',
    ) -> ModelType:
        obj = await self.get(session, pk)
        if obj is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, msg)
        return obj

    async def get_all(self, session: AsyncSession) -> List[ModelType]:
        objs = await session.scalars(select(self.model))
        return objs.all()

    async def create(
        self,
        session: AsyncSession,
        payload: CreateSchemaType,
        user: Optional[User] = None,
    ) -> ModelType:
        create_data = payload.dict()
        if user is not None:
            create_data['user_id'] = user.id
        return await self.__save(session, self.model(**create_data))

    async def update(
        self,
        session: AsyncSession,
        pk: int,
        payload: UpdateSchemaType,
        user: Optional[User] = None,
    ) -> ModelType:
        obj = await self.get_or_404(session, pk)
        self.has_permission(obj, user)
        update_data = payload.dict(
            exclude_unset=True,
            exclude_none=True,
            exclude_defaults=True)
        self.is_update_allowed(obj, update_data)
        for field in update_data:
            if field in jsonable_encoder(obj):
                setattr(obj, field, update_data[field])
        return await self.__save(session, obj)

    async def delete(
        self,
        session: AsyncSession,
        pk: int,
        user: Optional[User] = None,
    ) -> ModelType:
        obj = await self.get_or_404(session, pk)
        self.has_permission(obj, user)
        self.is_delete_allowed(obj)
        await session.delete(obj)
        await session.commit()
        return obj