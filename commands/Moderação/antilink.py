import re
from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "antilink.json"


URL_RE = re.compile(r"(https?://\S+|discord\.gg/\S+|discord\.com/invite/\S+)", re.IGNORECASE)


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _get_guild_conf(guild_id: int) -> dict:
    data = _load()
    g = data.get(str(guild_id))
    if not isinstance(g, dict):
        g = {"enabled": False, "whitelist": []}
    g.setdefault("enabled", False)
    g.setdefault("whitelist", [])
    if not isinstance(g["whitelist"], list):
        g["whitelist"] = []
    return g


class AntiLink(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="antilink",
        help="Anti-link: antilink on|off; antilink whitelist add|remove|list",
    )
    @commands.has_permissions(manage_guild=True)
    async def antilink(self, ctx: commands.Context, acao: str, subacao: str | None = None, canal: discord.TextChannel | None = None):
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona em servidores.", mention_author=False)
        acao = (acao or "").strip().lower()
        subacao = (subacao or "").strip().lower() if subacao else None

        data = _load()
        gid = str(ctx.guild.id)
        conf = _get_guild_conf(ctx.guild.id)

        if acao in {"on", "enable", "ativar"}:
            conf["enabled"] = True
            data[gid] = conf
            _save(data)
            return await ctx.reply("✅ Anti-link ativado.", mention_author=False)

        if acao in {"off", "disable", "desativar"}:
            conf["enabled"] = False
            data[gid] = conf
            _save(data)
            return await ctx.reply("✅ Anti-link desativado.", mention_author=False)

        if acao == "whitelist":
            if subacao in {"add", "adicionar"}:
                if canal is None:
                    return await ctx.reply("Use: `antilink whitelist add #canal`.", mention_author=False)
                cid = int(canal.id)
                if cid not in conf["whitelist"]:
                    conf["whitelist"].append(cid)
                data[gid] = conf
                _save(data)
                return await ctx.reply(f"✅ {canal.mention} liberado no anti-link.", mention_author=False)

            if subacao in {"remove", "remover"}:
                if canal is None:
                    return await ctx.reply("Use: `antilink whitelist remove #canal`.", mention_author=False)
                cid = int(canal.id)
                conf["whitelist"] = [x for x in conf["whitelist"] if int(x) != cid]
                data[gid] = conf
                _save(data)
                return await ctx.reply(f"✅ {canal.mention} removido da whitelist.", mention_author=False)

            if subacao in {"list", "listar"}:
                if not conf["whitelist"]:
                    return await ctx.reply("Whitelist vazia.", mention_author=False)
                lines = [f"- <#{cid}>" for cid in conf["whitelist"][:30]]
                return await ctx.reply("Canais liberados:\n" + "\n".join(lines), mention_author=False)

            return await ctx.reply("Use: `antilink whitelist add|remove|list`.", mention_author=False)

        enabled = "ativado" if conf.get("enabled") else "desativado"
        await ctx.reply(f"Anti-link está **{enabled}**. Use `antilink on`/`antilink off`.", mention_author=False)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return

        conf = _get_guild_conf(message.guild.id)
        if not conf.get("enabled"):
            return
        if int(message.channel.id) in {int(x) for x in conf.get("whitelist", [])}:
            return
        if message.author.guild_permissions.manage_messages:
            return
        if not message.guild.me.guild_permissions.manage_messages:
            return
        if not message.channel.permissions_for(message.guild.me).manage_messages:
            return

        content = message.content or ""
        if not URL_RE.search(content):
            return
        try:
            await message.delete()
        except Exception:
            return
        try:
            await message.channel.send(
                f"🚫 {message.author.mention}, links não são permitidos aqui.",
                delete_after=8,
            )
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiLink(bot))
