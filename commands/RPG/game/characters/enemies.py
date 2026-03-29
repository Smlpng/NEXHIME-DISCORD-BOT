from commands.RPG.game.characters.basehero import BaseHero
from commands.RPG.game.items.weapons import *
from commands.RPG.game.items.armors import *
from commands.RPG.game.characters.loot import Loot
from commands.RPG.utils.decorators import mana_ability

        
class EnemyTotemDoBando(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=40,
            attack=2,
            magic=1,
            defense=7,
            magic_resistance=3,
            mana=100,
            **kwargs
        )
        self.name = "Totem do Bando"
        self.image = "https://cdn.discordapp.com/attachments/474702643625984021/1248370223644672050/tplImg448cf06ed22b4c25bee83fed318624bd.jpg?ex=6665651e&is=6664139e&hm=9c4481d293279c988d33a3aa998d8559d3f02635059da297b03a37b86353155f&"
        self.id = 1
        
        self.ability = {
            "name" : "teste",
            "cost" : 10,
            "func" : self.special_attack
        }
        
        self.loot = Loot(
            nex=10,
            wood=2,
            xp=10,
            equipment = WeaponKnife,
            level=kwargs.get('level', 1)
        )
        
        
    
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, 20)
    
        
class EnemyGosmaDeBanana(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
           hp=20,
           attack=1,
           magic=3,
           defense=2,
           magic_resistance=2,
           mana=10,
           **kwargs
        )
        self.name = 'Gosma de Banana'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1248374929783521280/13712f15-7631-468d-a5cb-4d55d4cddfdc.jpeg?ex=66729880&is=66714700&hm=bb6b4be5d85aae3ed91c6728e488b1f0114acdf310217859fb34e29f3d39888e&'
        self.id = 2

        self.ability = {
            "name" : "Disparo pegajoso",
            "cost" : 10,
            "func" : self.special_attack
        }
        
        self.loot = Loot(
           nex=1,
           wood=0,
           iron=1,
           runes=0,
           xp=4,
           equipment=ArmorStrawHelmet,
           level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, 30)
        
class EnemySimioDeMagma(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=50,
            attack=5,
            magic=7,
            defense=4,
            magic_resistance=9,
            mana=50,
            **kwargs
        )
        self.name = 'Símio de Magma'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1255177713472508035/fire_dragon.jpeg?ex=667c2ed6&is=667add56&hm=c0d22dfa4d431f5bf6c93f14d1b6c125e82b7cb964638390605d4b6468135bb4&'
        self.id = 3

        self.ability = {
            "name" : "Sopro infernal",
            "cost" : 25,
            "func" : self.special_attack
        }
        
        self.loot = Loot(
            nex=60,
            wood=5,
            iron=0,
            runes=0,
            xp=10,
            equipment=None,
            drop_rate=0.05,
            level=kwargs.get('level', 1)
        )
        
         
    @mana_ability(cost=25)
    def special_attack(self, enemy):
        enemy.mana -= 10
        if enemy.mana < 0:
            enemy.mana = 0
        message = self.do_magic(enemy, 40)
        message += f"\n{enemy.name} perdeu 10 de mana"
        return message
        
