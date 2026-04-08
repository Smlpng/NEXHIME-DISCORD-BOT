import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class DadosNex(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="dados",
        aliases=["apostadados", "duelodados"],
        help="Duelo de dados apostando nex. Ex: !dados 600",
    )
    async def dados(self, ctx: commands.Context, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para o duelo de dados.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva. Ex: !dados 600")

        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            return await inte.response.send_message(
                f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex."
            )

        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta. Tente novamente.")

        player_roll = random.randint(1, 6)
        dealer_roll = random.randint(1, 6)
        payout = 0
        result_text = ""

        if player_roll > dealer_roll:
            multiplier = 2.2 if player_roll == 6 and dealer_roll == 1 else 1.9
            payout = int(round(bet_amount * multiplier))
            update_active_hero_resources(inte.user.id, nex=payout)
            result_text = f"Voce venceu o duelo e recebeu {_format_nex(payout)} nex."
        elif player_roll == dealer_roll:
            payout = bet_amount
            update_active_hero_resources(inte.user.id, nex=payout)
            result_text = "Empate. Sua aposta foi devolvida integralmente."
        else:
            result_text = "O dealer venceu a rodada e ficou com sua aposta."

        updated_hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="ðŸŽ² Duelo de Dados", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Seu dado", value=str(player_roll), inline=True)
        embed.add_field(name="Dealer", value=str(dealer_roll), inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(updated_hero['nex'])} nex", inline=True)
        embed.add_field(name="Resultado", value=result_text, inline=False)
        embed.set_footer(text="6 contra 1 paga bonus maximo. Empate devolve a aposta.")
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DadosNex(bot))