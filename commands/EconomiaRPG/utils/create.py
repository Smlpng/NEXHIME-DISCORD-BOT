from commands.EconomiaRPG.utils.database import ensure_profile, has_selected_class, set_active_hero_class
from discord import Embed, ButtonStyle, Color
from discord.ui import Button, View
from commands.EconomiaRPG.characters.heros import *

async def create_hero(inte):
    async def callback(interaction, class_name, id):
        if interaction.user != inte.user:
            return  # assure that the user is the same that started the command

        if has_selected_class(interaction.user.id):
            original_message = await inte.original_response()
            await original_message.edit(
                embed=Embed(
                    title="Heroi ja existente",
                    description="Voce ja escolheu a classe do seu heroi.",
                    color=0x1E90FF,
                ),
                view=None,
            )
            return

        ensure_profile(interaction.user.id)
        set_active_hero_class(interaction.user.id, id)

        embed = Embed(title=f"Classe de {interaction.user}", description="Heroi criado com _sucesso_!", color=0x1E90FF)
        embed.add_field(name="Classe:", value=class_name)
        embed.set_image(url=class_images[class_name])
        original_message = await inte.original_response() # inte not interaction to get the last message
        await original_message.edit(embed=embed, view=None)
    
    # Each class with their picture 
    class_images = {
        "ðŸ§™â€â™‚ï¸ Mago": MagicDummy().image,
        "ðŸ”ª Assassino": AssasinDummy().image,
        "ðŸ›¡ï¸ Tanque": Tank().image
    }
    
    ensure_profile(inte.user.id)
    if has_selected_class(inte.user.id):
        await inte.response.send_message("Voce ja escolheu a classe do seu heroi.")
        return

    # sends a message and waits for an answer via buttons.
    embed = Embed(title=f"{inte.user.name}, ESCOLHA SUA CLASSE!", color=Color.blue(), description="Clique em um botao para escolher sua classe")
    embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272664340142489600/DALLE_2024-08-12_18.13.40_-_A_fantasy_RPG_style_image_of_a_hero_standing_on_a_mountain_seen_from_the_back_holding_a_sword_and_looking_out_towards_a_distant_castle._The_hero_has.webp?ex=66bbcc87&is=66ba7b07&hm=aa8882e4b47cb20fbadfbad4164037a80bb696bb77776d0e7fba77daaea715a7&")
    
    #creates buttons
    view = View()
        
    for index, class_name in enumerate(class_images):
        button = Button(label=class_name, style=ButtonStyle.primary)
        
        button.callback = lambda i, class_name=class_name, id=index+1 : callback(i, class_name, id)
        view.add_item(button)

    await inte.response.send_message(embed=embed, view=view, ephemeral=True)
