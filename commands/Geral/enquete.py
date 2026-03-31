import asyncio
import re

import discord
from discord.ext import commands


_NUMBER_EMOJIS = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",
]


def _parse_duration_to_seconds(duration: str | None) -> int | None:
    if not duration:
        return None
    duration = duration.strip().lower()
    match = re.fullmatch(r"(\d+)([smhd])", duration)
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return max(1, value * mult)


class Enquete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="enquete",
        aliases=["poll"],
        help="Cria uma enquete com opções separadas por | (ex: opção A | opção B).",
    )
    async def enquete(self, ctx: commands.Context, pergunta: str, opcoes: str, duracao: str | None = None):
        options = [opt.strip() for opt in opcoes.split("|") if opt.strip()]
        if len(options) < 2:
            return await ctx.reply("Forneça pelo menos 2 opções separadas por `|`.", mention_author=False)
        if len(options) > 10:
            return await ctx.reply("Máximo de 10 opções.", mention_author=False)

        seconds = _parse_duration_to_seconds(duracao)
        if duracao and seconds is None:
            return await ctx.reply("Duração inválida. Use algo como `10m`, `2h`, `1d`.", mention_author=False)

        desc = "\n".join(f"{_NUMBER_EMOJIS[i]} {opt}" for i, opt in enumerate(options))
        if seconds:
            end_ts = int(discord.utils.utcnow().timestamp()) + seconds
            desc += f"\n\n⏳ Encerra em <t:{end_ts}:R>."

        embed = discord.Embed(title="📊 Enquete", description=f"**{pergunta}**\n\n{desc}", color=discord.Color.green())
        embed.set_footer(text=f"Criada por {ctx.author}")

        message = await ctx.reply(embed=embed, mention_author=False)
        for i in range(len(options)):
            try:
                await message.add_reaction(_NUMBER_EMOJIS[i])
            except Exception:
                pass

        if seconds:
            # Apenas marca visualmente o término (não faz apuração automática para evitar inconsistências de mensagens em híbridos)
            await asyncio.sleep(seconds)
            try:
                await message.reply("⏱️ Enquete encerrada.", mention_author=False)
            except Exception:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Enquete(bot))
