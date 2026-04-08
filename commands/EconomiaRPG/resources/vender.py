import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


SELL_PRICES = {
    "wood": 8,
    "madeira": 8,
    "iron": 14,
    "ferro": 14,
    "runes": 65,
    "runas": 65,
}

RESOURCE_MAP = {
    "wood": "wood",
    "madeira": "wood",
    "iron": "iron",
    "ferro": "iron",
    "runes": "runes",
    "runas": "runes",
}


class Vender(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="vender", aliases=["sell"], help="Vende recursos. Ex: !vender madeira 5")
    async def vender(self, ctx: commands.Context, recurso: str, quantidade: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa ter um heroi ativo para vender recursos.")
        if quantidade <= 0:
            return await inte.response.send_message("A quantidade precisa ser maior que zero.")

        resource_key = RESOURCE_MAP.get(recurso.lower())
        if resource_key is None:
            return await inte.response.send_message("Voce pode vender madeira, ferro ou runas.")
        if int(hero.get(resource_key, 0)) < quantidade:
            return await inte.response.send_message("Voce nao tem essa quantidade para vender.")

        total = quantidade * SELL_PRICES[recurso.lower()]
        success = update_active_hero_resources(inte.user.id, nex=total, **{resource_key: -quantidade})
        if not success:
            return await inte.response.send_message("Nao foi possivel concluir a venda.")

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="Venda concluida", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Recurso", value=recurso.title(), inline=True)
        embed.add_field(name="Quantidade", value=str(quantidade), inline=True)
        embed.add_field(name="Recebido", value=f"{total} nex", inline=True)
        embed.add_field(name="Carteira", value=f"{hero['nex']} nex", inline=False)
        await inte.response.send_message(embed=embed)

    @commands.command(name="venderall", aliases=["sellall"], help="Vende toda a madeira e ferro do heroi ativo.")
    async def venderall(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa ter um heroi ativo para vender recursos.")

        wood = int(hero.get("wood", 0))
        iron = int(hero.get("iron", 0))
        runes = int(hero.get("runes", 0))
        if wood <= 0 and iron <= 0 and runes <= 0:
            return await inte.response.send_message("Voce nao tem recursos para vender agora.")

        total = wood * SELL_PRICES["wood"] + iron * SELL_PRICES["iron"] + runes * SELL_PRICES["runes"]
        success = update_active_hero_resources(inte.user.id, nex=total, wood=-wood, iron=-iron, runes=-runes)
        if not success:
            return await inte.response.send_message("Nao foi possivel concluir a venda em lote.")

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="Venda em lote", color=RPG_PRIMARY_COLOR)
        embed.description = f"Tudo foi vendido por **{total} nex**."
        embed.add_field(name="Madeira", value=str(wood), inline=True)
        embed.add_field(name="Ferro", value=str(iron), inline=True)
        embed.add_field(name="Runas", value=str(runes), inline=True)
        embed.add_field(name="Carteira", value=f"{hero['nex']} nex", inline=False)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Vender(bot))