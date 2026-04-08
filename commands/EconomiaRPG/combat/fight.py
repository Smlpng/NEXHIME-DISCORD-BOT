from discord.ext import commands
from commands.EconomiaRPG.utils.game_loop.fight import NewFight
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.zones.zones.encounters import get_enemy_from_zone
from commands.EconomiaRPG.utils.hero_actions import load_hero
from commands.EconomiaRPG.utils.querys import get_zone
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter

class Fight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='fight')
    async def fight(self, ctx):
        """Inicia uma batalha na zona atual."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return


        zone_id = get_zone(inte.user.id)
        
        user = load_hero(inte.user.id, name=inte.user.name)
        enemy = get_enemy_from_zone(zone_id)
        
        await inte.response.send_message("Carregando...")
        
        await NewFight(inte).fight(user,enemy)

async def setup(bot):
    await bot.add_cog(Fight(bot))
