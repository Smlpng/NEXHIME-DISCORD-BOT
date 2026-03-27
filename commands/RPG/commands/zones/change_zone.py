from discord import app_commands, SelectOption
from discord.ext import commands
from discord.ui import View, Select
from commands.RPG.game.zones.embeds import get_zone_embed
from commands.RPG.utils.database import get_active_zone_id, set_active_zone_id
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.hero_actions import load_hero
from commands.RPG.utils.command_adapter import CommandContextAdapter

class ChangeZone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='change_zone')
    async def change_zone(self, ctx):
        """Troca a zona atual do mapa."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        hero = load_hero(inte.user.id)
        
        class Dropdown(Select):
            def __init__(self):
                
                options = [
                    SelectOption(value=1, label="Clareira dos Sussurros", emoji='🏕️')
                ]
                
                if hero.level >= 10:
                    options.append(SelectOption(value=2, label="Ruinas Cobertas de Musgo", emoji='⛓️'))
                    if hero.level >= 20:
                        options.append(SelectOption(value=3, label="Rio das Presas", emoji='🌲'))
                        if hero.level >= 25:
                            options.append(SelectOption(value=4, label="Caverna do Eco Profundo", emoji='🏜️'))
                            if hero.level >= 35:
                                options.append(SelectOption(value=5, label="Ninho da Arvore-Mae", emoji='🐸'))
                            else:
                                options.append(SelectOption(value=0, label="Uma nova zona sera liberada no nivel 35", emoji='🔒'))
                        else:
                            options.append(SelectOption(value=0, label="Uma nova zona sera liberada no nivel 25", emoji='🔒'))
                    else:
                        options.append(SelectOption(value=0, label="Uma nova zona sera liberada no nivel 20", emoji='🔒'))
                else:
                    options.append(SelectOption(value=0, label="Uma nova zona sera liberada no nivel 10", emoji='🔒'))
                    
                super().__init__(placeholder='Selecione uma zona', min_values=1, max_values=1, options=options)
        
        
            async def callback(self, interaction):
                if interaction.user.id != inte.user.id:
                    return
                zone_id = int(self.values[0])
                if zone_id == 0:
                    return await interaction.response.defer()
                message = await inte.original_response()
                await message.edit(embed=get_zone_embed(zone_id))
                set_active_zone_id(inte.user.id, zone_id)
                await interaction.response.defer()
              
        
        data = {"zone_id": get_active_zone_id(inte.user.id)}
                
                
        view = View()
        view.add_item(Dropdown())

        

        await inte.response.send_message('Selecione a zona para onde deseja ir:', view=view, embed=get_zone_embed(data["zone_id"]))

async def setup(bot):
    await bot.add_cog(ChangeZone(bot))
