import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, get_bank_balance
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


class Bolsa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bolsa", aliases=["wallet", "carteira"], help="Resumo rapido da sua economia e recursos do RPG.")
    async def bolsa(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa ter um heroi ativo para abrir a bolsa.")

        bank = get_bank_balance(inte.user.id)
        embed = discord.Embed(title=f"Bolsa de {inte.user.display_name}", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Carteira", value=f"{hero['nex']} nex", inline=True)
        embed.add_field(name="Banco", value=f"{bank} nex", inline=True)
        embed.add_field(name="Total", value=f"{hero['nex'] + bank} nex", inline=True)
        embed.add_field(name="Madeira", value=str(hero["wood"]), inline=True)
        embed.add_field(name="Ferro", value=str(hero["iron"]), inline=True)
        embed.add_field(name="Runas", value=str(hero["runes"]), inline=True)
        embed.add_field(name="Tomates", value=f"{hero['tomato']}/{hero['tomato_capacity']}", inline=True)
        embed.add_field(name="Flores", value=f"{hero['flower']}/{hero['flower_capacity']}", inline=True)
        embed.add_field(name="Zona", value=str(hero.get("zone_id", "?")), inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bolsa(bot))