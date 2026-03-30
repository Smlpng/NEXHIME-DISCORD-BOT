from commands.RPG.utils.database import increment_advancement


MAX_LEVEL = 50


def get_xp_required(level: int) -> int:
    level = max(int(level), 1)
    return round(6.5 * (1.5 ** level))


def add_kill(user_id : int, amount=1):
    increment_advancement(user_id, "kills", amount)
    
    
def add_upgrade(user_id : int, amount=1):
    increment_advancement(user_id, "upgrades", amount)
    
    
def add_nex_spent(user_id : int, amount : int):
    increment_advancement(user_id, "nex_spent", amount)


def add_gold_spent(user_id : int, amount : int):
    add_nex_spent(user_id, amount)
