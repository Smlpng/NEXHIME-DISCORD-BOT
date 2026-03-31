import discord
import random
from discord.ext import commands

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bola8", aliases=["8ball"], help="Faça uma pergunta e receba uma resposta aleatória.")
    async def eight_ball(self, ctx: commands.Context, *, question: str):
        """Responde com uma frase aleatória como 'Sim', 'Não', 'Talvez', etc."""
        responses = [
            "Sim",
            "Não",
            "Talvez",
            "Com certeza",
            "Não sei",
            "Provavelmente não",
            "As estrelas dizem que sim",
            "Pergunte novamente mais tarde",
            "Acho que sim, mas não tenho certeza"
        ]
        response = random.choice(responses)
        await ctx.reply(f"Pergunta: {question}\nResposta: {response}", mention_author=False)

async def setup(bot):
    await bot.add_cog(EightBall(bot))
