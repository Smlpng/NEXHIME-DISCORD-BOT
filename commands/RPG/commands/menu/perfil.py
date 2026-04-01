import time

import discord
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import (
    get_active_hero,
    get_active_quest_log,
    get_advancements,
    get_bank_balance,
    get_daily_remaining_seconds,
    list_active_inventory,
)
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR, resolve_zone_name


CLASS_NAMES = {
    1: "Mago",
    2: "Assassino",
    3: "Tanque",
}


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="perfil", aliases=["profile"])
    async def perfil(self, ctx, membro: discord.Member | None = None):
        """Mostra um resumo completo do heroi e da economia."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        alvo = membro or inte.user
        hero = get_active_hero(alvo.id)
        if hero is None:
            return await inte.response.send_message("Esse usuario nao possui heroi ativo no momento.")

        advancements = get_advancements(alvo.id) or {"kills": 0, "upgrades": 0, "nex_spent": 0}
        quest_log = get_active_quest_log(alvo.id) or {"active": {}, "completed": []}
        inventory = list_active_inventory(alvo.id)
        bank_balance = get_bank_balance(alvo.id)
        daily_remaining = get_daily_remaining_seconds(alvo.id, 86400, time.time())

        embed = discord.Embed(title=f"Perfil de {alvo.display_name}", color=RPG_PRIMARY_COLOR)
        embed.set_thumbnail(url=alvo.display_avatar.url)
        embed.add_field(name="Classe", value=CLASS_NAMES.get(hero.get("class"), str(hero.get("class"))), inline=True)
        embed.add_field(name="Nivel", value=str(hero.get("level", 0)), inline=True)
        embed.add_field(name="XP", value=str(hero.get("xp", 0)), inline=True)
        embed.add_field(name="Raca", value=str(hero.get("race") or "Nao definida"), inline=True)
        embed.add_field(name="Tribo", value=str(hero.get("tribe") or "Nao definida"), inline=True)
        embed.add_field(name="Zona", value=resolve_zone_name(hero.get("zone_id")), inline=True)
        embed.add_field(name="Carteira", value=f"{hero.get('nex', 0)} nex", inline=True)
        embed.add_field(name="Banco", value=f"{bank_balance} nex", inline=True)
        embed.add_field(name="Recursos", value=f"Madeira: {hero.get('wood', 0)}\nFerro: {hero.get('iron', 0)}\nRunas: {hero.get('runes', 0)}", inline=True)
        embed.add_field(name="Combate", value=f"Abates: {advancements.get('kills', 0)}\nMelhorias: {advancements.get('upgrades', 0)}\nNex gasto: {advancements.get('nex_spent', 0)}", inline=True)
        embed.add_field(name="Progresso", value=f"Itens no inventario: {len(inventory)}\nQuests ativas: {len(quest_log.get('active', {}))}\nQuests concluidas: {len(quest_log.get('completed', []))}", inline=True)
        if hero.get("title"):
            embed.add_field(name="Titulo ativo", value=str(hero["title"]), inline=False)
        if daily_remaining > 0:
            hours, remainder = divmod(daily_remaining, 3600)
            minutes, _ = divmod(remainder, 60)
            embed.set_footer(text=f"Daily disponivel em {hours}h {minutes}m.")
        else:
            embed.set_footer(text="Seu daily ja pode ser resgatado.")
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Perfil(bot))