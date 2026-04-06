import asyncio
import random

import discord
from discord.ext import commands


_WORDS = [
    "banana", "cachorro", "tartaruga", "diamante", "foguete", "guitarra",
    "hipopótamo", "janela", "lagarta", "mariposa", "nuvem", "oceano",
    "pinguim", "queijo", "relógio", "sapato", "tigre", "urso",
    "ventilador", "xilogravura", "zebra", "abacaxi", "borboleta",
    "castelo", "dragão", "elefante", "floresta", "galinha", "harpa",
    "ilha", "jangada", "kiwi", "livro", "montanha", "navio",
    "orquídea", "palácio", "quadro", "riacho", "sereia", "tomate",
    "uva", "violino", "xadrez", "yacare", "zoológico",
]

_STAGES = [
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        "      |\n"
        "      |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        "  |   |\n"
        "      |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|   |\n"
        "      |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        "      |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        " /    |\n"
        "      |\n"
        "=========```"
    ),
    (
        "```\n"
        "  +---+\n"
        "  |   |\n"
        "  O   |\n"
        " /|\\  |\n"
        " / \\  |\n"
        "      |\n"
        "=========```"
    ),
]

_MAX_WRONG = len(_STAGES) - 1


def _display_word(word: str, guessed: set[str]) -> str:
    return " ".join(c if c in guessed or not c.isalpha() else r"\_" for c in word)


class Forca(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="forca",
        aliases=["hangman", "jogo_da_forca"],
        help="Joga a forca. Adivinhe a palavra letra por letra.",
    )
    async def forca(self, ctx: commands.Context):
        """Inicia um jogo da forca com uma palavra aleatória."""
        word = random.choice(_WORDS).lower()
        guessed: set[str] = set()
        wrong: list[str] = []

        def build_embed() -> discord.Embed:
            stage = _STAGES[len(wrong)]
            display = _display_word(word, guessed)
            embed = discord.Embed(title="🪢 Jogo da Forca", color=discord.Color.orange())
            embed.description = stage
            embed.add_field(name="Palavra", value=f"`{display}`", inline=False)
            if wrong:
                embed.add_field(name="Letras erradas", value=" ".join(wrong), inline=False)
            embed.set_footer(text=f"Erros: {len(wrong)}/{_MAX_WRONG} — Digite uma letra no chat.")
            return embed

        msg = await ctx.reply(embed=build_embed(), mention_author=False)

        def check(m: discord.Message) -> bool:
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        while True:
            # Check win condition
            if all(c in guessed or not c.isalpha() for c in word):
                final = discord.Embed(
                    title="🎉 Você venceu!",
                    description=f"A palavra era **{word}**.",
                    color=discord.Color.green(),
                )
                return await ctx.reply(embed=final, mention_author=False)

            if len(wrong) >= _MAX_WRONG:
                final = discord.Embed(
                    title="💀 Game Over",
                    description=f"A palavra era **{word}**.",
                    color=discord.Color.red(),
                )
                return await ctx.reply(embed=final, mention_author=False)

            try:
                guess_msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.reply("⏱️ Tempo esgotado! Jogo encerrado.", mention_author=False)

            letter = guess_msg.content.strip().lower()
            if len(letter) != 1 or not letter.isalpha():
                await ctx.reply("Digite apenas **uma letra** por vez.", mention_author=False)
                continue
            if letter in guessed or letter in wrong:
                await ctx.reply("Você já tentou essa letra.", mention_author=False)
                continue

            if letter in word:
                guessed.add(letter)
            else:
                wrong.append(letter)

            try:
                await msg.edit(embed=build_embed())
            except Exception:
                msg = await ctx.send(embed=build_embed())


async def setup(bot: commands.Bot):
    await bot.add_cog(Forca(bot))
