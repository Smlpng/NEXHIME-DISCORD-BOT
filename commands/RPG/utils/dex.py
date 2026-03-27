from discord import Embed, Color
from commands.RPG.utils.database import count_enemies_in_zone, list_seen_enemies_by_zone

AMOUNT_OF_ZONES = 5
enemies_amount = [[]] # Extra list for 0 index
for i in range(AMOUNT_OF_ZONES):
    enemies_amount.append({"amount": count_enemies_in_zone(i + 1)})
    
embed_titles = [[], # Extra list for 0 index
                {
                    "name": "**🏕️ Clareira dos Sussurros**"
                },
                {
                    "name": "**⛓️ Ruínas Cobertas de Musgo**"
                },
                {
                    "name": "**🌲 Rio das Presas**"
                },
                {
                    "name": "**🏜️ Caverna do Eco Profundo**"
                },
                {
                    "name": "**🐸 Ninho da Árvore-Mãe**"
                },]


def get_seen_by_zone(zone_id: int, user_id: int) -> list[dict]:
    return list_seen_enemies_by_zone(user_id, zone_id)


def get_seen_line(zone_id: int, user_id: int) -> str:
    enemies_list = ""
    seen = get_seen_by_zone(zone_id, user_id)
    for data in seen:
        enemies_list += "🟢 " + data["name"] + "\n"
    dif = enemies_amount[zone_id]["amount"] - len(seen)
    if dif != 0:
        for _ in range(dif):
            enemies_list += "❔ Não descoberto\n"
            
    return enemies_list


def get_dex_embed(user_id: int):
    embed = Embed(title="Bestiário", description="Inimigos vistos em cada zona", color=Color.blue())

    for i in range(AMOUNT_OF_ZONES):
        zone_id = i + 1
        enemies_list = get_seen_line(zone_id, user_id)
        
        embed.add_field(name=embed_titles[zone_id]["name"], value=enemies_list, inline=False)

    
    
    return embed
