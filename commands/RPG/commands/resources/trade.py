from discord import app_commands, Embed, Color, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
from commands.RPG.utils.database import get_active_hero, update_active_hero_resources
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.command_adapter import CommandContextAdapter

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.resource_emojis = {
            1: '🌲',  # Wood
            2: '⛏️',  # Iron
            3: '🏆'   # Gold
        }

        self.resource_names = {
            1: 'Madeira',
            2: 'Ferro',
            3: 'Ouro'
        }

    @commands.hybrid_command(name='trade')
    @app_commands.choices(
        give=[
            app_commands.Choice(name="Madeira", value=1),
            app_commands.Choice(name="Ferro", value=2),
            app_commands.Choice(name="Ouro", value=3)
        ],
        receive=[
            app_commands.Choice(name="Madeira", value=1),
            app_commands.Choice(name="Ferro", value=2),
            app_commands.Choice(name="Ouro", value=3)
        ]
    )
    async def trade(self, ctx, give : int, give_amount : int, receive : int, receive_amount : int):
        """Troca recursos com outros jogadores."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce precisa criar um heroi antes de trocar recursos do jogo.")
        
        if give == receive:
            return await inte.response.send_message("Os recursos oferecidos e recebidos precisam ser diferentes.", ephemeral=True)
        elif give_amount < 0 or receive_amount < 0:
            return await inte.response.send_message("A quantidade de recursos nao pode ser negativa.", ephemeral=True)
        elif give_amount == 0 and receive_amount == 0:
            return await inte.response.send_message("As duas quantidades nao podem ser 0 ao mesmo tempo.", ephemeral=True)

        data = get_active_hero(inte.user.id)

        resource_column = self.resource_names[give].lower().replace('madeira', 'wood').replace('ferro', 'iron').replace('ouro', 'gold')
        receive_column = self.resource_names[receive].lower().replace('madeira', 'wood').replace('ferro', 'iron').replace('ouro', 'gold')

        if data[resource_column] < give_amount:
            return await inte.response.send_message("Voce nao tem recursos suficientes para essa troca.", ephemeral=True)


        embed = Embed(title="Oferta de troca", color=Color.blue())
        embed.add_field(name=f"Oferecendo {self.resource_names[give]} {self.resource_emojis[give]}", value=f"Quantidade: {give_amount}", inline=False)
        embed.add_field(name=f"Solicitando {self.resource_names[receive]} {self.resource_emojis[receive]}", value=f"Quantidade: {receive_amount}", inline=False)
        
        view = View()
        accept_back = Button(label="Aceitar", style=ButtonStyle.primary)
        accept_back.callback = lambda i, inte=inte : self.make_trade(i, inte, give, give_amount, receive, receive_amount)
        view.add_item(accept_back)
        
        await inte.response.send_message(embed=embed, view=view)
        
        
    async def make_trade(self, interaction, inte, give : int, give_amount : int, receive : int, receive_amount : int):
        if interaction.user.id == inte.user.id:
            return await interaction.response.send_message("Voce nao pode aceitar a propria oferta de troca.", ephemeral=True)
        
        data = get_active_hero(interaction.user.id)
        
        resource_column = self.resource_names[give].lower().replace('madeira', 'wood').replace('ferro', 'iron').replace('ouro', 'gold')
        receive_column = self.resource_names[receive].lower().replace('madeira', 'wood').replace('ferro', 'iron').replace('ouro', 'gold')

        if data[receive_column] < receive_amount:
            return await interaction.response.send_message("Voce nao tem recursos suficientes para aceitar essa troca.", ephemeral=True)
        
        data = get_active_hero(inte.user.id)
        
        if data[resource_column] < give_amount:
            original =  await inte.original_response()
            await original.edit(view=None)
            return await interaction.response.send_message("A oferta original nao e mais valida.", ephemeral=True)
        
        
        update_active_hero_resources(
            inte.user.id,
            gold=(-give_amount if resource_column == "gold" else receive_amount if receive_column == "gold" else 0),
            wood=(-give_amount if resource_column == "wood" else receive_amount if receive_column == "wood" else 0),
            iron=(-give_amount if resource_column == "iron" else receive_amount if receive_column == "iron" else 0),
        )

        update_active_hero_resources(
            interaction.user.id,
            gold=(give_amount if resource_column == "gold" else -receive_amount if receive_column == "gold" else 0),
            wood=(give_amount if resource_column == "wood" else -receive_amount if receive_column == "wood" else 0),
            iron=(give_amount if resource_column == "iron" else -receive_amount if receive_column == "iron" else 0),
        )
        
        original =  await inte.original_response()
        await original.edit(view=None)
        return await interaction.response.send_message("Troca concluida com sucesso.")

async def setup(bot):
    await bot.add_cog(Trade(bot))
