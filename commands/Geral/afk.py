import json
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "afk.json"


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


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="afk", help="Marca você como AFK (ausente) com um motivo opcional.")
    async def afk(self, ctx: commands.Context, *, motivo: str | None = None):
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona em servidores.", mention_author=False)
        data = _load()
        gid = str(ctx.guild.id)
        g = data.setdefault(gid, {})
        g[str(ctx.author.id)] = {
            "reason": (motivo or "AFK").strip()[:200],
            "since": int(discord.utils.utcnow().timestamp()),
        }
        _save(data)
        await ctx.reply("✅ Você foi marcado como AFK.", mention_author=False)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return

        data = _load()
        gid = str(message.guild.id)
        g = data.get(gid, {})
        if not isinstance(g, dict):
            return

        author_id = str(message.author.id)
        if author_id in g:
            # Voltou do AFK
            g.pop(author_id, None)
            data[gid] = g
            _save(data)
            try:
                await message.channel.send(f"👋 {message.author.mention} bem-vindo(a) de volta! AFK removido.")
            except Exception:
                pass

        # Avisar quando mencionarem alguém AFK
        mentioned = {str(u.id) for u in message.mentions}
        hits = [uid for uid in mentioned if uid in g]
        if not hits:
            return

        lines = []
        for uid in hits[:5]:
            payload = g.get(uid, {})
            reason = payload.get("reason", "AFK")
            since = payload.get("since")
            since_text = f"<t:{since}:R>" if isinstance(since, int) else "(tempo desconhecido)"
            lines.append(f"<@{uid}> está AFK: **{reason}** ({since_text})")

        try:
            await message.channel.send("\n".join(lines))
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))
