from commands.EconomiaRPG.items.baseequipment import BaseEquipment

class BaseArmor(BaseEquipment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "armor"
        self.type_id = 2
    

