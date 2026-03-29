import time

import discord
from discord.ext import commands

from commands.RPG.game.items.armors import armor_dict
from commands.RPG.game.items.weapons import weapon_dict
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import (
    ensure_profile,
    get_active_hero,
    get_active_quest_log,
    get_active_zone_id,
    get_advancements,
    list_active_inventory,
    save_active_quest_log,
    update_active_hero_resources,
)


QUESTS = {
    "cacador_iniciante": {
        "name": "Cacador Iniciante",
        "description": "Derrote 5 inimigos nas zonas do reino.",
        "type": "kills",
        "goal": 5,
        "requirements": {"level": 1},
        "rewards": {"nex": 60, "wood": 3},
    },
    "ferreiro_aprendiz": {
        "name": "Ferreiro Aprendiz",
        "description": "Melhore 1 equipamento na forja.",
        "type": "upgrades",
        "goal": 1,
        "requirements": {"level": 1},
        "rewards": {"nex": 40, "iron": 2},
    },
    "mercador_do_bando": {
        "name": "Mercador do Bando",
        "description": "Gaste 200 nex com o seu heroi.",
        "type": "nex_spent",
        "goal": 200,
        "requirements": {"level": 1},
        "rewards": {"wood": 4, "iron": 1, "runes": 1},
    },
    "colecionador": {
        "name": "Colecionador de Equipamentos",
        "description": "Tenha pelo menos 3 equipamentos no inventario ativo.",
        "type": "inventory_count",
        "goal": 3,
        "requirements": {"level": 1},
        "rewards": {"nex": 80, "runes": 1},
    },
    "ruinas_cobertas": {
        "name": "Rumo as Ruinas",
        "description": "Alcance a zona 2 e explore alem do campo inicial.",
        "type": "zone_reach",
        "goal": 2,
        "requirements": {"level": 10},
        "rewards": {"nex": 120, "wood": 5, "iron": 3},
    },
}


PROGRESS_FIELDS = {
    "kills": "kills",
    "upgrades": "upgrades",
    "nex_spent": "nex_spent",
}


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def resolve_quest(query: str | None):
    if not query:
        return None, None
    normalized = normalize_text(query)
    for quest_id, quest in QUESTS.items():
        if normalize_text(quest_id) == normalized or normalize_text(quest["name"]) == normalized:
            return quest_id, quest
    return None, None


def get_inventory_display_name(item: dict) -> str:
    if item["type"] == 1:
        return weapon_dict[item["item_id"]]().name
    return armor_dict[item["item_id"]]().name


def get_inventory_count(user_id: int) -> int:
    return len(list_active_inventory(user_id))


def get_progress_value(user_id: int, quest_type: str, active_data: dict) -> int:
    if quest_type in PROGRESS_FIELDS:
        advancements = get_advancements(user_id) or {"kills": 0, "upgrades": 0, "nex_spent": 0}
        baseline = int(active_data.get("snapshot", {}).get(PROGRESS_FIELDS[quest_type], 0))
        return max(0, int(advancements.get(PROGRESS_FIELDS[quest_type], 0)) - baseline)
    if quest_type == "inventory_count":
        return get_inventory_count(user_id)
    if quest_type == "zone_reach":
        return int(get_active_zone_id(user_id) or 0)
    return 0


def build_progress_text(user_id: int, quest: dict, active_data: dict) -> tuple[bool, str]:
    progress = get_progress_value(user_id, quest["type"], active_data)
    goal = int(quest["goal"])
    if quest["type"] == "zone_reach":
        return progress >= goal, f"Zona atual: {progress}/{goal}"
    return progress >= goal, f"Progresso: {progress}/{goal}"


def check_requirements(hero: dict, quest: dict) -> tuple[bool, str | None]:
    level_required = int(quest.get("requirements", {}).get("level", 1))
    if int(hero.get("level", 1)) < level_required:
        return False, f"Voce precisa estar no nivel {level_required} para aceitar essa missao."
    return True, None