class EnemyMacacoOssudo(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=30,
            attack=3,
            magic=1,
            defense=1,
            magic_resistance=2,
            mana=10,
            **kwargs
        )
        self.name = 'Macaco Ossudo'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1256033175818473472/skeleton.jpeg?ex=667f4b8d&is=667dfa0d&hm=1f4f3dc7de924fb5ff26856001a5d51aa3a03256fdbe7e7adced7cc961f9f862&'
        self.id = 4

        self.ability = {
            "name" : "Coleta de ossos",
            "cost" : 10,
            "func" : self.special_attack
        }
        
        self.loot = Loot(
            nex=1,
            wood=0,
            iron=1,
            runes=0,
            xp=2,
            equipment=WeaponKnife,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        amount = self.magic * 5
        if self.hp + amount > self.max_hp:
            amount = self.max_hp - self.hp
            self.hp = self.max_hp
        else:
            self.hp += amount
        return f"{self.name} recuperou {amount} de HP"
        
class EnemySaguiSaqueador(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=10,
            attack=4,
            magic=1,
            defense=2,
            magic_resistance=2,
            mana=10,
            **kwargs
        )
        self.name = 'Sagui Saqueador'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1265311340176736257/DALLE_2024-07-23_11.15.25_-_A_fantasy_RPG_style_image_of_a_goblin_in_a_fighting_stance_standing_in_a_medieval_training_field._The_goblin_has_green_skin_pointy_ears_and_is_wear.webp?ex=66a10c83&is=669fbb03&hm=070ea131dda78975751ae19bcd053eba7956e3963b522bc23578c6d3102ab960&'
        self.id = 5

        self.ability = {
            "name" : "Mordida",
            "cost" : 10,
            "func" : self.special_attack
        }
        
        self.loot = Loot(
            nex=2,
            wood=0,
            iron=0,
            runes=0,
            xp=3,
            equipment=WeaponGloves,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=20)
    
    
class EnemyMicoVigia(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=15,
            attack=7,
            magic=1,
            defense=2,
            magic_resistance=2,
            mana=5,
            **kwargs
        )
        self.name = 'Mico Vigia'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1265316305914036225/DALLE_2024-07-23_11.35.10_-_A_fantasy_RPG_style_image_of_a_crow_perched_on_a_wooden_post._The_crow_has_glossy_black_feathers_a_sharp_beak_and_piercing_eyes_with_a_semi-realist.webp?ex=66a11123&is=669fbfa3&hm=ee543d69c19e97c5912237c13172f333e19964edbc5ca7d50b09dfa93ac4171f&'
        self.id = 6
        
        self.ability = {
            "name" : "Grito",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=1,
            wood=0,
            iron=0,
            runes=0,
            xp=2,
            equipment=ArmorIron,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=15)
    
    
class EnemyLarvaDaCopa(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=5,
            attack=1,
            magic=3,
            defense=1,
            magic_resistance=1,
            mana=5,
            **kwargs
        )
        self.name = 'Larva da Copa'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1265318463317086342/DALLE_2024-07-23_11.43.45_-_A_fantasy_RPG_style_image_of_a_worm_on_the_ground._The_worm_has_a_slightly_segmented_body_earthy_colors_and_a_subtle_sheen_with_a_semi-realistic_ap.webp?ex=66a11326&is=669fc1a6&hm=46f9be4583f93f9797e8b71306649b90a5d5f6975e48b8ca4f05bad831cb4535&'
        self.id = 7
        
        self.ability = {
            "name" : "Cusparada de terra",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=0,
            wood=0,
            iron=0,
            runes=0,
            xp=2,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=15)
    
    
class EnemySombraDoGalho(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=15,
            attack=0,
            magic=10,
            defense=4,
            magic_resistance=8,
            mana=40,
            **kwargs
        )
        self.name = 'Sombra do Galho'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1265671051803885669/DALLE_2024-07-24_11.04.41_-_A_fantasy_RPG_style_image_of_a_ghost_in_a_medieval_dungeon._The_ghost_has_a_translucent_ethereal_appearance_with_a_faint_blue_glow_and_an_eerie_expr.webp?ex=66a25b85&is=66a10a05&hm=375903be12e4245ce0a32bce5480ede52125c5d36c108d1cc3f43aa14bf0020f&'
        self.id = 8

        self.ability = {
            "name" : "Escuridao",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=1,
            wood=0,
            iron=2,
            runes=0,
            xp=3,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=20)
        
        
class EnemyRatoDoCeleiroDeBanana(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=25,
            attack=3,
            magic=1,
            defense=5,
            magic_resistance=6,
            mana=10,
            **kwargs
        )
        self.name = 'Rato do Celeiro de Banana'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1265674069462880326/DALLE_2024-07-24_11.16.47_-_A_fantasy_RPG_style_image_of_a_giant_rat_in_a_medieval_dungeon._The_rat_has_dark_fur_sharp_teeth_and_red_eyes_with_a_semi-realistic_appearance_that.webp?ex=66a25e55&is=66a10cd5&hm=cbf3649a0c2ebefad80495b18dd8409a09fff322c806f934d7b799f80f08d31e&'
        self.id = 9
        
        self.ability = {
            "name" : "Mordida",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=2,
            wood=0,
            iron=0,
            runes=0,
            xp=2,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
    
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=15)
       

class EnemyBugioDePresas(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=15,
            attack=7,
            magic=2,
            defense=4,
            magic_resistance=4,
            mana=10,
            **kwargs
        )
        self.name = 'Bugio de Presas'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1266042518877900871/DALLE_2024-07-25_11.40.47_-_A_fantasy_RPG_style_image_of_a_wolf_in_a_forest._The_wolf_has_a_semi-realistic_appearance_with_fur_details_sharp_eyes_and_a_powerful_stance_but_not.webp?ex=66a3b57a&is=66a263fa&hm=998095c407c5a4a28f8dac20571c29655b0a97fb79a490bc99bf9a6e0bc9a049&'
        self.id = 10
        
        self.ability = {
            "name" : "Rugido",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=2,
            wood=1,
            iron=0,
            runes=0,
            xp=3,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        if self.magic > enemy.defense:
            reduced = enemy.defense
        else:
            reduced = self.magic

        enemy.defense -= reduced
        return f"a defesa de {enemy.name} foi reduzida em {reduced}"
        
        
class EnemyGorilaSaqueador(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=35,
            attack=4,
            magic=4,
            defense=8,
            magic_resistance=8,
            mana=20,
            **kwargs
        )
        self.name = 'Gorila Saqueador'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1266047261993865357/DALLE_2024-07-25_11.59.43_-_A_fantasy_RPG_style_image_of_a_giant_goblin_in_a_forest._The_goblin_has_green_skin_pointy_ears_and_is_wearing_simple_ragged_clothing._It_has_a_semi.webp?ex=66a3b9e5&is=66a26865&hm=312662606ae1d4d45e84141b36da00a6dd02df3310f0333a4983872b7b790959&'
        self.id = 11
        
        self.ability = {
            "name" : "Esmagar",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=6,
            wood=1,
            iron=0,
            runes=0,
            xp=5,
            equipment=WeaponPan,
            level=kwargs.get('level', 1)
        )
        

    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=20)
    
    
class EnemyUrsoDasBananeiras(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=20,
            attack=6,
            magic=1,
            defense=10,
            magic_resistance=2,
            mana=10,
            **kwargs
        )
        self.name = 'Urso das Bananeiras'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1266048696005562423/DALLE_2024-07-25_12.05.25_-_A_fantasy_RPG_style_image_of_a_bear_in_a_forest._The_bear_has_a_semi-realistic_appearance_with_fur_details_and_a_strong_powerful_stance_but_not_over.webp?ex=66a3bb3b&is=66a269bb&hm=aaab02c160670ef2f47bc96963bc1e3b98a0c10ccfefb4b0a0c616935d6eed98&'
        self.id = 12
        
        self.ability = {
            "name" : "Arranhao",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=2,
            wood=3,
            iron=0,
            runes=0,
            xp=3,
            equipment=ArmorBearSkin,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=15)
    
    
class EnemyJiboiaDoCipo(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=20,
            attack=2,
            magic=6,
            defense=2,
            magic_resistance=2,
            mana=20,
            **kwargs
        )
        self.name = 'Jiboia do Cipó'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1266371103312314369/DALLE_2024-07-26_09.26.30_-_A_fantasy_RPG_style_image_of_a_snake_in_a_forest._The_snake_has_a_semi-realistic_appearance_with_scales_and_a_coiled_ready-to-strike_pose_but_not_ov.webp?ex=66a4e77f&is=66a395ff&hm=681a1bfad37eaa347f7892bbdf41a3c7a5604458b52b7feb9d1f8eb660740477&'
        self.id = 13
        
        self.ability = {
            "name" : "Mordida venenosa",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=3,
            wood=1,
            iron=0,
            runes=0,
            xp=2,
            equipment=WeaponMedkit,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=10)
    
    
class EnemyAncestralEnfaixado(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=30,
            attack=3,
            magic=5,
            defense=3,
            magic_resistance=3,
            mana=10,
            **kwargs
        )
        self.name = 'Ancestral Enfaixado'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1267487705395363920/DALLE_2024-07-29_11.23.19_-_A_fantasy_RPG_style_image_of_a_mummy_in_a_desert._The_mummy_has_a_semi-realistic_appearance_with_tattered_bandages_and_a_menacing_stance_but_not_over.webp?ex=66a8f769&is=66a7a5e9&hm=c7fc13a1656992475e9b20f07bea0217ac7f1ad123199125b1a1a608bae5c160&'
        self.id = 14
        
        self.ability = {
            "name" : "Regeneracao",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=2,
            wood=1,
            iron=1,
            runes=0,
            xp=3,
            equipment=ArmorMagicCloak,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        amount = self.magic * 5
        if self.hp + amount > self.max_hp:
            amount = self.max_hp - self.hp
            self.hp = self.max_hp
        else:
            self.hp += amount
        return f"{self.name} recuperou {amount} de HP"
    
    
class EnemyEscorpiaoDaCasca(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=15,
            attack=9,
            magic=2,
            defense=3,
            magic_resistance=4,
            mana=5,
            **kwargs
        )
        self.name = 'Escorpiao da Casca'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1267490719401250816/DALLE_2024-07-29_11.35.23_-_A_fantasy_RPG_style_image_of_a_scorpion_in_a_desert._The_scorpion_has_a_semi-realistic_appearance_with_a_segmented_body_pincers_and_a_curved_tail_wi.webp?ex=66a8fa38&is=66a7a8b8&hm=a1981b0e7d4391763418573b55993e80eb1fed614ddfa7c4bd20c6e1c9f432de&'
        self.id = 15

        self.ability = {
            "name" : "Ferroada venenosa",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=4,
            wood=0,
            iron=0,
            runes=0,
            xp=3,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=30)
    
    
class EnemyGuardiaoDeAreiaDoCacho(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=50,
            attack=3,
            magic=3,
            defense=5,
            magic_resistance=5,
            mana=20,
            **kwargs
        )
        self.name = 'Guardiao de Areia do Cacho'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1267493041858547813/DALLE_2024-07-29_11.44.09_-_A_fantasy_RPG_style_image_of_a_sand_golem_in_a_desert._The_golem_has_a_semi-realistic_appearance_with_a_body_made_of_sand_and_rock_with_glowing_eyes_.webp?ex=66a8fc62&is=66a7aae2&hm=999eebfe24423072d1829241da65817004736e687d60bb82d8c82549327dd9b7&'
        self.id = 16
        
        self.ability = {
            "name" : "Esmagar",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=3,
            wood=1,
            iron=2,
            runes=0,
            xp=4,
            equipment=None,
            level=kwargs.get('level', 1)
        )


    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=10)
    
    
class EnemyCatadoresDoSol(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=20,
            attack=5,
            magic=2,
            defense=4,
            magic_resistance=8,
            mana=10,
            **kwargs
        )
        self.name = 'Catadores do Sol'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1267496827708772372/DALLE_2024-07-29_11.59.46_-_A_fantasy_RPG_style_image_of_a_carrion_bird_flying_in_a_desert._The_bird_has_a_semi-realistic_appearance_with_dark_feathers_a_sharp_beak_and_outstre.webp?ex=66a8ffe8&is=66a7ae68&hm=dc879d2e5edeba93a3e59d8437c5864fbccb7589bbf55bdca3598080e5d74c26&'
        self.id = 17
        
        self.ability = {
            "name" : "Bicadas",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=3,
            wood=0,
            iron=2,
            runes=0,
            xp=3,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=30)
    
    
class EnemySapoDoBananalPodre(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=25,
            attack=3,
            magic=6,
            defense=4,
            magic_resistance=4,
            mana=20,
            **kwargs
        )
        self.name = 'Sapo do Bananal Podre'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1268562912247808102/DALLE_2024-08-01_10.35.59_-_A_fantasy_RPG_style_image_of_a_giant_frog_in_a_swamp._The_frog_has_a_semi-realistic_appearance_with_warty_skin_large_eyes_and_a_powerful_stance_but_1.webp?ex=66ace0c7&is=66ab8f47&hm=6eb7ba9907e1333db2900117b53dfa49c0c68a2854002fffb282664c0fc8f545&'
        self.id = 18
        
        self.ability = {
            "name" : "Lambida toxica",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=3,
            wood=3,
            iron=1,
            runes=0,
            xp=4,
            equipment=None,
            level=kwargs.get('level', 1)
        )
    
    
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=25)
    
    
class EnemyReiDoPoleiroDeBanana(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=40,
            attack=8,
            magic=4,
            defense=4,
            magic_resistance=4,
            mana=30,
            **kwargs
        )
        self.name = 'Rei do Poleiro de Banana'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1270861381377196122/DALLE_2024-08-07_18.49.16_-_A_fantasy_RPG_style_image_of_a_majestic_and_aggressive_falcon_wearing_a_crown_in_an_attack_pose_in_a_medieval_training_field._The_falcon_has_a_semi-r.webp?ex=66b53d64&is=66b3ebe4&hm=66d0931e2ae968f944a4c8096103b240b5c1eed8c1a6c25bbd83227686175a42&'
        self.id = 19
        
        self.ability = {
            "name" : "Mordida feroz",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=40,
            wood=2,
            iron=0,
            runes=0,
            xp=10,
            equipment=None,
            level=kwargs.get('level', 1)
        )


    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_attack(enemy, power=25)


