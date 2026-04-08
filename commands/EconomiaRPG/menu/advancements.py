from discord import Embed, Color
from discord.ext import commands
from commands.EconomiaRPG.utils.database import get_advancements
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter

class Advancements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='advancements')
    async def advancements(self, ctx):
        """Mostra o progresso do heroi."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        def create_bar(progress: int, total: int) -> str:
            percent = progress / total
            filled_length = int(40 * percent)
            bar = 'â–ˆ' * filled_length + '-' * (40 - filled_length)
            
            return f'`[{bar}]`'
        
        data = get_advancements(inte.user.id)
        
        
        embed = Embed(title=f"Progresso de {inte.user.name}", color=Color.blue())
        embed.add_field(name=f'Derrote 100 monstros ({data["kills"]}/100)', value=create_bar(data["kills"],100), inline=False)
        embed.add_field(name=f'Melhore equipamentos 30 vezes ({data["upgrades"]}/30)', value=create_bar(data["upgrades"], 30), inline=False)
        embed.add_field(name=f'Gaste 100.000 nex ({data["nex_spent"]}/100000)', value=create_bar(data["nex_spent"], 100000), inline=False)
        
        await inte.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Advancements(bot))
