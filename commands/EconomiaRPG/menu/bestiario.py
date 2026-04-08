import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import count_enemies_in_zone, get_active_zone_id, list_seen_enemies_by_zone
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR, build_progress_bar, resolve_zone_name


class Bestiario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bestiario", aliases=["bestiary", "dexzona"])
    async def bestiario(self, ctx, zona: int | None = None):
        """Mostra os inimigos ja vistos na zona atual ou em uma zona especifica."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return

        zone_id = zona if zona is not None else get_active_zone_id(inte.user.id)
        if zone_id is None:
            return await inte.response.send_message("Nao foi possivel identificar a zona do seu heroi.")

        seen = list_seen_enemies_by_zone(inte.user.id, zone_id)
        total = count_enemies_in_zone(zone_id)
        embed = discord.Embed(title=f"Bestiario - {resolve_zone_name(zone_id)}", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Progresso", value=f"{len(seen)}/{total}\n{build_progress_bar(len(seen), total)}", inline=False)
        if seen:
            lines = [f"- {enemy['name']}" for enemy in seen[:20]]
            embed.add_field(name="Criaturas vistas", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="Criaturas vistas", value="Nenhum inimigo registrado nessa zona ainda.", inline=False)
        embed.set_footer(text="Use fight, explorar e dungeon para encontrar novas criaturas.")
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Bestiario(bot))