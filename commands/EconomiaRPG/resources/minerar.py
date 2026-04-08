import json
import random
import time
from pathlib import Path

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "mining_cooldown.json"
COOLDOWN_SECONDS = 10 * 60


def _load() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text("{}", encoding="utf-8")
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


class Minerar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="minerar", aliases=["mineiron"], help="Mineracao periodica para ganhar ferro e um pouco de nex.")
    async def minerar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para minerar.")

        data = _load()
        now_ts = int(time.time())
        last_ts = int(data.get(str(inte.user.id), 0) or 0)
        if last_ts + COOLDOWN_SECONDS > now_ts:
            return await inte.response.send_message(
                f"Voce ja minerou recentemente. Tente novamente <t:{last_ts + COOLDOWN_SECONDS}:R>.",
                ephemeral=True,
            )

        iron_reward = random.randint(2, 6)
        nex_reward = random.randint(15, 45)
        rune_reward = 1 if random.random() <= 0.08 else 0
        update_active_hero_resources(inte.user.id, iron=iron_reward, nex=nex_reward, runes=rune_reward)
        data[str(inte.user.id)] = now_ts
        _save(data)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="⛏️ Mineracao", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} voltou da mina com novos recursos."
        embed.add_field(name="Ferro", value=f"+{iron_reward}", inline=True)
        embed.add_field(name="Nex", value=f"+{nex_reward}", inline=True)
        embed.add_field(name="Runas", value=f"+{rune_reward}", inline=True)
        embed.add_field(name="Total de ferro", value=str(hero["iron"]), inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Minerar(bot))