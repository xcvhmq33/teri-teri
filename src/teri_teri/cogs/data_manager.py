import asyncio
from pathlib import Path

import discord
from config import DATA_ALL_DIR, EXTRACTED_DIR
from crud import create, delete
from database import (
    Item as ItemORM,
)
from database import (
    Properties as PropertiesORM,
)
from database import (
    Session,
)
from database import (
    Skill as SkillORM,
)
from discord import app_commands
from discord.ext import commands
from hg2_data_extractor import DataCipher, DataDownloader, DataExtractor
from hg2_data_extractor.enums import PRESETS, Preset, Server
from hg2_item_parser import ItemParser
from hg2_item_parser.exceptions import ItemNotFoundError
from hg2_item_parser.models import Item


class ItemUpdater:
    def __init__(self, data_dir_path: Path):
        self.data_dir_path = data_dir_path
        self.parser = ItemParser(self.data_dir_path)

    async def parse_in_thread(self, item_id: int) -> Item:
        parsed_item = await asyncio.to_thread(self.parser.parse_item, item_id)
        return parsed_item

    async def parse_and_update(self, item_id: int) -> None:
        parsed_item = await self.parse_in_thread(item_id)
        item_orm = self.item_to_orm(parsed_item)
        async with Session.begin() as session:
            await delete(session, item_orm)
        async with Session.begin() as session:
            await create(session, item_orm)

    def item_to_orm(self, parsed_item: Item) -> ItemORM:
        info_dict = parsed_item.info.__dict__.copy()
        info_dict.pop("id")
        info_dict["ingame_id"] = parsed_item.info.id
        item_orm = ItemORM(**info_dict)

        for parsed_skill in parsed_item.skills:
            skill_dict = parsed_skill.__dict__.copy()
            skill_dict.pop("id")
            skill_dict["ingame_id"] = parsed_skill.id
            skill_orm = SkillORM(**skill_dict)
            item_orm.skills.append(skill_orm)

        properties_orm = PropertiesORM(**parsed_item.properties.__dict__)
        item_orm.properties = properties_orm

        return item_orm


class DataManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @app_commands.command(
        name="update_item", description="Parse and insert item to database"
    )
    async def update_item(self, interaction: discord.Interaction, item_id: int) -> None:
        await interaction.response.defer()
        updater = ItemUpdater(EXTRACTED_DIR)
        try:
            await updater.parse_and_update(item_id)
        except ItemNotFoundError:
            await interaction.followup.send(
                f"❌ **Item No. `{item_id}` not found!**", ephemeral=True
            )
            return
        await interaction.followup.send(
            f"✅ **Item No. `{item_id}` updated!**", ephemeral=True
        )

    @commands.is_owner()
    @app_commands.command(
        name="update_data", description="Download, decrypt and extract items data"
    )
    async def update_data(
        self, interaction: discord.Interaction, server: Server, version: str
    ) -> None:
        await interaction.response.defer()
        try:
            downloader = DataDownloader(server, version)
            downloader.download_data_all(DATA_ALL_DIR)
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Something get wrong while downloading:**\n{e}", ephemeral=True
            )
            return
        DataCipher.decrypt_file(DATA_ALL_DIR / "data_all.unity3d")
        extractor = DataExtractor(DATA_ALL_DIR / "data_all_dec.unity3d")
        for asset_name in PRESETS[Preset.ITEMS]:
            extractor.extract_asset(asset_name, EXTRACTED_DIR)

        await interaction.followup.send("✅ **Data updated!**", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DataManager(bot))
