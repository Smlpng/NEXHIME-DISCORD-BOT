from discord.ext import commands
from commands.EconomiaRPG.zones.zones.embeds import get_zone_full_embed
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter

class Zone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='zone')
    async def zone(self, ctx):
        """Mostra informacoes da zona atual."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        await inte.response.send_message(embed=get_zone_full_embed(inte.user.id))

async def setup(bot):
    await bot.add_cog(Zone(bot))
