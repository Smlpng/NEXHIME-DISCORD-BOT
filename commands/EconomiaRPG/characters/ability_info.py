import discord
from discord import Embed


def abilities_embed(hero: object, inte):
    embed = Embed(title=f"Habilidades de {inte.user.name}", color=discord.Color.blue())
    embed.add_field(name="Classe 🏹", value=hero.classname, inline=True)
    embed.add_field(name="Golpe", value="**Acerta o inimigo**\nPODER: 10\nCUSTO: 0", inline=False)
    embed.set_image(url=hero.image)
    match hero.classname:
        case "Mago":
            embed.add_field(name="Chama magica", value="**Causa dano de fogo**\nPODER: 10\nCUSTO: 5", inline=False)
            if hero.level >= 10:
                embed.add_field(name="Cura", value="**Recupera vida com base na magia do usuario**\nCUSTO: 10", inline=False)
            if hero.level >= 25:
                embed.add_field(name="Feitico ancestral", value="**Causa dano massivo**\nPODER: 10\nCUSTO: 20", inline=False)
        case "Assassino":
            embed.add_field(name="Golpe brutal", value="**Ataca o inimigo com as laminas**\nPODER: 20\nCUSTO: 5", inline=False)
            if hero.level >= 10:
                embed.add_field(name="Sacrificio", value="**Sacrifica vida para causar dano massivo**\nPODER: 35\nCUSTO: 33% da vida", inline=False)
            if hero.level >= 25:
                embed.add_field(name="Quebra-escudo", value="**Reduz a defesa do inimigo com base na magia do usuario**\nCUSTO: 10", inline=False)
        case "Tanque":
            embed.add_field(name="Esmagar", value="**Esmaga o inimigo**\nPODER: 20\nCUSTO: 10", inline=False)
            if hero.level >= 10:
                embed.add_field(name="Fortalecer", value="**Aumenta as defesas**\nCUSTO: 10", inline=False)
                
    if hero.weapon:
        embed.add_field(name=hero.weapon.name + " (Ataque da arma)", value=hero.weapon.attack_description, inline=False)
                
    
                
    return embed