import json
import random
import time
from pathlib import Path

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, get_active_zone_id, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "collect_cooldown.json"
COOLDOWN_SECONDS = 12 * 60


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


class Coletar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="coletar", aliases=["gather"], help="Coleta recursos periodicamente conforme a zona do heroi.")
    async def coletar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa ter um heroi ativo para coletar recursos.")

        data = _load()
        now_ts = int(time.time())
        last_ts = int(data.get(str(inte.user.id), 0) or 0)
        if last_ts + COOLDOWN_SECONDS > now_ts:
            return await inte.response.send_message(
                f"Voce ja coletou recentemente. Tente novamente <t:{last_ts + COOLDOWN_SECONDS}:R>.",
                ephemeral=True,
            )

        zone = int(get_active_zone_id(inte.user.id) or 1)
        wood_reward = random.randint(zone, zone + 3)
        iron_reward = random.randint(max(0, zone - 1), zone + 1)
        nex_reward = random.randint(10 * zone, 25 * zone)
        rune_reward = 1 if random.random() <= min(0.04 * zone, 0.2) else 0

        update_active_hero_resources(inte.user.id, wood=wood_reward, iron=iron_reward, nex=nex_reward, runes=rune_reward)
        data[str(inte.user.id)] = now_ts
        _save(data)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="🌿 Coleta", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} fez uma coleta na zona {zone}."
        embed.add_field(name="Madeira", value=f"+{wood_reward}", inline=True)
        embed.add_field(name="Ferro", value=f"+{iron_reward}", inline=True)
        embed.add_field(name="Nex", value=f"+{nex_reward}", inline=True)
        embed.add_field(name="Runas", value=f"+{rune_reward}", inline=True)
        embed.add_field(name="Estoque atual", value=f"Madeira {hero['wood']} | Ferro {hero['iron']} | Runas {hero['runes']}", inline=False)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Coletar(bot))