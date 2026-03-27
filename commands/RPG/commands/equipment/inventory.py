import discord
from discord.ext import commands
from commands.RPG.utils.database import list_active_inventory
from commands.RPG.game.items.weapons import weapon_dict
from commands.RPG.game.items.armors import armor_dict
from discord import Embed
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='inventory')
    async def inventory(self, ctx):
        """Mostra o inventario."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        data = list_active_inventory(inte.user.id)
        if data == []:
            return await inte.response.send_message("Voce nao possui itens no inventario.")
        
        embed = Embed(title="Inventario", color=discord.Color.blue())
        
        for item in data:
            match item["type"]:
                case 1 :
                    item_dict = weapon_dict
                case 2:
                    item_dict = armor_dict
                    
            item_obj = item_dict[item["item_id"]]()
            item_type = "Arma" if item_obj.type == "weapon" else "Armadura"
            embed.add_field(name=item_obj.name, value=f"Tipo: {item_type}\nRaridade: {item_obj.rarity} | Nivel: {item['level']}\nAtributos: {item_obj.boosts}\nAtaque especial: {item_obj.attack_description}", inline=False)
        
        return await inte.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
