from discord.ext import commands
from commands.RPG.utils.game_loop.fight import NewFight
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.game.zones.encounters import get_enemy_from_zone
from commands.RPG.utils.hero_actions import load_hero
from commands.RPG.utils.querys import get_zone
from commands.RPG.utils.command_adapter import CommandContextAdapter

class Fight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='fight')
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
