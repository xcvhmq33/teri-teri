from config import settings
from hg2_item_parser.enums import DamageType, WeaponType
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, AsyncAttrs): ...


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingame_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    title_id: Mapped[int]
    title: Mapped[str] = mapped_column(String(64))
    image_id: Mapped[int]
    image_url: Mapped[str]
    damage_type: Mapped[DamageType] = mapped_column(nullable=True)
    rarity: Mapped[int]

    properties: Mapped["Properties"] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )

    def __str__(self):
        return (
            f"ID: {self.id}\n"
            f"Ingame ID: {self.ingame_id}\n"
            f"Title: {self.title}\n"
            f"Image URL: {self.image_url}\n"
            f"Damage Type: {self.damage_type}\n"
            f"Rarity: {self.rarity}"
        )


class Properties(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    max_lvl: Mapped[int]
    cost: Mapped[int] = mapped_column(nullable=True)
    max_lvl_damage: Mapped[int] = mapped_column(nullable=True)
    max_lvl_ammo: Mapped[int] = mapped_column(nullable=True)
    max_lvl_atk_speed: Mapped[float] = mapped_column(nullable=True)
    max_lvl_hp: Mapped[int] = mapped_column(nullable=True)
    weapon_type: Mapped[WeaponType] = mapped_column(nullable=True)
    deploy_limit: Mapped[int] = mapped_column(nullable=True)
    duration: Mapped[float] = mapped_column(nullable=True)
    crit_rate: Mapped[float] = mapped_column(nullable=True)
    base_sync: Mapped[int] = mapped_column(nullable=True)
    max_sync: Mapped[int] = mapped_column(nullable=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.ingame_id"))

    item: Mapped["Item"] = relationship(back_populates="properties")

    def __str__(self):
        return (
            f"Max Lvl: {self.max_lvl}\n"
            f"Cost: {self.cost}\n"
            f"Max Lvl Damage: {self.max_lvl_damage}\n"
            f"Max Lvl Ammo: {self.max_lvl_ammo}\n"
            f"Max Lvl ASPD: {self.max_lvl_atk_speed}\n"
            f"Max Lvl HP: {self.max_lvl_hp}\n"
            f"Weapon Type: {self.weapon_type}\n"
            f"Deploy Limit: {self.deploy_limit}\n"
            f"Duration: {self.duration}\n"
            f"Crit Rate: {self.crit_rate}\n"
            f"Base Sync: {self.base_sync}\n"
            f"Max Sync: {self.max_sync}"
        )


class Skill(Base):
    __tablename__ = "skill"
    id: Mapped[int] = mapped_column(primary_key=True)
    ingame_id: Mapped[int]
    title_id: Mapped[int]
    title: Mapped[str] = mapped_column(String(64))
    description_template_id: Mapped[int]
    description_template: Mapped[str]
    description: Mapped[str]
    damage_type: Mapped[DamageType] = mapped_column(nullable=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.ingame_id"))

    item: Mapped["Item"] = relationship(back_populates="skills")

    def __str__(self):
        return f"{self.title}[{self.damage_type}]\n{self.description}"


engine = create_async_engine(settings.DATABASE_URL)
Session = async_sessionmaker(engine)


def create_all() -> None:
    Base.metadata.create_all(engine)


def drop_all() -> None:
    Base.metadata.drop_all(engine)
