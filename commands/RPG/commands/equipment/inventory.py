import discord
from discord.ext import commands
from commands.RPG.utils.database import get_active_hero, list_active_inventory
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.presentation import build_inventory_embed

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='inventory', aliases=['inventario'])
    async def inventory(self, ctx):
        """Mostra o inventario."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        data = list_active_inventory(inte.user.id)
        hero_data = get_active_hero(inte.user.id)
        embed = build_inventory_embed(inte.user.display_name, data, hero_data)
        embed.set_footer(text="Itens marcados como equipados já estão ativos no seu herói.")
        return await inte.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