def grant_rewards(user_id: int, quest: dict) -> str:
    rewards = quest.get("rewards", {})
    update_active_hero_resources(
        user_id,
        nex=int(rewards.get("nex", 0)),
        wood=int(rewards.get("wood", 0)),
        iron=int(rewards.get("iron", 0)),
        runes=int(rewards.get("runes", 0)),
    )
    parts = []
    if rewards.get("nex"):
        parts.append(f"{rewards['nex']} nex")
    if rewards.get("wood"):
        parts.append(f"{rewards['wood']} madeira")
    if rewards.get("iron"):
        parts.append(f"{rewards['iron']} ferro")
    if rewards.get("runes"):
        parts.append(f"{rewards['runes']} runas")
    return ", ".join(parts) if parts else "sem recompensas"


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="quests")
    async def quests(self, ctx, acao: str | None = None, *, alvo: str | None = None):
        """Gerencia as missoes adaptadas ao RPG atual."""
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        hero = get_active_hero(inte.user.id)

        if hero is None:
            return await inte.response.send_message("Seu perfil ainda nao esta pronto para usar quests.")

        quest_log = get_active_quest_log(inte.user.id) or {"active": {}, "completed": []}

        if not acao:
            return await inte.response.send_message(embed=self.build_overview_embed(inte.user.id, hero, quest_log))

        action = normalize_text(acao)
        if action == "disponiveis":
            return await inte.response.send_message(embed=self.build_available_embed(inte.user.id, hero, quest_log))

        if not alvo:
            return await inte.response.send_message(
                "Uso: /quests, /quests disponiveis, /quests ver <id>, /quests aceitar <id>, /quests entregar <id> ou /quests cancelar <id>."
            )

        quest_id, quest = resolve_quest(alvo)
        if quest is None:
            return await inte.response.send_message("Missao nao encontrada.")

        if action == "ver":
            return await inte.response.send_message(embed=self.build_details_embed(inte.user.id, quest_id, quest, quest_log))

        if action == "aceitar":
            if quest_id in quest_log["completed"]:
                return await inte.response.send_message("Voce ja concluiu essa missao.")
            if quest_id in quest_log["active"]:
                return await inte.response.send_message("Essa missao ja esta ativa.")

            valid, message = check_requirements(hero, quest)
            if not valid:
                return await inte.response.send_message(message)

            snapshot = {}
            if quest["type"] in PROGRESS_FIELDS:
                advancements = get_advancements(inte.user.id) or {"kills": 0, "upgrades": 0, "nex_spent": 0}
                snapshot[PROGRESS_FIELDS[quest["type"]]] = int(advancements.get(PROGRESS_FIELDS[quest["type"]], 0))

            quest_log["active"][quest_id] = {
                "accepted_at": int(time.time()),
                "snapshot": snapshot,
            }
            save_active_quest_log(inte.user.id, quest_log)
            return await inte.response.send_message(f"Missao aceita: {quest['name']}.")

        if action == "cancelar":
            if quest_id not in quest_log["active"]:
                return await inte.response.send_message("Essa missao nao esta ativa.")
            quest_log["active"].pop(quest_id, None)
            save_active_quest_log(inte.user.id, quest_log)
            return await inte.response.send_message(f"Missao cancelada: {quest['name']}.")

        if action == "entregar":
            active_data = quest_log["active"].get(quest_id)
            if active_data is None:
                return await inte.response.send_message("Essa missao nao esta ativa.")

            complete, progress_text = build_progress_text(inte.user.id, quest, active_data)
            if not complete:
                return await inte.response.send_message(f"Voce ainda nao completou essa missao. {progress_text}")

            reward_text = grant_rewards(inte.user.id, quest)
            quest_log["active"].pop(quest_id, None)
            if quest_id not in quest_log["completed"]:
                quest_log["completed"].append(quest_id)
            save_active_quest_log(inte.user.id, quest_log)
            return await inte.response.send_message(f"Missao concluida: {quest['name']}. Recompensas: {reward_text}.")

        await inte.response.send_message(
            "Uso: /quests, /quests disponiveis, /quests ver <id>, /quests aceitar <id>, /quests entregar <id> ou /quests cancelar <id>."
        )

    def build_overview_embed(self, user_id: int, hero: dict, quest_log: dict) -> discord.Embed:
        embed = discord.Embed(title="Quadro de Missoes", color=discord.Color.blue())
        embed.add_field(
            name="Disponiveis",
            value=self._build_available_text(hero, quest_log),
            inline=False,
        )
        embed.add_field(
            name="Ativas",
            value=self._build_active_text(user_id, quest_log),
            inline=False,
        )
        completed = quest_log.get("completed", [])
        embed.add_field(
            name="Concluidas",
            value="\n".join(f"- {QUESTS[quest_id]['name']}" for quest_id in completed[:10]) or "Nenhuma missao concluida ainda.",
            inline=False,
        )
        embed.set_footer(text="Use quests ver <id>, quests aceitar <id> ou quests entregar <id>.")
        return embed

    def build_available_embed(self, user_id: int, hero: dict, quest_log: dict) -> discord.Embed:
        embed = discord.Embed(title="Missoes Disponiveis", color=discord.Color.green())
        embed.description = self._build_available_text(hero, quest_log)
        return embed

    def build_details_embed(self, user_id: int, quest_id: str, quest: dict, quest_log: dict) -> discord.Embed:
        embed = discord.Embed(title=quest["name"], description=quest["description"], color=discord.Color.gold())
        embed.add_field(name="ID", value=quest_id, inline=True)
        embed.add_field(name="Objetivo", value=f"{quest['type']} ({quest['goal']})", inline=True)
        embed.add_field(name="Recompensas", value=grant_rewards_preview(quest), inline=False)
        active_data = quest_log.get("active", {}).get(quest_id)
        if active_data:
            _, progress_text = build_progress_text(user_id, quest, active_data)
            embed.add_field(name="Progresso atual", value=progress_text, inline=False)
        return embed

    def _build_available_text(self, hero: dict, quest_log: dict) -> str:
        lines = []
        for quest_id, quest in QUESTS.items():
            if quest_id in quest_log.get("completed", []) or quest_id in quest_log.get("active", {}):
                continue
            valid, _ = check_requirements(hero, quest)
            if valid:
                lines.append(f"- {quest_id}: {quest['name']}")
        return "\n".join(lines) or "Nenhuma missao disponivel agora."

    def _build_active_text(self, user_id: int, quest_log: dict) -> str:
        lines = []
        for quest_id, active_data in quest_log.get("active", {}).items():
            quest = QUESTS.get(quest_id)
            if quest is None:
                continue
            _, progress_text = build_progress_text(user_id, quest, active_data)
            lines.append(f"- {quest['name']}: {progress_text}")
        return "\n".join(lines) or "Nenhuma missao ativa."


def grant_rewards_preview(quest: dict) -> str:
    rewards = quest.get("rewards", {})
    parts = []
    if rewards.get("nex"):
        parts.append(f"{rewards['nex']} nex")
    if rewards.get("wood"):
        parts.append(f"{rewards['wood']} madeira")
    if rewards.get("iron"):
        parts.append(f"{rewards['iron']} ferro")
    if rewards.get("runes"):
        parts.append(f"{rewards['runes']} runas")
    return ", ".join(parts) or "Sem recompensas"


async def setup(bot):
    await bot.add_cog(Quests(bot))