import discord
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import clear_active_hero_class, ensure_profile, has_selected_class, update_active_hero_resources
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR


RESPEC_COST_NEX = 150


class ResetClasse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="reset_classe",
        aliases=["respec"],
        help="Reseta sua classe no RPG (permite escolher novamente).",
    )
    async def reset_classe(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        if not has_selected_class(inte.user.id):
            return await inte.response.send_message("Você ainda não escolheu uma classe.")

        if RESPEC_COST_NEX > 0:
            ok = update_active_hero_resources(inte.user.id, nex=-RESPEC_COST_NEX)
            if not ok:
                return await inte.response.send_message(
                    f"Você precisa de **{RESPEC_COST_NEX} nex** para resetar sua classe.",
                    ephemeral=True,
                )

        clear_active_hero_class(inte.user.id)
        embed = discord.Embed(title="🔄 Classe resetada", color=RPG_PRIMARY_COLOR)
        embed.description = (
            f"Sua classe foi removida.\n"
            f"Use `escolher_classe` para escolher novamente."
        )
        if RESPEC_COST_NEX > 0:
            embed.add_field(name="Custo", value=f"{RESPEC_COST_NEX} nex", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ResetClasse(bot))
