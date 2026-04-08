import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


CARD_VALUES = list(range(1, 14))
CARD_LABELS = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K",
}


def _card_label(value: int) -> str:
    return CARD_LABELS.get(value, str(value))


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class HighLow(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="highlow", aliases=["maioroumenor"], help="Adivinhe se a proxima carta sera maior ou menor. Ex: !highlow 500 maior")
    async def highlow(self, ctx: commands.Context, bet_amount: int, palpite: str):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para jogar highlow.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva. Ex: !highlow 500 maior")

        guess = palpite.strip().lower()
        if guess not in {"maior", "menor"}:
            return await inte.response.send_message("Use `maior` ou `menor` como palpite.")

        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            return await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex.")
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta.")

        first_card = random.choice(CARD_VALUES)
        second_card = random.choice(CARD_VALUES)

        if second_card == first_card:
            payout = bet_amount
            result_text = "Empate de cartas. Sua aposta foi devolvida."
        else:
            is_higher = second_card > first_card
            win = (guess == "maior" and is_higher) or (guess == "menor" and not is_higher)
            payout = int(round(bet_amount * 1.9)) if win else 0
            result_text = "Voce acertou o movimento da proxima carta." if win else "A carta virou contra o seu palpite."

        if payout > 0:
            update_active_hero_resources(inte.user.id, nex=payout)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="🃏 High Low", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Carta inicial", value=_card_label(first_card), inline=True)
        embed.add_field(name="Proxima carta", value=_card_label(second_card), inline=True)
        embed.add_field(name="Palpite", value=guess.title(), inline=True)
        embed.add_field(name="Resultado", value=result_text, inline=False)
        embed.add_field(name="Carteira", value=f"{_format_nex(hero['nex'])} nex", inline=True)
        if payout > 0:
            embed.add_field(name="Premio", value=f"{_format_nex(payout)} nex", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HighLow(bot))