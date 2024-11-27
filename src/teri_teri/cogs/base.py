import discord
from discord import app_commands
from discord.ext import commands


class Base(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.tree.sync()
        print(f"Bot has logged in as {self.bot.user}")

    @commands.is_owner()
    @app_commands.command(name="shutdown", description="Close bot session")
    async def shutdown(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await self.bot.close()

    @commands.is_owner()
    @app_commands.command(name="sync", description="Synchronize all commands")
    async def sync(self, interaction: discord.Interaction) -> None:
        synced = await self.bot.tree.sync()
        command_names = "\n".join(f"{command.name}" for command in synced)
        await interaction.response.send_message(
            f"Synced {len(synced)} command(s):\n{command_names}", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Base(bot))
