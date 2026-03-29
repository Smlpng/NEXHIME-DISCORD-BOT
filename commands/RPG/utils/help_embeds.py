from discord import Embed, Color

def get_help_embed(command_id: int):
    if command_id == 0: # Introduction
        embed = Embed(title="✨ **Bem-vindo ao RPG 50** ✨", color=Color.blue())
        embed.add_field(name="🛡️ **Sobre**", value="Entre no Reino dos Mil Galhos, uma terra inspirada em lendas símias onde tribos de macacos, reliquias de banana e templos nas copas disputam poder.\n**Sua jornada comeca agora: lute pelo bando e descubra os segredos da Coroa do Cacho.** ⚔️", inline=False)
        embed.add_field(name="📜 **Como usar**", value="👇 Selecione a categoria de comandos que deseja conhecer.\n**Combate** e um bom ponto de partida. 🗡️", inline=False)
        embed.add_field(name="📖 **Historia**", value="Dizem que o antigo Imperio Símio caiu quando a Coroa do Cacho foi quebrada em varias reliquias. Agora, cada zona guarda um fragmento de poder, e so os guerreiros mais fortes do bando podem reunifica-los. 🍌", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272664340142489600/DALLE_2024-08-12_18.13.40_-_A_fantasy_RPG_style_image_of_a_hero_standing_on_a_mountain_seen_from_the_back_holding_a_sword_and_looking_out_towards_a_distant_castle._The_hero_has.webp?ex=66bbcc87&is=66ba7b07&hm=aa8882e4b47cb20fbadfbad4164037a80bb696bb77776d0e7fba77daaea715a7&")
    
    elif command_id == 1: # Combat
        embed = Embed(title="⚔️ Comandos de Combate", color=Color.blue())
        embed.add_field(name="/fight", value="Inicia uma batalha na area atual. 🗡️", inline=False)
        embed.add_field(name="/dungeon (nivel 5 necessario)", value="Entra em uma dungeon com varias lutas e um chefe final. Nao e possivel se curar.\nPode ser jogada com outro jogador. 🏰", inline=True)
        embed.add_field(name="/raid (nivel 10 necessario)", value="Junte-se a outros jogadores para enfrentar um inimigo poderoso. 🛡️", inline=False)
        embed.add_field(name="/pvp", value="Desafie outro jogador para um duelo. 🤺", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272678835913232457/DALLE_2024-08-12_19.11.14_-_A_fantasy_RPG_style_image_of_a_bow_and_arrow._The_bow_has_a_semi-realistic_appearance_with_a_slightly_curved_wooden_body_and_a_taut_string._The_arrow_.webp?ex=66bbda07&is=66ba8887&hm=d78688518fa8994708e9fcd44dc01a59432539df2147be40dd0bf3d7c0c06721&")
        
    elif command_id == 2: # Stats
        embed = Embed(title="📊 Comandos de Status", color=Color.blue())
        embed.add_field(name="/menu", value="Abre o menu do perfil. Se a classe ainda nao tiver sido escolhida, voce pode decidir isso quando quiser. 🧙‍♂️", inline=False)
        embed.add_field(name="/advancements", value="Confira o progresso e as conquistas do seu heroi. 🏆", inline=False)
        embed.add_field(name="/dex", value="Veja informacoes sobre os inimigos encontrados. 📚", inline=False)
        embed.add_field(name="/quests", value="Veja, aceite, entregue ou cancele missoes adaptadas ao progresso atual do heroi. 📜", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272674936749822045/DALLE_2024-08-12_18.55.45_-_A_fantasy_RPG_style_image_of_a_sword_resting_on_a_treasure_chest._The_sword_has_a_semi-realistic_appearance_with_a_sharp_blade_and_ornate_hilt_while_.webp?ex=66bbd666&is=66ba84e6&hm=fad4e8ce1d7ee1d952e519dd7c27831797cdf816b10a730d2e66b62a90111efb&")
        
    elif command_id == 3: # Zones
        embed = Embed(title="🌍 Comandos de Zonas", color=Color.blue())
        embed.add_field(name="/zone", value="Mostra detalhes sobre a area atual e seus inimigos. 🗺️", inline=False)
        embed.add_field(name="/change_zone", value="Move seu heroi para outra area de acordo com o nivel. 🚶‍♂️", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272676356756607036/DALLE_2024-08-12_19.01.27_-_A_fantasy_RPG_style_image_of_a_sky_with_the_sun_visible._The_sky_has_a_semi-realistic_appearance_with_soft_clouds_and_a_warm_glow_from_the_sun_but_no.webp?ex=66bbd7b8&is=66ba8638&hm=6e775e4e6d06eba760add37c811a55c833f443a87aa92c8bc4187f4050fd2b94&")
        
    elif command_id == 4: # Equipment
        embed = Embed(title="🛡️ Comandos de Equipamento", color=Color.blue())
        embed.add_field(name="/inventory", value="Veja seus equipamentos e atributos. 🎒", inline=False)
        embed.add_field(name="/equip_weapon", value="Equipe uma arma do seu inventario. ⚔️", inline=False)
        embed.add_field(name="/equip_armor", value="Equipe uma armadura do seu inventario. 🛡️", inline=False)
        embed.add_field(name="/forge", value="Melhore seus equipamentos na forja. 🔨", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272676579297988638/DALLE_2024-08-12_19.02.19_-_A_fantasy_RPG_style_image_of_a_shield._The_shield_has_a_semi-realistic_appearance_with_a_slightly_worn_surface_detailed_edges_and_a_central_emblem_.webp?ex=66bbd7ed&is=66ba866d&hm=53fa2fc7a5482ed747e9081349ae3f367fc3108f9571094f72cecb623234c7df&")
        
    elif command_id == 5: # Heroes
        embed = Embed(title="🦸 Heroi Unico", color=Color.blue())
        embed.add_field(name="Regra atual", value="Cada usuario pode ter apenas um heroi por conta. Nao ha comandos para criar outro heroi ou trocar de heroi.", inline=False)
        embed.add_field(name="Criacao inicial", value="O perfil unico do jogador pode nascer em comandos de economia, mas a classe do heroi so e escolhida depois, quando ele usar uma parte do jogo que realmente precise dela. 🌟", inline=False)
        embed.add_field(name="/escolher_raca", value="Define a raca do seu heroi dentro do sistema atual. 🧬", inline=False)
        embed.add_field(name="/escolher_tribo", value="Define a tribo do seu heroi. 🏕️", inline=False)
        embed.add_field(name="/trocar_tribo", value="Troca a tribo atual do heroi sem depender do sistema antigo de cargos. 🔄", inline=False)
        embed.add_field(name="/descansar", value="Mostra como o descanso funciona no RPG atual. 🛌", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272677780353716254/DALLE_2024-08-12_19.07.07_-_A_fantasy_RPG_style_image_of_a_helmet._The_helmet_has_a_semi-realistic_appearance_with_a_slightly_worn_surface_detailed_edges_and_a_visor_but_not_o.webp?ex=66bbd90c&is=66ba878c&hm=2e9750c6e13022050007b0177478abbef26bce94b15a3a90b04e0a7d62f22f72&")
        
    elif command_id == 6: # Commerce
        embed = Embed(title="💰 Comandos de Comercio", color=Color.blue())
        embed.add_field(name="/shop", value="Abre a loja para ver os itens disponiveis. 🛒", inline=False)
        embed.add_field(name="/buy [item] [amount]", value="Compra um item na loja. 🛍️", inline=False)
        embed.add_field(name="/trade [give_item] [give_amount] [receive_item] [receive_amount]", value="Troca recursos com outro jogador. 🤝", inline=False)
        embed.add_field(name="/banco", value="Mostra quanto nex esta na carteira e no banco. 🏦", inline=False)
        embed.add_field(name="/depositar [quantidade]", value="Move nex da carteira do heroi para o banco. 📥", inline=False)
        embed.add_field(name="/sacar [quantidade]", value="Move nex do banco para a carteira do heroi. 📤", inline=False)
        embed.add_field(name="/transferir [jogador] [quantidade]", value="Envia nex do seu banco para o banco de outro jogador. 💸", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/474702643625984021/1272675246918336532/DALLE_2024-08-12_18.57.02_-_A_fantasy_RPG_style_image_of_logs_placed_side_by_side._The_logs_have_a_semi-realistic_appearance_with_rough_bark_and_visible_wood_grain_but_not_overl.webp?ex=66bbd6b0&is=66ba8530&hm=00f16d18e828e6543018165ae80d81276b5644c3d9c946934a8e62bc8dfa4300&")
        
    return embed
