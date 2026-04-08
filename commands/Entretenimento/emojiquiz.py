import random

import discord
from discord.ext import commands


QUIZ = [
    {"emoji": "🍌👑", "answer": "rei macaco"},
    {"emoji": "🔥🐉", "answer": "dragao de fogo"},
    {"emoji": "🌧️⚡", "answer": "tempestade"},
    {"emoji": "🏰👻", "answer": "castelo assombrado"},
    {"emoji": "🐺🌕", "answer": "lobisomem"},
]


class EmojiQuiz(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="emojiquiz", aliases=["quizemoji"], help="Mostra um enigma curto com emojis.")
    async def emojiquiz(self, ctx: commands.Context):
        question = random.choice(QUIZ)
        embed = discord.Embed(title="Emoji Quiz", description=question["emoji"], color=discord.Color.gold())
        embed.set_footer(text=f"Resposta: {question['answer']}")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiQuiz(bot))