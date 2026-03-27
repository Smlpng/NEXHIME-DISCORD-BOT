from commands.RPG.utils.database import increment_advancement


def add_kill(user_id : int, amount=1):
    increment_advancement(user_id, "kills", amount)
    
    
def add_upgrade(user_id : int, amount=1):
    increment_advancement(user_id, "upgrades", amount)
    
    
def add_gold_spent(user_id : int, amount : int):
    increment_advancement(user_id, "gold_spent", amount)
