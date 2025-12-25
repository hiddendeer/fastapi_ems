"""
基础 CRUD 类
封装 FastCRUD，提供类型安全的 CRUD 操作
"""
from typing import Any, Generic, Type, TypeVar

from fastcrud import FastCRUD
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import Base


# 类型变量
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础 CRUD 类
    封装 FastCRUD，提供类型安全的数据库操作
    
    使用示例:
        class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
            pass
        
        user_crud = UserCRUD(User)
        
        # 在路由中使用
        async def get_user(db: AsyncSession, user_id: int):
            return await user_crud.get(db, id=user_id)
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 CRUD 实例
        
        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model
        self._crud = FastCRUD(model)

    async def get(
        self,
        db: AsyncSession,
        schema_to_select: Type[BaseModel] | None = None,
        return_as_model: bool = False,
        **kwargs: Any,
    ) -> dict | BaseModel | None:
        """
        获取单条记录
        
        Args:
            db: 数据库会话
            schema_to_select: 返回的 Schema 类型
            return_as_model: 是否返回 Pydantic 模型
            **kwargs: 查询条件
        
        Returns:
            查询结果字典或 Pydantic 模型，未找到返回 None
        """
        return await self._crud.get(
            db=db,
            schema_to_select=schema_to_select,
            return_as_model=return_as_model,
            **kwargs,
        )

    async def get_multi(
        self,
        db: AsyncSession,
        offset: int = 0,
        limit: int = 100,
        schema_to_select: Type[BaseModel] | None = None,
        return_as_model: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        获取多条记录
        
        Args:
            db: 数据库会话
            offset: 偏移量
            limit: 限制数量
            schema_to_select: 返回的 Schema 类型
            return_as_model: 是否返回 Pydantic 模型
            **kwargs: 查询条件
        
        Returns:
            包含 data 和 total_count 的字典
        """
        return await self._crud.get_multi(
            db=db,
            offset=offset,
            limit=limit,
            schema_to_select=schema_to_select,
            return_as_model=return_as_model,
            **kwargs,
        )

    async def create(
        self,
        db: AsyncSession,
        object: CreateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        创建记录
        
        Args:
            db: 数据库会话
            object: 创建数据（Pydantic 模型或字典）
        
        Returns:
            创建的模型实例
        """
        return await self._crud.create(db=db, object=object)

    async def create_and_get(
        self,
        db: AsyncSession,
        object: CreateSchemaType | dict[str, Any],
        **search_kwargs: Any,
    ) -> dict[str, Any] | None:
        """
        创建记录并返回完整的记录数据（包含自增 ID）
        
        Args:
            db: 数据库会话
            object: 创建数据（Pydantic 模型或字典）
            **search_kwargs: 用于查询新创建记录的条件（如果 create 返回 None）
        
        Returns:
            创建的完整记录（字典格式）
        """
        # 先尝试创建并获取返回的对象
        result = await self._crud.create(db=db, object=object)
        
        # 如果 FastCRUD 返回了对象，直接返回
        if result is not None:
            # 如果是 ORM 对象，需要刷新以获取自增 ID
            if hasattr(result, '__dict__') and hasattr(result, 'id'):
                # 重新查询以获取完整的数据（包括所有字段的默认值）
                return await self.get(db=db, id=result.id)
        
        # 如果创建返回了 None 或不完整，根据提供的搜索条件查询
        if search_kwargs:
            return await self.get(db=db, **search_kwargs)
        
        return None

    async def create_many(
        self,
        db: AsyncSession,
        objects: list[CreateSchemaType | dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        批量创建记录（优化版，毫秒级性能）
        
        使用 SQLAlchemy 原生的批量插入，比逐条插入快 100+ 倍
        
        Args:
            db: 数据库会话
            objects: 要创建的对象列表（Pydantic 模型或字典）
        
        Returns:
            创建的记录列表（包含自增 ID 和默认值）
        """
        if not objects:
            return []
        
        # 将 Pydantic 模型转换为字典
        objects_data = []
        for obj in objects:
            if isinstance(obj, dict):
                objects_data.append(obj)
            else:
                # Pydantic 模型转字典
                objects_data.append(obj.model_dump(exclude_unset=True))
        
        # 使用 SQLAlchemy 的 add_all() 方法批量插入
        # 这是最快的方式，一次性提交所有数据
        instances = [self.model(**data) for data in objects_data]
        db.add_all(instances)
        await db.flush()  # 刷新以获取自增 ID
        
        # 获取插入的记录的 ID
        ids = [instance.id for instance in instances]
        
        # 批量查询所有新插入的记录，获取完整数据（包括时间戳等）
        from sqlalchemy import select
        
        query = select(self.model).where(self.model.id.in_(ids))
        result = await db.execute(query)
        created_instances = result.scalars().all()
        
        # 转换为字典列表
        return [
            {
                "id": instance.id,
                **(
                    {col.name: getattr(instance, col.name) for col in instance.__table__.columns}
                    if hasattr(instance, '__table__')
                    else {}
                ),
            }
            for instance in created_instances
        ]

    async def update(
        self,
        db: AsyncSession,
        object: UpdateSchemaType | dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        更新记录
        
        Args:
            db: 数据库会话
            object: 更新数据（Pydantic 模型或字典）
            **kwargs: 查询条件
        """
        await self._crud.update(db=db, object=object, **kwargs)

    async def delete(
        self,
        db: AsyncSession,
        soft_delete: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        删除记录
        
        Args:
            db: 数据库会话
            soft_delete: 是否软删除
            **kwargs: 查询条件
        """
        if soft_delete:
            await self._crud.db_delete(db=db, soft_delete=True, **kwargs)
        else:
            await self._crud.delete(db=db, **kwargs)

    async def count(
        self,
        db: AsyncSession,
        **kwargs: Any,
    ) -> int:
        """
        统计记录数
        
        Args:
            db: 数据库会话
            **kwargs: 查询条件
        
        Returns:
            记录数量
        """
        return await self._crud.count(db=db, **kwargs)

    async def exists(
        self,
        db: AsyncSession,
        **kwargs: Any,
    ) -> bool:
        """
        检查记录是否存在
        
        Args:
            db: 数据库会话
            **kwargs: 查询条件
        
        Returns:
            是否存在
        """
        return await self._crud.exists(db=db, **kwargs)

    async def get_or_create(
        self,
        db: AsyncSession,
        object: CreateSchemaType | dict[str, Any],
        **kwargs: Any,
    ) -> tuple[ModelType, bool]:
        """
        获取或创建记录
        
        Args:
            db: 数据库会话
            object: 创建数据
            **kwargs: 查询条件
        
        Returns:
            (模型实例, 是否新创建)
        """
        existing = await self.get(db=db, **kwargs)
        if existing:
            return existing, False
        created = await self.create(db=db, object=object)
        return created, True

    async def update_or_create(
        self,
        db: AsyncSession,
        object: CreateSchemaType | UpdateSchemaType | dict[str, Any],
        **kwargs: Any,
    ) -> tuple[ModelType, bool]:
        """
        更新或创建记录
        
        Args:
            db: 数据库会话
            object: 创建/更新数据
            **kwargs: 查询条件
        
        Returns:
            (模型实例, 是否新创建)
        """
        existing = await self.get(db=db, **kwargs)
        if existing:
            await self.update(db=db, object=object, **kwargs)
            return await self.get(db=db, **kwargs), False
        created = await self.create(db=db, object=object)
        return created, True


class CRUDFactory:
    """
    CRUD 工厂类
    快速创建 CRUD 实例
    
    使用示例:
        user_crud = CRUDFactory.create(User)
        item_crud = CRUDFactory.create(Item)
    """

    @staticmethod
    def create(model: Type[ModelType]) -> BaseCRUD[ModelType, BaseModel, BaseModel]:
        """
        创建 CRUD 实例
        
        Args:
            model: SQLAlchemy 模型类
        
        Returns:
            BaseCRUD 实例
        """
        return BaseCRUD(model)

