import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "timezones.json"


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


class Timezone(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _resolve_timezone(name: str) -> ZoneInfo | None:
        try:
            return ZoneInfo(name)
        except Exception:
            return None

    @commands.group(name="timezone", invoke_without_command=True, help="Configura ou consulta seu fuso horario.")
    async def timezone(self, ctx: commands.Context):
        data = _load()
        current = data.get(str(ctx.author.id))
        if current is None:
            return await ctx.reply("Voce ainda nao configurou timezone. Use `!timezone set America/Sao_Paulo`.")
        await ctx.reply(f"Seu timezone atual e `{current}`.")

    @timezone.command(name="set", help="Define seu timezone. Ex: !timezone set America/Sao_Paulo")
    async def timezone_set(self, ctx: commands.Context, *, timezone_name: str):
        tz = self._resolve_timezone(timezone_name)
        if tz is None:
            return await ctx.reply("Timezone invalido. Exemplo valido: `America/Sao_Paulo`.")
        data = _load()
        data[str(ctx.author.id)] = timezone_name
        _save(data)
        now_local = datetime.now(tz).strftime("%d/%m/%Y %H:%M")
        await ctx.reply(f"Timezone salvo como `{timezone_name}`. Agora local: {now_local}.")

    @timezone.command(name="remove", aliases=["clear"], help="Remove seu timezone salvo.")
    async def timezone_remove(self, ctx: commands.Context):
        data = _load()
        if str(ctx.author.id) in data:
            data.pop(str(ctx.author.id), None)
            _save(data)
            return await ctx.reply("Seu timezone foi removido.")
        await ctx.reply("Voce nao tinha timezone salvo.")

    @commands.command(name="horario", aliases=["timeuser", "localtime"], help="Mostra o horario local de um usuario que configurou timezone.")
    async def horario(self, ctx: commands.Context, membro: discord.Member | None = None):
        target = membro or ctx.author
        data = _load()
        timezone_name = data.get(str(target.id))
        if timezone_name is None:
            return await ctx.reply("Esse usuario ainda nao configurou timezone.")
        tz = self._resolve_timezone(timezone_name)
        if tz is None:
            return await ctx.reply("O timezone salvo para esse usuario esta invalido.")
        now_local = datetime.now(tz)
        embed = discord.Embed(title=f"Horario local de {target}", color=discord.Color.blurple())
        embed.add_field(name="Timezone", value=timezone_name, inline=False)
        embed.add_field(name="Agora", value=now_local.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Timezone(bot))