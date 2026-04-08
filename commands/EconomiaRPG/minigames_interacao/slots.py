import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


SLOT_SYMBOLS = ["ðŸ’", "ðŸ‹", "ðŸ””", "ðŸ€", "ðŸ’Ž", "7ï¸âƒ£"]


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _calculate_multiplier(reels: list[str]) -> float:
    counts: dict[str, int] = {}
    for symbol in reels:
        counts[symbol] = counts.get(symbol, 0) + 1

    highest = max(counts.values())
    top_symbol = max(counts, key=counts.get)

    if highest == 3 and top_symbol == "7ï¸âƒ£":
        return 8.0
    if highest == 3 and top_symbol == "ðŸ’Ž":
        return 5.5
    if highest == 3:
        return 3.5
    if highest == 2 and "7ï¸âƒ£" in counts:
        return 1.8
    if highest == 2:
        return 1.4
    return 0.0


class Slots(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="slots",
        aliases=["slot", "cacaniqueis", "cacaniquel"],
        help="Gira uma maquina caÃ§a-niqueis apostando nex. Ex: !slots 500",
    )
    async def slots(self, ctx: commands.Context, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para usar os slots.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva. Ex: !slots 500")

        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            return await inte.response.send_message(
                f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex."
            )

        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta. Tente novamente.")

        reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        multiplier = _calculate_multiplier(reels)
        payout = int(round(bet_amount * multiplier)) if multiplier > 0 else 0

        if payout > 0:
            update_active_hero_resources(inte.user.id, nex=payout)

        updated_hero = get_active_hero(inte.user.id)
        profit = payout - bet_amount

        embed = discord.Embed(title="ðŸŽ° Slots", color=RPG_PRIMARY_COLOR)
        embed.description = " | ".join(reels)
        embed.add_field(name="Aposta", value=f"{_format_nex(bet_amount)} nex", inline=True)
        embed.add_field(name="Multiplicador", value=f"{multiplier:.2f}x", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(updated_hero['nex'])} nex", inline=True)

        if payout > 0:
            embed.add_field(
                name="Resultado",
                value=f"Voce ganhou {_format_nex(payout)} nex ({profit:+,} nex).".replace(",", "."),
                inline=False,
            )
        else:
            embed.add_field(name="Resultado", value="A casa levou sua aposta desta vez.", inline=False)

        embed.set_footer(text="3 iguais pagam mais. Dois simbolos iguais ainda rendem premio menor.")
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Slots(bot))