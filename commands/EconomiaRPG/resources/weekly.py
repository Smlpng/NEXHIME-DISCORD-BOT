import json
import random
import time
from pathlib import Path

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import ensure_profile, get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "weekly_claims.json"
COOLDOWN_SECONDS = 7 * 24 * 60 * 60


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


class Weekly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weekly", aliases=["semanal"], help="Coleta sua recompensa semanal de nex.")
    async def weekly(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("VocÃª precisa ter um herÃ³i ativo para resgatar a recompensa semanal.")

        now_ts = time.time()
        data = _load()
        last_ts = float(data.get(str(inte.user.id), 0) or 0)
        available_at = last_ts + COOLDOWN_SECONDS
        if available_at > now_ts:
            await inte.response.send_message(
                f"VocÃª jÃ¡ resgatou seu semanal. Tente novamente <t:{int(available_at)}:R>.",
                ephemeral=True,
            )
            return

        reward = random.randint(1200, 1800)
        ok = update_active_hero_resources(inte.user.id, nex=reward)
        if not ok:
            return await inte.response.send_message("NÃ£o consegui aplicar a recompensa agora. Tente novamente.")

        data[str(inte.user.id)] = now_ts
        _save(data)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="Recompensa semanal", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} recebeu **{reward} nex** pela recompensa semanal."
        embed.add_field(name="Carteira atual", value=f"{hero['nex']} nex", inline=True)
        embed.add_field(name="PrÃ³ximo resgate", value="Daqui a 7 dias", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Weekly(bot))
