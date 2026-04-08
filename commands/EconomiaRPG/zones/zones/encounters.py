import pandas as pd
import random
from pathlib import Path
from commands.EconomiaRPG.characters.enemies import enemy_dict
from commands.EconomiaRPG.characters.loot import Loot
from commands.EconomiaRPG.items.armors import *
from commands.EconomiaRPG.items.weapons import *

CSV_DIR = Path(__file__).resolve().parent / "csv"

routes = [
    CSV_DIR / "Zone enemies - Training camp.csv",
    CSV_DIR / "Zone enemies - Dungeon.csv",
    CSV_DIR / "Zone enemies - Forest.csv",
    CSV_DIR / "Zone enemies - Desert.csv",
    CSV_DIR / "Zone enemies - Swamp.csv",
]

df_list = [[]] # an empty list to skip index 0
probabilities = [[]]
bosses = [[]]

for route in routes:
    df = pd.read_csv(route)
    df_list.append(df)
    probabilities.append(df['Probability'].tolist())
    bosses.append(df[df['Boss'] == True].to_dict(orient='records'))
    

def get_enemy_from_zone(zone_id: int, bonus: float=None):
    enemy_data = random.choices(df_list[zone_id].to_dict(orient='records'), weights=probabilities[zone_id], k=1)[0]
    level = random.randint(enemy_data["Min-Level"], enemy_data["Max-Level"])
    if bonus:
        level = round(level * bonus)
    enemy = enemy_dict[enemy_data["ID"]](level=level)
    return enemy


def get_boos_from_zone(zone_id: int, bonus: float=None):
    boss_data = random.choices(bosses[zone_id])[0]
    boss_level = random.randint(boss_data["Min-Level"], boss_data["Max-Level"])
    if bonus:
        boss_level = round(boss_level * bonus)
    boss = enemy_dict[boss_data["ID"]](level=boss_level)
    return boss


def get_dungeon_from_zone(zone_id: int, bonus: float=None) -> list:
    enemy_amount = 2 + zone_id
    enemy_list = []

    boss = get_boos_from_zone(zone_id, bonus=bonus)
    enemy_list.append(boss)
    
    for _ in range(enemy_amount):
        enemy_list.append(get_enemy_from_zone(zone_id, bonus=bonus))
        
    return enemy_list


def get_dungeon_loot_from_zone(zone_id: int) -> Loot:
    equipments = [None, WeaponCrossbow, ArmorScale, ArmorBearSkin, WeaponSpear, WeaponRelic]
    loot = Loot(nex=20**zone_id,wood=3**zone_id,iron=3**zone_id,xp=100**zone_id,equipment=equipments[zone_id],drop_rate=1)
    return loot
    
