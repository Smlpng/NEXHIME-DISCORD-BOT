from pathlib import Path

import discord
from discord.ext import commands


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "assets" / "templates"


KNOWN = [
    ("cerebro", "cérebro", "Expanding Brain"),
    ("pisei", "pisei", "pisei na merda"),
    ("queimar", "queimar", "queimar"),
    ("triangulo", "triângulo", "triângulo amoroso"),
    ("trio_dragoes", "trio_dragão", "trio de dragões"),
    ("tweet", "tweet", "tweet falso"),
    ("wanted", "procurado", "wanted"),
]


class MemeLista(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="meme_lista",
        aliases=["memes_lista", "templates"],
        description="Lista os geradores de imagem disponíveis.",
    )
    async def meme_lista(self, ctx: commands.Context):
        existing = set()
        if TEMPLATES_DIR.exists():
            for p in TEMPLATES_DIR.iterdir():
                if p.is_dir():
                    existing.add(p.name)

        lines = []
        for folder, cmd, label in KNOWN:
            status = "✅" if folder in existing else "⚠️"
            lines.append(f"{status} **{cmd}** — {label}")

        embed = discord.Embed(title="🎨 Geradores de imagem", description="\n".join(lines), color=discord.Color.purple())
        embed.set_footer(text="Use /help para ver detalhes e exemplos.")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(MemeLista(bot))
