from discord.ext import commands
from commands.RPG.utils.dex import get_dex_embed
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter

class Dex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dex')
    async def dex(self, ctx):
        """Mostra o registro de inimigos encontrados."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        await inte.response.send_message(embed=get_dex_embed(inte.user.id))

async def setup(bot):
    await bot.add_cog(Dex(bot))
