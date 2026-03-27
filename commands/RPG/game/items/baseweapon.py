from commands.RPG.game.items.baseequipment import BaseEquipment

class BaseWeapon(BaseEquipment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "weapon"
        self.type_id = 1
    
    def custom_attack(self):
        pass





