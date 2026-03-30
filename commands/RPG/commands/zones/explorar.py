import json
from pathlib import Path

import discord
from discord.ext import commands

from commands.RPG.game.zones.encounters import get_enemy_from_zone
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import ensure_profile, get_active_zone_id, record_enemy_seen
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR, resolve_zone_name


DB_PATH = Path("DataBase") / "rpg_explore_cooldown.json"
COOLDOWN_SECONDS = 5 * 60


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


class Explorar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="explorar", description="Explora a zona atual e encontra um inimigo (cooldown).")
    async def explorar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        now_ts = int(discord.utils.utcnow().timestamp())
        data = _load()
        last_ts = int(data.get(str(inte.user.id), 0) or 0)
        available_at = last_ts + COOLDOWN_SECONDS
        if available_at > now_ts:
            return await inte.response.send_message(
                f"⏳ Você já explorou recentemente. Tente novamente <t:{available_at}:R>.",
                ephemeral=True,
            )

        zone_id = get_active_zone_id(inte.user.id)
        if zone_id is None:
            zone_id = 0

        enemy = get_enemy_from_zone(int(zone_id))
        record_enemy_seen(inte.user.id, getattr(enemy, "id", 0) or 0)

        msg = None
        try:
            msg = enemy.loot.drop(inte.user.id, name=inte.user.display_name)
        except Exception:
            msg = f"Você encontrou **{getattr(enemy, 'name', 'um inimigo')}** (nível {getattr(enemy, 'level', '?')}) e voltou em segurança."

        zone_name = resolve_zone_name(int(zone_id))
        embed = discord.Embed(title="🧭 Exploração", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Local", value=zone_name, inline=False)
        embed.add_field(name="Encontro", value=f"**{getattr(enemy, 'name', 'Inimigo')}** (nível {getattr(enemy, 'level', '?')})", inline=False)
        embed.add_field(name="Resultado", value=msg, inline=False)
        embed.set_footer(text=f"Cooldown: {COOLDOWN_SECONDS // 60} min")

        data[str(inte.user.id)] = now_ts
        _save(data)
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Explorar(bot))
