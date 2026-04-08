import random

from discord.ext import commands


EVENTS = [
    "Uma chuva de bananas caiu do nada sobre o servidor.",
    "Um bardo apareceu e comecou a narrar o chat como se fosse um anime.",
    "Um portal abriu e trouxe um goblin vendendo pao de alho encantado.",
    "Todo mundo recebeu uma missao secreta que ninguem entendeu direito.",
    "Um dragao passou voando e ignorou completamente a staff.",
    "O relampago caiu, mas por algum motivo so acertou os emojis.",
]


class Acontecimento(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="acontecimento", aliases=["eventoaleatorio"], help="Gera um evento caotico aleatorio no chat.")
    async def acontecimento(self, ctx: commands.Context):
        await ctx.reply(random.choice(EVENTS))


async def setup(bot: commands.Bot):
    await bot.add_cog(Acontecimento(bot))