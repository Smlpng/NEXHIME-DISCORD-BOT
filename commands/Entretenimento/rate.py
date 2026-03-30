import hashlib

from discord.ext import commands


def _stable_score(seed_text: str) -> int:
    h = hashlib.md5(seed_text.encode("utf-8"))
    value = int.from_bytes(h.digest()[:2], "big")
    return value % 11


class Rate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="rate",
        aliases=["nota"],
        description="Dá uma nota (0 a 10) para um texto ou usuário.",
    )
    async def rate(self, ctx: commands.Context, *, alvo: str):
        gid = str(ctx.guild.id) if ctx.guild else "dm"
        seed = f"{gid}:{ctx.author.id}:{alvo.strip().lower()}"
        score = _stable_score(seed)
        await ctx.reply(f"🎯 Eu dou **{score}/10** para: {alvo}", mention_author=False)


async def setup(bot):
    await bot.add_cog(Rate(bot))
