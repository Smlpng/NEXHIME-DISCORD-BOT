from discord import Embed, Color
from commands.RPG.utils.querys import get_zone
from commands.RPG.utils.dex import get_seen_line

zones_data = [
    {},
    {
        "name": "🏕️ Clareira dos Sussurros",
        "level": "Baixo",
        "loot": "Baixo",
        "description": "Uma clareira antiga onde o vento parece carregar avisos dos ancestrais do bando. Totens rachados e pegadas recentes cercam o caminho.",
        "image": "https://cdn.discordapp.com/attachments/474702643625984021/1265302785864237106/DALLE_2024-07-23_10.41.24_-_A_medieval_training_field_with_various_training_dummies_archery_targets_and_wooden_training_weapons_scattered_around._The_field_is_surrounded_by_a_w.webp?ex=66a1048c&is=669fb30c&hm=b62a903d9dd1cdd051aa01478590a24b5a79cc470456dafbadfd041a261498f9&"
    },
    {
        "name": "⛓️ Ruínas Cobertas de Musgo",
        "level": "Baixo",
        "loot": "Baixo",
        "description": "Restos de um presidio ancestral tomados pelo musgo e pela umidade. Correntes velhas, celas abertas e sombras inquietas dominam as ruinas.",
        "image": "https://cdn.discordapp.com/attachments/474702643625984021/1265303722422960191/DALLE_2024-07-23_10.45.08_-_A_medieval_dungeon_interior_with_stone_walls_and_floors_dimly_lit_by_torches._The_scene_includes_iron_bars_a_few_wooden_barrels_and_a_wooden_table_.webp?ex=66a1056b&is=669fb3eb&hm=ca4e36de374748ba92ce8b553c2db2a08d19b046d0f12034ad4dbf95215dae4d&"
    },
    {
        "name": "🌲 Rio das Presas",
        "level": "Medio",
        "loot": "Baixo",
        "description": "Um rio feroz corta a mata e atrai predadores de todos os tamanhos. Margens enlameadas, cipós baixos e rugidos distantes marcam a região.",
        "image": "https://cdn.discordapp.com/attachments/474702643625984021/1265303908931207280/DALLE_2024-07-23_10.45.55_-_A_medieval_forest_scene_with_tall_dense_trees_and_thick_underbrush._Sunlight_filters_through_the_canopy_creating_dappled_shadows_on_the_forest_floor.webp?ex=66a10598&is=669fb418&hm=408df2146b1fbfae1386bd3c3ceb5fd568c9d286a215f1bff3e1926bf9d43a64&"
    },
    {
        "name": "🏜️ Caverna do Eco Profundo",
        "level": "Medio",
        "loot": "Medio",
        "description": "Um complexo de tuneis profundos onde o som se multiplica e confunde invasores. Camaras antigas escondem guardioes, reliquias e criaturas da areia.",
        "image": "https://cdn.discordapp.com/attachments/474702643625984021/1265304075658989630/DALLE_2024-07-23_10.46.36_-_A_medieval_desert_scene_with_vast_sand_dunes_under_a_bright_clear_sky._Sparse_vegetation_like_dry_bushes_and_cacti_are_scattered_around._In_the_dista.webp?ex=66a105bf&is=669fb43f&hm=3e59d8437a6ca3eed933774322366cf53c57f72a029b599bca422f9b896f807b&"
    },
    {
        "name": "🐸 Ninho da Árvore-Mãe",
        "level": "Alto",
        "loot": "Alto",
        "description": "No topo das águas escuras e das raízes gigantes ergue-se a Árvore-Mãe. Ali se escondem mutações, xamãs e os segredos finais do reino símio.",
        "image": "https://cdn.discordapp.com/attachments/474702643625984021/1265304195309899907/DALLE_2024-07-23_10.47.04_-_A_medieval_swamp_scene_with_murky_water_dense_vegetation_and_twisted_gnarled_trees_draped_with_hanging_moss._The_swamp_is_shrouded_in_mist_creatin.webp?ex=66a105dc&is=669fb45c&hm=431a958de0a4e38fa982986d30ef88322a24252b215826eb8fbfd2ff0564a4e7&"
    }
]


def get_zone_embed(zone_id: int):
    embed = Embed(title=zones_data[zone_id]["name"], color=Color.blue())
    embed.add_field(name="Nivel da zona", value=zones_data[zone_id]["level"], inline=False)
    embed.add_field(name="Loot", value=zones_data[zone_id]["loot"], inline=True)
    embed.add_field(name="Lore", value=zones_data[zone_id]["description"], inline=False)
    embed.set_image(url=zones_data[zone_id]["image"])
    
    return embed


def get_zone_full_embed(user_id: int):
    zone_id = get_zone(user_id)
    embed = Embed(title=zones_data[zone_id]["name"], color=Color.blue())
    embed.add_field(name="Nivel da zona", value=zones_data[zone_id]["level"], inline=False)
    embed.add_field(name="Loot", value=zones_data[zone_id]["loot"], inline=True)
    embed.add_field(name="Lore", value=zones_data[zone_id]["description"], inline=False)
    embed.add_field(name="Inimigos", value=get_seen_line(zone_id, user_id), inline=False)
    embed.set_image(url=zones_data[zone_id]["image"])
    
    return embed
