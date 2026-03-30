import asyncio
import re

import discord
from discord.ext import commands


def _parse_duration_to_seconds(duration: str) -> int | None:
    duration = (duration or "").strip().lower()
    match = re.fullmatch(r"(\d+)([smhd])", duration)
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return max(1, value * mult)


class Timer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="timer",
        aliases=["lembrete_canal"],
        description="Agenda uma mensagem após um tempo (ex: 10m, 2h, 1d).",
    )
    async def timer(self, ctx: commands.Context, tempo: str, *, mensagem: str):
        seconds = _parse_duration_to_seconds(tempo)
        if seconds is None:
            return await ctx.reply("Formato de tempo inválido. Use `5m`, `1h`, `2d`...", mention_author=False)

        end_ts = int(discord.utils.utcnow().timestamp()) + seconds
        await ctx.reply(f"⏳ Timer configurado para <t:{end_ts}:R>.", mention_author=False)

        await asyncio.sleep(seconds)
        try:
            await ctx.channel.send(f"⏰ {ctx.author.mention} {mensagem}")
        except Exception:
            # fallback para DM
            try:
                await ctx.author.send(f"⏰ {mensagem}")
            except Exception:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Timer(bot))
