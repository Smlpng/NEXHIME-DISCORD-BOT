import discord
import random
from discord.ext import commands

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="piada", aliases=["joke"], help="Receba uma piada aleatória para alegrar o dia.")
    async def joke(self, ctx: commands.Context):
        """Responde com uma piada aleatória."""
        jokes = [
            "Por que o livro foi ao médico? Porque estava com muitas páginas em branco!",
            "O que o zero disse para o oito? Bonito cinto!",
            "Qual é o animal que é dois em um? O camelo, porque tem duas corcovas!",
            "Por que o JavaScript foi ao terapeuta? Porque não conseguia lidar com suas promessas!",
            "Como o elétron se sente no trabalho? Sempre em movimento e nunca em repouso!"
        ]
        joke = random.choice(jokes)
        await ctx.reply(joke, mention_author=False)

async def setup(bot):
    await bot.add_cog(Joke(bot))
