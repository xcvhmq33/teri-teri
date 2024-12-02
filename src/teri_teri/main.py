import asyncio

import discord
from config import settings
from discord.ext import commands

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())


async def main() -> None:
    async with bot:
        await bot.load_extension("cogs.base")
        await bot.load_extension("cogs.equipdex")
        await bot.load_extension("cogs.data_manager")
        await bot.start(settings.TOKEN)


asyncio.run(main())
