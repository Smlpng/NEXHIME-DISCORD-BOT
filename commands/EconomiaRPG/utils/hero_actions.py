from commands.EconomiaRPG.characters.heros import *
from commands.EconomiaRPG.utils.database import add_item_to_active_hero, active_hero_has_item, get_active_hero_clean, record_enemy_seen

def load_hero(user_id : int, name: str="user") -> object:
    data = get_active_hero_clean(user_id)
    hero_class = get_class_by_id(data["class"])
    hero = hero_class(level=data["level"], weapon_id=data["weapon_id"], weapon_level=data["weapon_level"], armor_id=data["armor_id"], armor_level=data["armor_level"], name=name)
    return hero

def get_class_by_id(class_id : int) -> object:
    return class_dict[class_id]

class_dict = {
    1 : MagicDummy,
    2 : AssasinDummy,
    3 : Tank
}


def add_if_new(user_id : int, item : object) -> bool:
    if not has_item(user_id, item):
        add_item(user_id, item)
        return True
    else:
        return False


def has_item(user_id : int, item : object) -> bool:
    return active_hero_has_item(user_id, item.id, item.type)


def add_item(user_id : int, item : object) -> None:
    add_item_to_active_hero(user_id, item.type, item.id)
    
    
def see_enemy(user_id: int, enemy_id: int) -> None:
    record_enemy_seen(user_id, enemy_id)

