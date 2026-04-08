import asyncio
import random

import discord
from discord.ext import commands


QUESTIONS = [
    ("Qual emoji combina mais com um dragao?", ["🐉", "🍞", "🪑"], "🐉"),
    ("O que normalmente vem depois do raio?", ["⚡ chuva", "⚡ banana", "⚡ silencio eterno"], "⚡ chuva"),
    ("Qual item faz mais sentido em uma dungeon?", ["Espada", "Micro-ondas", "Patinete"], "Espada"),
]


class BossRush(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bossrush", aliases=["rushquiz"], help="Encare uma sequencia curta de perguntas em tempo limitado.")
    async def bossrush(self, ctx: commands.Context):
        score = 0
        selected_questions = random.sample(QUESTIONS, k=min(3, len(QUESTIONS)))

        for index, (question, options, answer) in enumerate(selected_questions, start=1):
            embed = discord.Embed(title=f"Boss Rush {index}/{len(selected_questions)}", description=question, color=discord.Color.red())
            embed.add_field(name="Opcoes", value="\n".join(f"- {option}" for option in options), inline=False)
            await ctx.send(embed=embed)
            try:
                reply = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
                )
            except asyncio.TimeoutError:
                await ctx.send("Tempo esgotado nessa rodada.")
                continue

            if reply.content.strip().lower() == answer.strip().lower():
                score += 1
                await ctx.send("Acertou.")
            else:
                await ctx.send(f"Errou. Resposta correta: {answer}")

        await ctx.reply(f"Boss Rush finalizado. Pontuacao: **{score}/{len(selected_questions)}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(BossRush(bot))