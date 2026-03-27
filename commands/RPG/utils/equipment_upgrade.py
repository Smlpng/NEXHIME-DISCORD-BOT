from commands.RPG.utils.database import list_active_clean_inventory, get_active_hero_id, get_hero_resources_by_id, increment_inventory_item_level, spend_hero_resources
from commands.RPG.utils.progress import add_upgrade

def equipment_upgrade_cost(level : int, rarity : int) -> tuple:
    if not (0 <= level <= 49 and level < rarity * 10):
        return False
    
    # Gold
    gold_cost = level * (100 * ((level // 10) + 1))
    
    # Wood
    wood_cost = 10 + level ** 2 * 2
    
    # Iron
    iron_cost = round(level + 5 ** (0.1 * level))
    
    # Runes
    if rarity >= 4:
        match level:
            case 24:
                rune_cost = 1
            case 29:
                rune_cost = 4
            case 34:
                rune_cost = 6
            case 39:
                rune_cost = 12
            case 44:
                rune_cost = 18
            case 49:
                rune_cost = 35
            case _:
                rune_cost = 0
    else:
        rune_cost = 0
    
    return (gold_cost, wood_cost, iron_cost, rune_cost)


def make_upgrade(user_id : int, item : object) -> bool:
    data = list_active_clean_inventory(user_id, item.type, item.id)[0]

    cost = equipment_upgrade_cost(data["level"], item.rarity)
    
    hero_id = get_active_hero_id(user_id)
    
    data = get_hero_resources_by_id(hero_id)
    
    if data["gold"] >= cost[0] and data["wood"] >= cost[1] and data["iron"] >= cost[2] and data["runes"] >= cost[3]:
        spend_hero_resources(hero_id, gold=cost[0], wood=cost[1], iron=cost[2], runes=cost[3])
        increment_inventory_item_level(hero_id, item.id, item.type)
        
        add_upgrade(user_id)
        
        return True
    
    return False

