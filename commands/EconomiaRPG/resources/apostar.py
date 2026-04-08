import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


class Apostar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="apostar", aliases=["bet"], help="Mostra os minigames de aposta disponiveis no RPG.")
    async def apostar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        embed = discord.Embed(title="Mesa de Apostas", color=RPG_PRIMARY_COLOR)
        embed.description = (
            "Use um dos jogos abaixo com sua aposta:\n"
            "- mines\n"
            "- blackjack\n"
            "- slots\n"
            "- raspadinha\n"
            "- dados\n"
            "- torre\n"
            "- roleta\n"
            "- highlow\n"
            "- crash\n"
            "- parouimpar"
        )
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Apostar(bot))