import random

import discord
from discord.ext import commands


REWARDS = [
    ("Comum", "🪨", "Uma pedra misteriosa que provavelmente nao serve para nada."),
    ("Incomum", "🧭", "Uma bussola quebrada que ainda tenta apontar para aventura."),
    ("Raro", "💍", "Um anel estranho com simbolos antigos."),
    ("Epico", "🗡️", "Uma arma lendaria de procedencia duvidosa."),
    ("Lendario", "👑", "Uma coroa absurda que transforma qualquer mensagem em pose de rei."),
]


class Caixinha(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="caixinha", aliases=["lootbox", "caixa"], help="Abre uma caixinha aleatoria de entretenimento.")
    async def caixinha(self, ctx: commands.Context):
        rarity, emoji, description = random.choices(
            REWARDS,
            weights=[45, 28, 16, 8, 3],
            k=1,
        )[0]
        embed = discord.Embed(title="Caixinha misteriosa", color=discord.Color.gold())
        embed.add_field(name="Raridade", value=f"{emoji} {rarity}", inline=False)
        embed.add_field(name="Conteudo", value=description, inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Caixinha(bot))