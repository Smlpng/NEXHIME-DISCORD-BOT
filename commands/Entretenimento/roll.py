import discord
import random
from discord.ext import commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rolar", aliases=["roll"], help="Rola um dado ou escolhe um número aleatório.")
    async def roll(self, ctx: commands.Context, number: int):
        """Rola um dado ou escolhe um número aleatório entre 1 e o número fornecido."""
        if number <= 0:
            await ctx.reply("Por favor, insira um número maior que 0.", mention_author=False)
            return
        result = random.randint(1, number)
        await ctx.reply(f'O número sorteado entre 1 e {number} é: {result}', mention_author=False)

async def setup(bot):
    await bot.add_cog(Roll(bot))
