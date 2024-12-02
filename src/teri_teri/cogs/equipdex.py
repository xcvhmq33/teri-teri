import crud
import discord
from database import Item, Session
from discord import app_commands
from discord.ext import commands
from hg2_item_parser.enums import DamageType

DAMAGE_TYPE_EMOJIS = {
    DamageType.PHYSICAL: "🗡️",
    DamageType.FIRE: "🔥",
    DamageType.ICE: "❄️",
    DamageType.ENERGY: "🔯",
    DamageType.LIGHT: "⚡",
    DamageType.POISON: "☠️",
    DamageType.NONE: "",
}


class Equipdex(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="get_item_text", description="Get item text ids by item id")
    async def get_item_text(self, interaction: discord.Interaction, item_id: int) -> None:
        await interaction.response.defer()
        async with Session() as session:
            item = await crud.read_by_ingame_id(session, item_id)
            if item is not None:
                response = (
                    f"**Item No.** {item.ingame_id}\n"
                    f"**Title:** {item.title} [`{item.title_id}`]\n"
                )
                for i, skill in enumerate(item.skills):
                    response += f"\n**Skill {i}**: {skill.title} [`{skill.title_id}`]\n"
                    response += f"{skill.description_template} [`{skill.description_template_id}`]\n"

                await interaction.followup.send(response)
                return
            
        await interaction.followup.send(f"❌ **Item not found:** `{item_id}`")

    @app_commands.command(name="search_item", description="Search for an item by title or id")
    async def search_item(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer()
        async with Session() as session:
            if query.isnumeric() and query.isascii():
                item = await crud.read_by_ingame_id(session, int(query))
                if item is not None:
                    await self.handle_item(interaction, item)
                    return
            else:
                items = await crud.search_by_title(session, query)
                if items:
                    if len(items) > 1:
                        await self.handle_items(interaction, items)
                    else:
                        await self.handle_item(interaction, items[0])
                    return

        await interaction.followup.send(f"❌ **Item not found:** `{query}`")

    async def handle_item(self, interaction: discord.Interaction, item: Item) -> None:
        embed = discord.Embed(color=discord.Color.blue())
        self.add_info_embed(embed, item)
        self.add_properties_embed(embed, item)
        self.add_skills_embed(embed, item)

        await interaction.followup.send(embed=embed)

    @staticmethod
    def add_info_embed(embed: discord.Embed, item: Item) -> None:
        damage_type_emoji = DAMAGE_TYPE_EMOJIS[item.damage_type]
        rarity = item.rarity * "⭐"
        embed.title = f"{item.title} {damage_type_emoji}\n{rarity}"
        embed.set_thumbnail(url=item.image_url)
        embed.set_author(name=f"No. {item.ingame_id}")

    @staticmethod
    def add_properties_embed(embed: discord.Embed, item: Item) -> None:
        weapon_type = None
        if item.properties.weapon_type is not None:
            weapon_type = item.properties.weapon_type.value

        crit_rate = None
        if item.properties.crit_rate is not None:
            crit_rate = f"{item.properties.crit_rate*100}%"

        fields = [
            ("Max Lvl", item.properties.max_lvl),
            ("Cost", item.properties.cost),
            ("Type", weapon_type),
            ("Max Lvl Damage", item.properties.max_lvl_damage),
            ("Max Lvl Ammo", item.properties.max_lvl_ammo),
            ("Max Lvl ASPD", item.properties.max_lvl_atk_speed),
            ("Max Lvl HP", item.properties.max_lvl_hp),
            ("Deploy Limit", item.properties.deploy_limit),
            ("Duration", item.properties.duration),
            ("Crit Rate", crit_rate),
            ("Base Sync", item.properties.base_sync),
            ("Max Sync", item.properties.max_sync),
        ]

        for name, value in fields:
            if value is not None:
                embed.add_field(name=name, value=value, inline=True)

    @staticmethod
    def add_skills_embed(embed: discord.Embed, item: Item) -> None:
        for skill in item.skills:
            damage_type_emoji = DAMAGE_TYPE_EMOJIS[skill.damage_type]
            embed.add_field(
                name=f"{skill.title} {damage_type_emoji}",
                value=skill.description,
                inline=False,
            )

    async def handle_items(
        self, interaction: discord.Interaction, items: list[Item]
    ) -> None:
        items = items[:20]
        formatted_items = "\n".join(
            f"`- {item.title} [ID: {item.ingame_id}] {item.rarity}⭐`" for item in items
        )
        response = (
            f"**✅ Multiple items found:**\n{formatted_items}\n"
            "***please use **`/search_item [ID]`** to select a specific item***"
        )

        await interaction.followup.send(response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Equipdex(bot))
