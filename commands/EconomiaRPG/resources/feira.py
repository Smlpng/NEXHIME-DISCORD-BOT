import random
from datetime import date

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


OFFERS = [
    {"name": "Lote de madeira", "cost": 120, "rewards": {"wood": 18}},
    {"name": "Caixa de ferro", "cost": 170, "rewards": {"iron": 12}},
    {"name": "Pacote de runas", "cost": 260, "rewards": {"runes": 3}},
    {"name": "Kit de coleta", "cost": 220, "rewards": {"wood": 10, "iron": 6}},
]


def _daily_offer() -> dict:
    day_seed = date.today().toordinal()
    random.seed(day_seed)
    return random.choice(OFFERS)


class Feira(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="feira", invoke_without_command=True, help="Mostra a oferta rotativa da feira do dia.")
    async def feira(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        offer = _daily_offer()
        rewards_text = ", ".join(f"{value} {key}" for key, value in offer["rewards"].items())
        embed = discord.Embed(title="Feira do dia", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Oferta", value=offer["name"], inline=False)
        embed.add_field(name="Custo", value=f"{offer['cost']} nex", inline=True)
        embed.add_field(name="Recebe", value=rewards_text, inline=True)
        embed.set_footer(text="Use feira comprar para pegar a oferta do dia.")
        await inte.response.send_message(embed=embed)

    @feira.command(name="comprar")
    async def feira_comprar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para comprar na feira.")
        offer = _daily_offer()
        if int(hero.get("nex", 0)) < offer["cost"]:
            return await inte.response.send_message("Voce nao tem nex suficiente para a oferta do dia.")
        success = update_active_hero_resources(inte.user.id, nex=-offer["cost"], **offer["rewards"])
        if not success:
            return await inte.response.send_message("Nao foi possivel concluir a compra da feira.")
        await inte.response.send_message(f"Compra concluida na feira: **{offer['name']}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Feira(bot))