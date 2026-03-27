from commands.RPG.game.characters.basehero import BaseHero
from commands.RPG.utils.decorators import mana_ability, health_ability
    
# ID 1
class MagicDummy(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=20,
            attack=3,
            magic=7,
            defense=3,
            magic_resistance=4,
            mana=20,
            **kwargs
        )
        self.classname = "Mago"
        self.image = "https://cdn.discordapp.com/attachments/474702643625984021/1271206558742614046/DALLE_2024-08-08_17.40.55_-_A_fantasy_RPG_style_image_of_a_Mage_class_hero_in_a_medieval_training_field._The_hero_has_a_semi-realistic_appearance_with_flowing_robes_a_staff_and.webp?ex=66b67edd&is=66b52d5d&hm=9d9a41fab7361cf89fb1fcab2e3ee09800fc2bad76f61e62c5d564c8c01e9d66&"
        
        level = kwargs.get('level', 1)
        
        self.abilities["Chama magica"] = self.magic_flame
        
        if level >= 10:
            self.abilities["Cura"] = self.heal
            
        if level >= 25:
            self.abilities["Feitico ancestral"] = self.ancestral_spell
            
            
    @mana_ability(cost=5)
    def magic_flame(self, enemy):
        return self.do_magic(enemy, 10)
    
    @mana_ability(cost=10)
    def heal(self, enemy):
        amount = self.magic * 2
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return f"{self.name} recuperou {amount} de vida"
    
    @mana_ability(cost=20)
    def ancestral_spell(self, enemy):
        return self.do_magic(enemy, 30)
    
# ID 2
class AssasinDummy(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=25,
            attack=5,
            magic=2,
            defense=4,
            magic_resistance=5,
            mana=10,
            **kwargs
        )
        self.classname = "Assassino"
        self.image = "https://cdn.discordapp.com/attachments/474702643625984021/1271206188444418088/DALLE_2024-08-08_17.39.23_-_An_animated_fantasy_RPG_style_image_of_an_Assassin_class_hero_in_a_medieval_training_field._The_hero_is_a_melee_fighter_holding_two_small_daggers_one.webp?ex=66b67e85&is=66b52d05&hm=c498c2bdecce29f674c22615f0449dbdabe14a322de33336414cb918b81d60b5&"
        
        level = kwargs.get('level', 1)
        
        self.abilities["Golpe brutal"] = self.super_hit
        
        if level >= 10:
            self.abilities["Sacrificio"] = self.sacrifice
            
        if level >= 25:
            self.abilities["Quebra-escudo"] = self.shield_broker
        
    @mana_ability(cost=5)
    def super_hit(self, enemy):
        return self.do_attack(enemy, 20)
    
    @health_ability(cost=33)
    def sacrifice(self, enemy):
        return self.do_attack(enemy, 35)
    
    @mana_ability(cost=10)
    def shield_broker(self, enemy):
        enemy.defense -= self.magic
        if enemy.defense <= 0:
            enemy.defense = 1
        return f"reduziu a defesa de {enemy.name} em {self.magic} pontos"
    
    
# ID 3
class Tank(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=30,
            attack=3,
            magic=1,
            defense=6,
            magic_resistance=6,
            mana=10,
            **kwargs
        )
        self.classname = "Tanque"
        self.image = "https://cdn.discordapp.com/attachments/474702643625984021/1271109367076229170/DALLE_2024-08-08_11.14.42_-_A_fantasy_RPG_style_image_of_a_Tank_class_hero_in_a_medieval_training_field._The_hero_has_a_semi-realistic_appearance_with_heavy_armor_a_large_shield.webp?ex=66b62459&is=66b4d2d9&hm=13c260f3ff409466d40a100757753af705e8f615e330499ba18469eb50373f0c&"
        
        level = kwargs.get('level', 1)
        
        self.abilities["Esmagar"] = self.smash
        
        if level >= 10:
            self.abilities["Fortalecer"] = self.reforce
            
            
    @mana_ability(cost=10)
    def smash(self, enemy):
        return self.do_attack(enemy, 20)
    
    @mana_ability(cost=10)
    def reforce(self, enemy):
        self.defense += self.magic
        self.magic_resistance += self.magic
        return f"{self.name} aumentou a propria defesa e resistencia magica em {self.magic} pontos"
