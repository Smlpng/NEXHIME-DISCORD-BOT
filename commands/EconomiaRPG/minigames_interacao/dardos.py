import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class Dardos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dardos", aliases=["dart"], help="Arremesse tres dardos e tente multiplicar a aposta.")
    async def dardos(self, ctx: commands.Context, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para jogar dardos.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva.")
        if int(hero.get("nex", 0)) < bet_amount:
            return await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(hero['nex'])} nex.")
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta.")

        throws = [random.randint(5, 50) for _ in range(3)]
        total = sum(throws)
        if total >= 120:
            multiplier = 2.8
        elif total >= 90:
            multiplier = 1.9
        elif total >= 70:
            multiplier = 1.2
        else:
            multiplier = 0

        payout = int(round(bet_amount * multiplier)) if multiplier > 0 else 0
        if payout > 0:
            update_active_hero_resources(inte.user.id, nex=payout)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="🎯 Dardos", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Arremessos", value=", ".join(str(value) for value in throws), inline=False)
        embed.add_field(name="Pontuacao", value=str(total), inline=True)
        embed.add_field(name="Multiplicador", value=f"{multiplier:.2f}x", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(hero['nex'])} nex", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Dardos(bot))