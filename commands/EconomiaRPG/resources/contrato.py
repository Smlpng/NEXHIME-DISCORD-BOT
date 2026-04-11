import random
import time
from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "contracts.json"
COOLDOWN_SECONDS = 4 * 60 * 60
CONTRACTS = [
    ("Escoltar um mercador", {"nex": 180, "wood": 2}),
    ("Patrulhar a fronteira", {"nex": 210, "iron": 2}),
    ("Caçar uma criatura rara", {"nex": 260, "runes": 1}),
    ("Recuperar suprimentos perdidos", {"nex": 170, "wood": 3, "iron": 1}),
]


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


class Contrato(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="contrato", aliases=["contract"], help="Conclui um contrato periodico por recompensa.")
    async def contrato(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para assumir contratos.")

        db = _load()
        now_ts = int(time.time())
        last_ts = int(db.get(str(inte.user.id), 0) or 0)
        if last_ts + COOLDOWN_SECONDS > now_ts:
            return await inte.response.send_message(
                f"Voce ja concluiu um contrato recentemente. Tente novamente <t:{last_ts + COOLDOWN_SECONDS}:R>.",
                ephemeral=True,
            )

        contract_name, rewards = random.choice(CONTRACTS)
        update_active_hero_resources(inte.user.id, **rewards)
        db[str(inte.user.id)] = now_ts
        _save(db)
        rewards_text = ", ".join(f"+{value} {key}" for key, value in rewards.items())

        embed = discord.Embed(title="Contrato concluido", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Missao", value=contract_name, inline=False)
        embed.add_field(name="Recompensa", value=rewards_text, inline=False)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Contrato(bot))