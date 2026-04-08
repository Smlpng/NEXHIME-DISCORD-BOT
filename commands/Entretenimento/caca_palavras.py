import random
import string

import discord
from discord.ext import commands


WORDS = ["BANANA", "CASTELO", "DRAGAO", "FLORESTA", "TESOURO", "AVENTURA"]
GRID_SIZE = 8


def _build_grid(word: str) -> list[list[str]]:
    grid = [[random.choice(string.ascii_uppercase) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    row = random.randint(0, GRID_SIZE - 1)
    col = random.randint(0, GRID_SIZE - len(word))
    for index, letter in enumerate(word):
        grid[row][col + index] = letter
    return grid


def _grid_text(grid: list[list[str]]) -> str:
    return "\n".join(" ".join(row) for row in grid)


class CacaPalavras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="caca_palavras", aliases=["cacapalavras", "wordhunt"], help="Mostra um mini caça-palavras com uma unica palavra escondida.")
    async def caca_palavras(self, ctx: commands.Context):
        word = random.choice(WORDS)
        grid = _build_grid(word)
        hint = f"A palavra tem {len(word)} letras."

        embed = discord.Embed(title="Caça-palavras", color=discord.Color.blurple())
        embed.description = f"```\n{_grid_text(grid)}\n```"
        embed.add_field(name="Dica", value=hint, inline=False)
        embed.set_footer(text=f"Resposta: {word.title()}")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CacaPalavras(bot))