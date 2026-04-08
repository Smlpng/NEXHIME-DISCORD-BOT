from commands.EconomiaRPG.items.basearmor import BaseArmor


class ArmorStrawHelmet(BaseArmor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.plain["defense"] = 1
        self.plain["magic_resistance"] = 1
        self.update_level()

        self.id = 1
        self.rarity = 1
        self.name = "Straw Helmet"
        self.boosts = f"defense + {self.plain['defense']} | magic resistance + {self.plain['magic_resistance']}"
        self.attack_description = "None"


class ArmorIron(BaseArmor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.plain["defense"] = 2
        self.plain["magic_resistance"] = 3
        self.update_level()

        self.id = 2
        self.rarity = 1
        self.name = "Iron"
        self.boosts = f"defense + {self.plain['defense']} | magic resistance + {self.plain['magic_resistance']}"
        self.attack_description = "None"


class ArmorScale(BaseArmor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.plain["magic"] = 2
        self.plain["magic_resistance"] = 5
        self.update_level()

        self.id = 3
        self.rarity = 4
        self.name = "Scale"
        self.boosts = f"magic + {self.plain['magic']} | magic resistance + {self.plain['magic_resistance']}"
        self.attack_description = "None"


class ArmorBearSkin(BaseArmor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.plain["attack"] = 1
        self.plain["defense"] = 4
        self.update_level()

        self.id = 4
        self.rarity = 4
        self.name = "Bear skin"
        self.boosts = f"defense + {self.plain['defense']} | attack + {self.plain['attack']}"
        self.attack_description = "None"


class ArmorMagicCloak(BaseArmor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.plain["magic"] = 3
        self.plain["magic_resistance"] = 4
        self.plain["max_mana"] = 5
        self.update_level()

        self.id = 5
        self.rarity = 5
        self.name = "Magic Cloak"
        self.boosts = (
            f"magic + {self.plain['magic']} | magic resistance + {self.plain['magic_resistance']}"
            f" | max mana + {self.plain['max_mana']}"
        )
        self.attack_description = "None"


armor_dict = {
    1: ArmorStrawHelmet,
    2: ArmorIron,
    3: ArmorScale,
    4: ArmorBearSkin,
    5: ArmorMagicCloak,
}