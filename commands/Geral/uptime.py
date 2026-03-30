import time

import discord
from discord.ext import commands


class Uptime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not hasattr(bot, "_started_at_ts"):
            bot._started_at_ts = int(discord.utils.utcnow().timestamp())
        if not hasattr(bot, "_started_at_monotonic"):
            bot._started_at_monotonic = time.monotonic()

    @commands.hybrid_command(name="uptime", aliases=["online"], description="Mostra há quanto tempo o bot está online.")
    async def uptime(self, ctx: commands.Context):
        started_ts = int(getattr(self.bot, "_started_at_ts", int(discord.utils.utcnow().timestamp())))
        seconds = max(0, int(time.monotonic() - getattr(self.bot, "_started_at_monotonic", time.monotonic())))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.reply(
            f"🟢 Estou online desde <t:{started_ts}:F> (<t:{started_ts}:R>).\n"
            f"⏱️ Uptime: {hours}h {minutes}m {seconds}s",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Uptime(bot))
