import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import ensure_profile, get_active_hero, has_selected_class


class Rest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="descansar", aliases=["rest"])
    async def descansar(self, ctx):
        """Explica como o descanso funciona no RPG atual."""
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        hero = get_active_hero(inte.user.id)

        embed = discord.Embed(title="Descanso", color=discord.Color.blue())

        if hero is None:
            embed.description = "Seu perfil ainda esta sendo preparado."
            return await inte.response.send_message(embed=embed, ephemeral=True)

        if has_selected_class(inte.user.id):
            embed.description = (
                "No sistema atual, vida e mana nao ficam persistidas entre combates. "
                "Seu heroi ja entra pronto para a proxima luta, entao descansar nao precisa aplicar cooldown ou recuperar energia."
            )
            embed.add_field(name="Proximo passo", value="Use fight, dungeon, raid ou pvp quando quiser continuar.", inline=False)
        else:
            embed.description = (
                "Seu heroi ainda nao escolheu uma classe, mas o descanso tambem nao e necessario no sistema atual. "
                "Primeiro escolha a classe quando quiser pelo menu do heroi."
            )
            embed.add_field(name="Dica", value="Abra menu para ver o perfil e definir classe, raÃ§a ou tribo quando quiser.", inline=False)

        await inte.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Rest(bot))