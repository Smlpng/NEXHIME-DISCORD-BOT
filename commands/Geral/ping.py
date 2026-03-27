import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", aliases=["latencia", "latência", "ms"], description="Latência do bot")
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f"🏓 | Pong! {round(self.bot.latency * 1000)}ms")

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
