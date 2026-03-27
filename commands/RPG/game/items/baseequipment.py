class BaseEquipment:
    def __init__(self, **kwargs):
        self.plain = {
            "attack": 0,
            "magic": 0,
            "defense": 0,
            "magic_resistance": 0,
            "max_mana": 0
        }

        self.multi = {
            "attack": 0,
            "magic": 0,
            "defense": 0,
            "magic_resistance": 0,
            "max_mana": 0
        }
        self.level = kwargs.get("level", 1)
        self.name = "Base name"
        self.boosts = ""
        self.attack_description = "None"
        self.id = None
        
        self.update_level()

    def update_level(self):
        PROGRESS = 1.2
        level = self.level - 1

        for stat in self.plain:
            self.plain[stat] = round(self.plain[stat] * PROGRESS ** level)
            self.multi[stat] = round(self.multi[stat] * PROGRESS ** level)
