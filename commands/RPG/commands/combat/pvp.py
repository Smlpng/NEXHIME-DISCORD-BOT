from discord import Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
from commands.RPG.utils.hero_actions import load_hero
from commands.RPG.utils.game_loop.fight import NewFight
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter


class Pvp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pvp')
    async def pvp(self, ctx):
        """Inicia um combate PVP."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        view = View()
        
        embed = Embed(title="PVP", description=f"{inte.user.name} esta desafiando alguem para uma batalha", color=0x3498db)
        embed.add_field(name="Como jogar", value="Clique no botao Aceitar")
        
        play_button = Button(label="Aceitar", style=ButtonStyle.primary)
        play_button.callback = lambda i, player_name=inte.user.name, player_id=inte.user.id, player_inte = inte : self.load_players(i, player_name, player_id, player_inte)
        view.add_item(play_button)  
        
        
        await inte.response.send_message(embed=embed, view=view)
        self.message = await inte.original_response()
        
        
    async def load_players(self, inte, player_name, player_id, player_inte):
        if inte.user.id == player_id:
            return 
        
        if not await hero_created(inte):
            return
        
        users_data = [
            (player_id, load_hero(player_id, name=player_name), player_inte),
            (inte.user.id, load_hero(inte.user.id, name=inte.user.name), inte)
        ]
        
        await self.message.delete()
        
        await NewFight(inte).pvp_fight(users_data)

async def setup(bot):
    await bot.add_cog(Pvp(bot))
