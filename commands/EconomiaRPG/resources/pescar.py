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


DB_PATH = Path("DataBase") / "fishing_cooldown.json"
COOLDOWN_SECONDS = 8 * 60


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


class Pescar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="pescar", aliases=["fish"], help="Pesca para conseguir nex e as vezes runas.")
    async def pescar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para pescar.")

        data = _load()
        now_ts = int(time.time())
        last_ts = int(data.get(str(inte.user.id), 0) or 0)
        if last_ts + COOLDOWN_SECONDS > now_ts:
            return await inte.response.send_message(
                f"Voce ja pescou recentemente. Tente novamente <t:{last_ts + COOLDOWN_SECONDS}:R>.",
                ephemeral=True,
            )

        fish_name, nex_reward = random.choice(
            [
                ("Tilapia de guerra", 45),
                ("Bagre ancestral", 60),
                ("Peixe-lua do reino", 85),
                ("Monstro do lago", 130),
            ]
        )
        rune_reward = 1 if random.random() <= 0.12 else 0
        update_active_hero_resources(inte.user.id, nex=nex_reward, runes=rune_reward)
        data[str(inte.user.id)] = now_ts
        _save(data)

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="🎣 Pescaria", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} pescou **{fish_name}**."
        embed.add_field(name="Nex", value=f"+{nex_reward}", inline=True)
        embed.add_field(name="Runas", value=f"+{rune_reward}", inline=True)
        embed.add_field(name="Carteira", value=f"{hero['nex']} nex", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Pescar(bot))