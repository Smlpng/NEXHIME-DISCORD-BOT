import asyncio
import random

import discord
from discord.ext import commands


WORDS = [
    "banana",
    "gorila",
    "floresta",
    "dragao",
    "castelo",
    "tesouro",
    "discord",
    "aventura",
    "fantasia",
    "misterio",
]


class Forca(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="forca", help="Joga uma rodada de forca no chat.")
    async def forca(self, ctx: commands.Context):
        word = random.choice(WORDS)
        guessed_letters: set[str] = set()
        wrong_letters: list[str] = []
        max_errors = 6

        def masked_word() -> str:
            return " ".join(letter if letter in guessed_letters else "_" for letter in word)

        embed = discord.Embed(title="Forca", color=discord.Color.blurple())
        embed.description = f"Palavra: {masked_word()}\nErros: 0/{max_errors}\nLetras erradas: --"
        await ctx.reply(embed=embed)

        while True:
            if all(letter in guessed_letters for letter in word):
                return await ctx.send(f"{ctx.author.mention} venceu a forca. A palavra era **{word}**.")
            if len(wrong_letters) >= max_errors:
                return await ctx.send(f"Fim de jogo. A palavra era **{word}**.")

            try:
                guess_message = await self.bot.wait_for(
                    "message",
                    timeout=40,
                    check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
                )
            except asyncio.TimeoutError:
                return await ctx.send(f"Tempo esgotado. A palavra era **{word}**.")

            guess = guess_message.content.strip().lower()
            if len(guess) != 1 or not guess.isalpha():
                await ctx.send("Envie apenas uma letra por vez.", delete_after=4)
                continue
            if guess in guessed_letters or guess in wrong_letters:
                await ctx.send("Essa letra ja foi usada.", delete_after=4)
                continue

            if guess in word:
                guessed_letters.add(guess)
            else:
                wrong_letters.append(guess)

            embed = discord.Embed(title="Forca", color=discord.Color.blurple())
            embed.description = (
                f"Palavra: {masked_word()}\n"
                f"Erros: {len(wrong_letters)}/{max_errors}\n"
                f"Letras erradas: {', '.join(wrong_letters) if wrong_letters else '--'}"
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Forca(bot))