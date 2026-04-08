from discord import Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
from commands.EconomiaRPG.utils.hero_actions import load_hero
from commands.EconomiaRPG.utils.game_loop.fight import NewFight
from commands.EconomiaRPG.zones.zones.encounters import get_enemy_from_zone
from commands.EconomiaRPG.utils.querys import get_zone
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter

class Raid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='raid')
    async def raid(self, ctx):
        """Enfrente um inimigo poderoso em grupo."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        hero = load_hero(inte.user.id)
        if hero.level < 10:
            return await inte.response.send_message("E necessario estar no nivel 10 para entrar em uma raid.")
        
        view = View()
        
        embed = Embed(title="Raid", description="Batalha de raid", color=0x3498db)
        embed.add_field(name="Como jogar", value="Clique no botao Entrar")
        
        play_button = Button(label="Entrar", style=ButtonStyle.primary)
        play_button.callback = lambda i, player_name=inte.user.name, player_id=inte.user.id, player_inte = inte : self.load_players(i, player_name, player_id, player_inte)
        view.add_item(play_button)  
        
        
        await inte.response.send_message(embed=embed, view=view)
        
    
    async def load_players(self, inte, player_name, player_id, player_inte):
        if inte.user.id == player_id:
            return 
        
        if not await hero_created(inte):
            return
        
        hero = load_hero(inte.user.id, name=inte.user.name)
        if hero.level < 10:
            return await inte.response.send_message("E necessario estar no nivel 10 para entrar em uma raid.", ephemeral=True)
        
        zone = get_zone(player_id)
        bonus = 1.75
        if zone == 1:
            bonus = 3
        
        users_data = [
            (player_id, load_hero(player_id, name=player_name), player_inte),
            (inte.user.id, hero, inte)
        ]
        
        original_message = await player_inte.original_response()
        await original_message.delete()
        await inte.response.send_message("Carregando...")
        
        await NewFight(inte).multi_fight(users_data, get_enemy_from_zone(zone, bonus=bonus))

async def setup(bot):
    await bot.add_cog(Raid(bot))
