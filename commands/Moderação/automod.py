import re
import time
from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "automod.json"
URL_RE = re.compile(r"https?://\S+|discord\.gg/\S+|discord\.com/invite/\S+", re.IGNORECASE)


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _default_conf() -> dict:
    return {
        "enabled": False,
        "max_mentions": 5,
        "caps_percent": 80,
        "min_caps_length": 12,
        "spam_threshold": 6,
        "spam_window": 8,
        "blocked_words": [],
        "whitelist": [],
    }


def _get_conf(guild_id: int) -> dict:
    data = _load()
    conf = data.get(str(guild_id), {})
    merged = _default_conf()
    if isinstance(conf, dict):
        merged.update(conf)
    merged["blocked_words"] = [str(word).lower() for word in merged.get("blocked_words", [])]
    merged["whitelist"] = [int(channel_id) for channel_id in merged.get("whitelist", [])]
    return merged


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_windows: dict[tuple[int, int], list[float]] = {}

    def _build_status_embed(self, guild: discord.Guild, conf: dict) -> discord.Embed:
        embed = discord.Embed(title=f"AutoMod - {guild.name}", color=discord.Color.blurple())
        embed.add_field(name="Status", value="Ativado" if conf["enabled"] else "Desativado", inline=True)
        embed.add_field(name="Spam", value=f"{conf['spam_threshold']} msgs / {conf['spam_window']}s", inline=True)
        embed.add_field(name="Mencoes", value=str(conf["max_mentions"]), inline=True)
        embed.add_field(name="Caps", value=f"{conf['caps_percent']}% em mensagens com 12+ letras", inline=True)
        blocked = ", ".join(conf["blocked_words"][:10]) or "Nenhuma"
        whitelist = "\n".join(f"- <#{channel_id}>" for channel_id in conf["whitelist"][:10]) or "Nenhum"
        embed.add_field(name="Palavras bloqueadas", value=blocked, inline=False)
        embed.add_field(name="Whitelist de canais", value=whitelist, inline=False)
        embed.set_footer(text="Uso: automod on|off, automod spam <qtd> [janela], automod mentions <qtd>, automod caps <percent>, automod palavra add|remove|list, automod whitelist add|remove|list")
        return embed

    def _persist_conf(self, guild_id: int, conf: dict) -> None:
        data = _load()
        data[str(guild_id)] = conf
        _save(data)

    @commands.command(name="automod", help="Configura protecoes automaticas de spam, caps, mencoes e blacklist.")
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx: commands.Context, acao: str | None = None, subacao: str | None = None, *resto):
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona apenas em servidores.", mention_author=False)

        conf = _get_conf(ctx.guild.id)
        action = (acao or "").strip().lower()
        sub = (subacao or "").strip().lower()

        if not action:
            return await ctx.reply(embed=self._build_status_embed(ctx.guild, conf), mention_author=False)

        if action in {"on", "ativar", "enable"}:
            conf["enabled"] = True
            self._persist_conf(ctx.guild.id, conf)
            return await ctx.reply("AutoMod ativado.", mention_author=False)

        if action in {"off", "desativar", "disable"}:
            conf["enabled"] = False
            self._persist_conf(ctx.guild.id, conf)
            return await ctx.reply("AutoMod desativado.", mention_author=False)

        if action == "spam":
            if sub.isdigit():
                conf["spam_threshold"] = max(3, int(sub))
                if resto and str(resto[0]).isdigit():
                    conf["spam_window"] = max(3, int(resto[0]))
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(
                    f"Protecao de spam ajustada para {conf['spam_threshold']} mensagens em {conf['spam_window']} segundos.",
                    mention_author=False,
                )
            return await ctx.reply("Use: automod spam <quantidade> [janela_em_segundos]", mention_author=False)

        if action == "mentions":
            if sub.isdigit():
                conf["max_mentions"] = max(1, int(sub))
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"Limite de mencoes ajustado para {conf['max_mentions']}.", mention_author=False)
            return await ctx.reply("Use: automod mentions <quantidade>", mention_author=False)

        if action == "caps":
            if sub.isdigit():
                conf["caps_percent"] = min(100, max(40, int(sub)))
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"Limite de caps ajustado para {conf['caps_percent']}%.", mention_author=False)
            return await ctx.reply("Use: automod caps <percentual>", mention_author=False)

        if action == "palavra":
            if sub in {"list", "listar"}:
                words = ", ".join(conf["blocked_words"]) or "Nenhuma palavra bloqueada."
                return await ctx.reply(f"Blacklist: {words}", mention_author=False)

            termo = " ".join(resto).strip().lower()
            if not termo:
                return await ctx.reply("Use: automod palavra add|remove <termo>", mention_author=False)
            if sub in {"add", "adicionar"}:
                if termo not in conf["blocked_words"]:
                    conf["blocked_words"].append(termo)
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"Palavra `{termo}` adicionada ao filtro.", mention_author=False)
            if sub in {"remove", "remover"}:
                conf["blocked_words"] = [word for word in conf["blocked_words"] if word != termo]
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"Palavra `{termo}` removida do filtro.", mention_author=False)
            return await ctx.reply("Use: automod palavra add|remove|list", mention_author=False)

        if action == "whitelist":
            channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else None
            if sub in {"list", "listar"}:
                lines = "\n".join(f"- <#{channel_id}>" for channel_id in conf["whitelist"]) or "Whitelist vazia."
                return await ctx.reply(lines, mention_author=False)
            if channel is None:
                return await ctx.reply("Use: automod whitelist add|remove #canal", mention_author=False)
            if sub in {"add", "adicionar"}:
                if channel.id not in conf["whitelist"]:
                    conf["whitelist"].append(channel.id)
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"{channel.mention} adicionado a whitelist.", mention_author=False)
            if sub in {"remove", "remover"}:
                conf["whitelist"] = [channel_id for channel_id in conf["whitelist"] if channel_id != channel.id]
                self._persist_conf(ctx.guild.id, conf)
                return await ctx.reply(f"{channel.mention} removido da whitelist.", mention_author=False)
            return await ctx.reply("Use: automod whitelist add|remove|list", mention_author=False)

        await ctx.reply(embed=self._build_status_embed(ctx.guild, conf), mention_author=False)

    async def _punish(self, message: discord.Message, reason: str) -> None:
        try:
            await message.delete()
        except Exception:
            return
        try:
            await message.channel.send(
                f"{message.author.mention}, sua mensagem foi removida pelo AutoMod: {reason}.",
                delete_after=8,
            )
        except Exception:
            pass

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        if message.author.guild_permissions.manage_messages:
            return
        if not message.guild.me.guild_permissions.manage_messages:
            return
        if not message.channel.permissions_for(message.guild.me).manage_messages:
            return

        conf = _get_conf(message.guild.id)
        if not conf["enabled"] or message.channel.id in conf["whitelist"]:
            return

        content = message.content or ""
        lowered = content.lower()

        if any(word and word in lowered for word in conf["blocked_words"]):
            return await self._punish(message, "conteudo bloqueado")

        mention_count = len(message.mentions) + len(message.role_mentions)
        if mention_count >= conf["max_mentions"]:
            return await self._punish(message, "excesso de mencoes")

        letters = [char for char in content if char.isalpha()]
        if len(letters) >= conf["min_caps_length"]:
            upper = sum(1 for char in letters if char.isupper())
            if upper and round((upper / len(letters)) * 100) >= conf["caps_percent"]:
                return await self._punish(message, "caps lock excessivo")

        if URL_RE.search(content) and "discord.gg/" in lowered:
            return await self._punish(message, "convite nao autorizado")

        now = time.time()
        key = (message.guild.id, message.author.id)
        window = [timestamp for timestamp in self.message_windows.get(key, []) if now - timestamp <= conf["spam_window"]]
        window.append(now)
        self.message_windows[key] = window[-max(conf["spam_threshold"], 1):]
        if len(window) >= conf["spam_threshold"]:
            self.message_windows[key] = []
            return await self._punish(message, "spam detectado")


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))