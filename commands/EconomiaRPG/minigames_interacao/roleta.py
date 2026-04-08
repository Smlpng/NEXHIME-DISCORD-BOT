import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


ROULETTE_COLORS = {
    0: "verde",
    1: "vermelho",
    2: "preto",
    3: "vermelho",
    4: "preto",
    5: "vermelho",
    6: "preto",
    7: "vermelho",
    8: "preto",
    9: "vermelho",
    10: "preto",
    11: "preto",
    12: "vermelho",
}


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class Roleta(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="roleta", aliases=["roulette"], help="Aposte numa cor ou numero. Ex: !roleta 500 vermelho")
    async def roleta(self, ctx: commands.Context, bet_amount: int, *, aposta: str):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para usar a roleta.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva. Ex: !roleta 500 vermelho")

        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            return await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex.")
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta.")

        aposta_normalizada = aposta.strip().lower()
        result_number = random.randint(0, 12)
        result_color = ROULETTE_COLORS[result_number]
        payout = 0
        result_text = ""

        if aposta_normalizada.isdigit():
            guessed_number = int(aposta_normalizada)
            if guessed_number == result_number:
                payout = bet_amount * 10
                result_text = f"Acerto total no numero {result_number}."
        elif aposta_normalizada in {"vermelho", "preto", "verde"}:
            if aposta_normalizada == result_color:
                payout = bet_amount * (12 if result_color == "verde" else 2)
                result_text = f"A cor sorteada foi {result_color}."
        else:
            update_active_hero_resources(inte.user.id, nex=bet_amount)
            return await inte.response.send_message("Aposta invalida. Use vermelho, preto, verde ou um numero de 0 a 12.")

        if payout > 0:
            update_active_hero_resources(inte.user.id, nex=payout)
        else:
            result_text = f"A roleta caiu em {result_number} ({result_color})."

        updated_hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="🎡 Roleta", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Resultado", value=f"{result_number} ({result_color})", inline=True)
        embed.add_field(name="Aposta", value=f"{_format_nex(bet_amount)} nex em {aposta_normalizada}", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(updated_hero['nex'])} nex", inline=True)
        embed.add_field(name="Resumo", value=result_text if payout == 0 else f"{result_text} Premio: {_format_nex(payout)} nex.", inline=False)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roleta(bot))