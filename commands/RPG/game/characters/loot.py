from random import random
from commands.RPG.utils.database import apply_loot_to_active_hero, get_active_hero_level_and_xp
from commands.RPG.utils.hero_actions import add_if_new


class Loot():
    def __init__(self, nex=0, wood=0, iron=0, runes=0, xp=0, equipment=None, drop_rate=0.1, level=1):
        self.nex = nex 
        self.wood = wood
        self.iron = iron
        self.runes = runes
        self.xp = round(xp * (1.07 ** level))
        self.equipment = equipment
        self.drop_rate = drop_rate
    
    def drop(self, user_id, name:str = "Usuario"):
        # Get xp info
        data = get_active_hero_level_and_xp(user_id)
        
        # Update xp and level if level < 50
        if data["level"] < 50:
            xp_needed = round(6.5 * (1.5 ** data["level"]))
            if xp_needed <= data["xp"] + self.xp:
                final_xp = data["xp"] + self.xp - xp_needed
                level_up = 1
            else:
                final_xp = data["xp"] + self.xp
                level_up = 0
        else:
            final_xp = 0
            level_up = 0
        
        # Load resources data
        apply_loot_to_active_hero(user_id, level_up, int(final_xp), self.nex, self.wood, self.iron, self.runes)
        
        # Create message
        message = "Recebeu"
        if self.nex > 0:
            message = message + f" {self.nex} nex"
        if self.wood > 0:
            message = message + f" {self.wood} de madeira"
        if self.iron > 0:
            message = message + f" {self.iron} de ferro"
        if self.runes > 0:
            message = message + f" {self.runes} runas"
        message = message + f"\ne {name} ganhou {self.xp} de XP"
        if level_up:
            message += f"\n{name} subiu de nivel"
            
        # If new equipment load it
        if self.equipment:
            if random() <= self.drop_rate:
                equipment = self.equipment()
                if add_if_new(user_id, equipment):
                    message += f"\n{name} recebeu um novo item: {equipment.name}"
            
            
        return message
