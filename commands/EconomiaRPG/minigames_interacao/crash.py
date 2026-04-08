import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class Crash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="crash", help="Aposte num multiplicador alvo. Ex: !crash 500 2.0")
    async def crash(self, ctx: commands.Context, bet_amount: int, cashout_multiplier: float):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para jogar crash.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva.")
        if cashout_multiplier < 1.1 or cashout_multiplier > 10:
            return await inte.response.send_message("Escolha um multiplicador entre 1.1x e 10x.")
        if int(hero.get("nex", 0)) < bet_amount:
            return await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(hero['nex'])} nex.")
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta.")

        crash_point = round(random.uniform(1.0, 6.0), 2)
        payout = 0
        result_text = ""
        if crash_point >= cashout_multiplier:
            payout = int(round(bet_amount * cashout_multiplier))
            update_active_hero_resources(inte.user.id, nex=payout)
            result_text = "Voce conseguiu sacar antes da queda."
        else:
            result_text = "O grafico explodiu antes do seu saque."

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="📈 Crash", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Seu alvo", value=f"{cashout_multiplier:.2f}x", inline=True)
        embed.add_field(name="Crash real", value=f"{crash_point:.2f}x", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(hero['nex'])} nex", inline=True)
        embed.add_field(name="Resultado", value=result_text, inline=False)
        if payout > 0:
            embed.add_field(name="Premio", value=f"{_format_nex(payout)} nex", inline=False)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Crash(bot))