from discord.ext import commands
from discord import app_commands, ButtonStyle, Embed
from discord.ui import View, Button
from commands.RPG.utils.database import get_active_hero, list_active_clean_inventory
from commands.RPG.game.items.weapons import weapon_dict
from commands.RPG.game.items.armors import armor_dict
from commands.RPG.utils.equipment_upgrade import equipment_upgrade_cost, make_upgrade
from commands.RPG.utils.hero_check import hero_created
from commands.RPG.utils.command_adapter import CommandContextAdapter


class Forge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page = 0
        self.message = None
        self.image = "https://cdn.discordapp.com/attachments/474702643625984021/1253102100645416960/forja.jpeg?ex=6674a1c6&is=66735046&hm=f19475fa6c33f9433842236160c5c77cd6adfb0cc26399b2e6f6c5ed0d804f53&"

    @commands.hybrid_command(name='forge')
    async def forge(self, ctx):
        """Melhora equipamentos na forja."""
        inte = CommandContextAdapter(ctx)
        if not await hero_created(inte):
            return
        
        await self.create_clean_start_message(inte)
        
    def create_start_embed(self, page):
        embed = Embed(title="Forja", description="Selecione um item para melhorar", color=0x3498db)
        embed.set_image(url=self.image)
        for i, item in enumerate(page):
            if item['type'] == "armor":
                dict = armor_dict
            elif item["type"] == "weapon":
                dict = weapon_dict
            embed.add_field(name=f"{i+1} {dict[item['item_id']]().name}", value=f"Nivel: {item['level']}")
        return embed
    
    def create_upgrade_embed(self, inte, cost, user_data, item, name):
        embed = Embed(title="Forja", description="Melhoria", color=0x3498db)
        embed.set_image(url=self.image)
    
        embed.add_field(name=name, value=f"Nivel: {item['level']}", inline=False)
        embed.add_field(name="Custo", value="", inline=False)
        embed.add_field(name="Ouro 💰", value=cost[0], inline=True)
        embed.add_field(name="Madeira 🌲", value=cost[1], inline=True)
        embed.add_field(name="Ferro ⛏️", value=cost[2], inline=True)
        embed.add_field(name="Runas 🧿", value=cost[3], inline=True)
        embed.add_field(name="Inventario", value="", inline=False)
        embed.add_field(name="Ouro 💰", value=user_data["gold"], inline=True)
        embed.add_field(name="Madeira 🌲", value=user_data["wood"], inline=True)
        embed.add_field(name="Ferro ⛏️", value=user_data["iron"], inline=True)
        embed.add_field(name="Runas 🧿", value=user_data["runes"], inline=True)
        
            
        return embed

    async def back(self, interaction, inte):
        if interaction.user.id != inte.user.id:
            return
        if self.page >= 1:
            self.page -= 1
            await self.create_start_message(self.pages[self.page], inte)
        await interaction.response.defer()

    async def forward(self, interaction, inte):
        if interaction.user.id != inte.user.id:
            return
        if len(self.pages) > self.page + 1:
            self.page += 1
            await self.create_start_message(self.pages[self.page], inte)
        await interaction.response.defer()
        
    async def upgrade_item(self, interaction, item, user_id, item_dict, inte):
        if interaction.user.id != inte.user.id:
            return
        make_upgrade(user_id, item)
        data = list_active_clean_inventory(inte.user.id, item_dict["type"], item_dict["item_id"])[0]
        await self.create_upgrade_message(interaction, inte, data)
        await interaction.response.defer()

    async def create_clean_start_message(self, inte, interaction=None):
        if interaction:
            if interaction.user.id != inte.user.id:
                return
        self.page = 0
        PER_PAGE = 5
        data = list_active_clean_inventory(inte.user.id)
        if data == []:
            self.pages = [[]]
        else:
            self.pages = [data[i:i + PER_PAGE] for i in range(0, len(data), PER_PAGE)]

        await self.create_start_message(self.pages[0], inte)
        if interaction:
            await interaction.response.defer()
        

    async def create_start_message(self, page, inte):
        view = View()  # Create a new view every time to reset buttons
        embed = self.create_start_embed(page)

        button_back = Button(label="<<", style=ButtonStyle.primary)
        button_back.callback = lambda i, inte=inte : self.back(i, inte)
        view.add_item(button_back)
        
        # Create item buttons
        for i, item in enumerate(page):
            button = Button(label=f"{i+1}", style=ButtonStyle.primary)
            button.callback = lambda interaction=i, inte=inte, item=item: self.create_upgrade_message(interaction,inte, item)
            view.add_item(button)
            
        button_forward = Button(label=">>", style=ButtonStyle.primary)
        button_forward.callback = lambda i, inte=inte : self.forward(i, inte)
        view.add_item(button_forward)

        if self.message:
            await self.message.edit(embed=embed, view=view)
        else:
            await inte.response.send_message(embed=embed, view=view)
            self.message = await inte.original_response()
            
            
    async def create_upgrade_message(self, interaction, inte, item):
        if interaction.user.id != inte.user.id:
            return
        view = View()
        
        # Checks valid level
        if item['type'] == "armor":
            dict = armor_dict
        elif item["type"] == "weapon":
            dict = weapon_dict
        item_object = dict[item['item_id']]()
        
        user_data = get_active_hero(inte.user.id)
        
        if cost := equipment_upgrade_cost(item["level"], item_object.rarity):
            embed = self.create_upgrade_embed(inte, cost, user_data, item, item_object.name)
        else:
            embed = Embed(title="Forja", description="Melhoria", color=0x3498db)
            embed.set_image(url=self.image)
            embed.add_field(name=f"{item_object.name} ja esta no nivel maximo", value="", inline=False)
        
        
        
        
        
        button_back = Button(label="Voltar", style=ButtonStyle.primary)
        button_back.callback = lambda i, inte=inte : self.create_clean_start_message(inte, interaction=i)
        view.add_item(button_back)
        if cost:
            if user_data["gold"] >= cost[0] and user_data["wood"] >= cost[1] and user_data["iron"] >= cost[2] and user_data["runes"] >= cost[3]:
                upgrade_button = Button(label="Melhorar", style=ButtonStyle.primary)
                upgrade_button.callback = lambda i, item_object=item_object, user_id=inte.user.id, item_dict=item, inte=inte:self.upgrade_item(i, item_object, user_id, item_dict, inte)
                view.add_item(upgrade_button)
            else:
                embed.add_field(name="Recursos insuficientes", value="", inline=False)
            
            
        await self.message.edit(embed=embed, view=view)
    
        

async def setup(bot):
    await bot.add_cog(Forge(bot))