class EnemyMutanteDoPantanoSimio(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=20,
            attack=8,
            magic=8,
            defense=8,
            magic_resistance=8,
            mana=20,
            **kwargs
        )
        self.name = 'Mutante do Pantano Símio'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1274507494021926922/DALLE_2024-08-17_20.17.35_-_A_fantasy_RPG_style_image_of_a_mutant_creature_in_a_swamp._The_mutant_has_a_semi-realistic_appearance_with_twisted_limbs_deformed_features_and_a_men.webp?ex=66c28119&is=66c12f99&hm=586a77227c104e6f4259343fe7bd5be92c3d1c0827f5a9fa0e5654d26d298467&'
        self.id = 20
        
        self.ability = {
            "name" : "Mordida acida",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=2,
            wood=2,
            iron=0,
            runes=0,
            xp=7,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=15)
            
        
class EnemyGuardiaoDoDossel(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=40,
            attack=7,
            magic=12,
            defense=8,
            magic_resistance=8,
            mana=20,
            **kwargs
        )
        self.name = 'Guardiao do Dossel'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1274496898652307456/DALLE_2024-08-17_19.35.31_-_A_fantasy_RPG_style_image_of_the_Forest_Guardian_a_colossal_ancient_spirit_that_protects_the_heart_of_the_forest._The_Guardian_appears_as_a_giant_tre.webp?ex=66c2773b&is=66c125bb&hm=55b134ff10042c0206f142c3ad37bd6797bdd052e31bed78e969c17e44c9a67c&'
        self.id = 21
        
        self.ability = {
            "name" : "Golpe de raiz",
            "cost" : 5,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=47,
            wood=4,
            iron=3,
            runes=1,
            xp=30,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=5)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=15)


