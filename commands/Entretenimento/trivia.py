import asyncio
import random

import discord
from discord.ext import commands


_QUESTIONS = [
    {
        "q": "Qual planeta é conhecido como 'Planeta Vermelho'?",
        "a": ["marte"],
    },
    {
        "q": "Quantos lados tem um triângulo?",
        "a": ["3", "tres", "três"],
    },
    {
        "q": "Qual é a capital do Brasil?",
        "a": ["brasilia", "brasília"],
    },
    {
        "q": "Em que continente fica o Egito?",
        "a": ["africa", "áfrica"],
    },
]


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="trivia",
        aliases=["quiz"],
        help="Faz uma pergunta rápida; responda no chat em até 20s.",
    )
    async def trivia(self, ctx: commands.Context):
        item = random.choice(_QUESTIONS)
        question = item["q"]
        answers = {a.strip().lower() for a in item["a"]}

        embed = discord.Embed(title="🧠 Trivia", description=question, color=discord.Color.gold())
        embed.set_footer(text="Responda no chat em até 20 segundos.")
        await ctx.reply(embed=embed, mention_author=False)

        def check(msg: discord.Message) -> bool:
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
            return await ctx.reply("⏱️ Tempo esgotado!", mention_author=False)

        guess = (msg.content or "").strip().lower()
        if guess in answers:
            return await ctx.reply("✅ Resposta correta!", mention_author=False)
        pretty = ", ".join(sorted(item["a"]))
        await ctx.reply(f"❌ Errado. Resposta(s) aceita(s): **{pretty}**", mention_author=False)


async def setup(bot):
    await bot.add_cog(Trivia(bot))
