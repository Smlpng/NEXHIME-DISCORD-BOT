import random

from discord.ext import commands


class CaraOuCoroa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="cara_ou_coroa",
        aliases=["coinflip", "coroa", "cara"],
        description="Joga cara ou coroa.",
    )
    async def cara_ou_coroa(self, ctx: commands.Context):
        result = random.choice(["Cara", "Coroa"])
        await ctx.reply(f"🪙 Deu **{result}**!", mention_author=False)


async def setup(bot):
    await bot.add_cog(CaraOuCoroa(bot))