class EnemyAncestralDasDunas(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=30,
            attack=6,
            magic=15,
            defense=8,
            magic_resistance=8,
            mana=20,
            **kwargs
        )
        self.name = 'Ancestral das Dunas'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1274508615423885363/DALLE_2024-08-17_20.22.09_-_A_fantasy_RPG_style_image_of_the_Lord_of_the_Sands_a_colossal_being_made_of_living_sand_capable_of_controlling_sandstorms_and_changing_shape_at_will.webp?ex=66c28225&is=66c130a5&hm=9c6188a8aa88f180d98f5f1bd076c46f6004ef2baa036fb6c70a0104eb55c6c5&'
        self.id = 22
        
        self.ability = {
            "name" : "Afogamento na areia",
            "cost" : 20,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=45,
            wood=4,
            iron=4,
            runes=1,
            xp=40,
            equipment=None,
            level=kwargs.get('level', 1)
        )


    @mana_ability(cost=20)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=20)
    
    
class EnemySoldadoDeLamaDoBandoCaido(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=25,
            attack=8,
            magic=6,
            defense=9,
            magic_resistance=9,
            mana=10,
            **kwargs
        )
        self.name = 'Soldados de Lama do Bando Caido'
        self.image = 'https://cdn.discordapp.com/attachments/474702643625984021/1274510561773748345/DALLE_2024-08-17_20.29.51_-_A_fantasy_RPG_style_image_of_Mudmen_humanoid_creatures_made_of_mud_and_swamp_vegetation._The_Mudmen_have_semi-realistic_appearances_with_bodies_compo.webp?ex=66c283f5&is=66c13275&hm=c9fda5950afee518b56976b2875e4eb996e0cdc4f7c32b2b7f962ed2db3c1be9&'
        self.id = 23
        
        self.ability = {
            "name" : "Arremesso de lama",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=5,
            wood=2,
            iron=1,
            runes=0,
            xp=8,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=15)
    
    
