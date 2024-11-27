from collections.abc import Sequence

from database import Item
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


async def create(session: AsyncSession, item: Item) -> None:
    session.add(item)


async def search_by_title(session: AsyncSession, title: str) -> Sequence[Item]:
    statement = (
        select(Item)
        .where(Item.title.icontains(title))
        .options(
            joinedload(Item.properties),
            joinedload(Item.skills),
        )
    )
    result = await session.execute(statement)
    items = result.unique().scalars().all()

    return items


async def read_by_ingame_id(session: AsyncSession, ingame_id: int) -> Item | None:
    query = (
        select(Item)
        .where(Item.ingame_id == ingame_id)
        .options(
            joinedload(Item.properties),
            joinedload(Item.skills),
        )
    )
    result = await session.execute(query)
    item = result.scalars().first()

    return item


async def delete(session: AsyncSession, item: Item) -> None:
    query = select(Item).where(Item.ingame_id == item.ingame_id)
    result = await session.execute(query)
    item = result.scalar_one_or_none()
    if item is not None:
        await session.delete(item)
