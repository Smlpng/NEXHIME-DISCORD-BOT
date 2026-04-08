from discord import Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
from commands.EconomiaRPG.utils.hero_actions import load_hero
from commands.EconomiaRPG.utils.game_loop.fight import NewFight
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.zones.zones.encounters import get_dungeon_from_zone, get_dungeon_loot_from_zone
from commands.EconomiaRPG.utils.querys import get_zone
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dungeon')
    async def dungeon(self, ctx, cooperative: int = 2):
        """Inicia uma dungeon."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        
        if cooperative == 1:
            view = View()
            
            embed = Embed(title="Dungeon", description="Entrar na dungeon", color=0x3498db)
            embed.add_field(name="Como jogar", value="Clique no botao Entrar")
            
            play_button = Button(label="Entrar", style=ButtonStyle.primary)
            play_button.callback = lambda i, player_name=inte.user.name, player_id=inte.user.id, player_inte = inte : self.load_players(i, player_name, player_id, player_inte)
            view.add_item(play_button)  
            
            await inte.response.send_message(embed=embed, view=view)
    
        elif cooperative == 2:
            hero = load_hero(inte.user.id, name=inte.user.name)
            if hero.level < 5:
                return await inte.response.send_message("E necessario estar no nivel 5 para entrar em uma dungeon.")
            await inte.response.send_message("Carregando...")
            zone_id = get_zone(inte.user.id)
            enemies = get_dungeon_from_zone(zone_id)
            loot = get_dungeon_loot_from_zone(zone_id)
            await NewFight(inte).consecutive_fight(hero, enemies, bonus=loot)
            
            
            
    async def load_players(self, inte, player_name, player_id, player_inte):
        if inte.user.id == player_id:
            return 
        
        if not await hero_created(inte):
            return
        
        hero = load_hero(inte.user.id, name=inte.user.name)
        if hero.level < 5:
            return await inte.response.send_message("E necessario estar no nivel 5 para entrar em uma dungeon.", ephemeral=True)
        
        zone_id = get_zone(player_id)
        bonus = 1.75
        if zone_id == 1:
            bonus = 3
        
        users_data = [
            (inte.user.id, hero, inte), # Places switched because in Fight turns change order, and first user should be the first to attack.
            (player_id, load_hero(player_id, name=player_name), player_inte)
        ]
        
        original_message = await player_inte.original_response()
        await original_message.delete()
        await inte.response.send_message("Carregando...")
        
        enemies = get_dungeon_from_zone(zone_id, bonus=bonus)
        loot = get_dungeon_loot_from_zone(zone_id)
        await NewFight(inte).consecutive_multi_fight(users_data, enemies, bonus=loot)
        
        
    

async def setup(bot):
    await bot.add_cog(Dungeon(bot))
