from discord import app_commands, SelectOption
from discord.ui import Select, View
from discord.ext import commands
from commands.RPG.utils.database import equip_item, list_active_inventory
from commands.RPG.game.items.weapons import weapon_dict
from commands.RPG.game.items.armors import armor_dict
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter

class Equip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='equip_weapon')
    async def equip_weapon(self, ctx):
        """Equipa uma arma."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        class Dropdown(Select):
            def __init__(self, data):

                options = []
                
                for item in data:
                    item_obj = weapon_dict[item["item_id"]]()
                    options.append(SelectOption(value=item["item_id"] ,label=item_obj.name, description=f"Id: {item_obj.id} | Nivel: {item['level']}", emoji='🟦'))
                
                super().__init__(placeholder='Escolha um item para equipar', min_values=1, max_values=1, options=options)

            async def callback(self, interaction):
                if interaction.user.id != inte.user.id:
                    return
                equip_item(inte.user.id, "weapon", int(self.values[0]))
                await interaction.response.send_message("Equipado com sucesso.")

            data = list_active_inventory(inte.user.id, item_type_id=1)

        if data == []:
            return await inte.response.send_message("Voce nao possui armas para equipar.")

        view = View()
        view.add_item(Dropdown(data))

        await inte.response.send_message('Selecione um equipamento para equipar:', view=view, ephemeral=True)
        
        
        
    @commands.hybrid_command(name='equip_armor')
    async def equip_armor(self, ctx):
        """Equipa uma armadura."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        class Dropdown(Select):
            def __init__(self, data):

                options = []
                
                
                
                for item in data:
                    item_obj = armor_dict[item["item_id"]]()
                    options.append(SelectOption(value=item["item_id"] ,label=item_obj.name, description=f"Id: {item_obj.id} | Nivel: {item['level']}", emoji='🟦'))
                
                super().__init__(placeholder='Escolha um item para equipar', min_values=1, max_values=1, options=options)

            async def callback(self, interaction):
                if interaction.user.id != inte.user.id:
                    return
                equip_item(inte.user.id, "armor", int(self.values[0]))
                await interaction.response.send_message("Equipado com sucesso.")

            data = list_active_inventory(inte.user.id, item_type_id=2)

        if data == []:
            return await inte.response.send_message("Voce nao possui armaduras para equipar.")

        # Crear la vista que muestra el Select
        view = View()
        view.add_item(Dropdown(data))

        # Enviar el mensaje con el Select
        await inte.response.send_message('Selecione um equipamento para equipar:', view=view, ephemeral=True)



    

async def setup(bot):
    await bot.add_cog(Equip(bot))