class EnemyXamaDaLuaBanana(BaseHero):
    def __init__(self, **kwargs):
        super().__init__(
            hp=40,
            attack=7,
            magic=15,
            defense=8,
            magic_resistance=8,
            mana=30,
            **kwargs
        )
        self.name = 'Xama da Lua Banana'
        self.image = ''
        self.id = 24
        
        self.ability = {
            "name" : "Maldicao",
            "cost" : 10,
            "func" : self.special_attack
        }

        self.loot = Loot(
            nex=60,
            wood=8,
            iron=3,
            runes=2,
            xp=70,
            equipment=None,
            level=kwargs.get('level', 1)
        )
        
        
    @mana_ability(cost=10)
    def special_attack(self, enemy):
        return self.do_magic(enemy, power=20)
    
        
enemy_dict = {
    1 : EnemyTotemDoBando,
    2 : EnemyGosmaDeBanana,
    3 : EnemySimioDeMagma,
    4 : EnemyMacacoOssudo,
    5 : EnemySaguiSaqueador,
    6 : EnemyMicoVigia,
    7 : EnemyLarvaDaCopa,
    8 : EnemySombraDoGalho,
    9 : EnemyRatoDoCeleiroDeBanana,
    10 : EnemyBugioDePresas,
    11 : EnemyGorilaSaqueador,
    12 : EnemyUrsoDasBananeiras,
    13 : EnemyJiboiaDoCipo,
    14 : EnemyAncestralEnfaixado,
    15 : EnemyEscorpiaoDaCasca,
    16 : EnemyGuardiaoDeAreiaDoCacho,
    17 : EnemyCatadoresDoSol,
    18 : EnemySapoDoBananalPodre,
    19 : EnemyReiDoPoleiroDeBanana,
    20 : EnemyMutanteDoPantanoSimio,
    21 : EnemyGuardiaoDoDossel,
    22 : EnemyAncestralDasDunas,
    23 : EnemySoldadoDeLamaDoBandoCaido,
    24 : EnemyXamaDaLuaBanana
}
