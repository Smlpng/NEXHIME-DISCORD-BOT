from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "modlog.json"


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _is_moderation_command(ctx: commands.Context) -> bool:
    cmd = ctx.command
    if cmd is None:
        return False
    cog = cmd.cog
    if cog is None:
        return False
    mod = getattr(cog, "__module__", "")
    return ".Moderação." in mod or mod.split(".")[-2].lower() == "moderação"


class ModLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="modlog",
        help="Configura o canal de modlog. Use: modlog set #canal | modlog off",
    )
    @commands.has_permissions(manage_guild=True)
    async def modlog(self, ctx: commands.Context, acao: str, canal: discord.TextChannel | None = None):
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona em servidores.", mention_author=False)
        acao = (acao or "").strip().lower()
        data = _load()
        gid = str(ctx.guild.id)

        if acao == "set":
            if canal is None:
                return await ctx.reply("Use: `modlog set #canal`.", mention_author=False)
            data[gid] = int(canal.id)
            _save(data)
            return await ctx.reply(f"✅ Modlog definido para {canal.mention}.", mention_author=False)

        if acao in {"off", "disable", "desativar"}:
            data.pop(gid, None)
            _save(data)
            return await ctx.reply("✅ Modlog desativado.", mention_author=False)

        current = data.get(gid)
        if current:
            return await ctx.reply(f"Modlog atual: <#{current}>.\nUse `modlog set #canal` ou `modlog off`.", mention_author=False)
        return await ctx.reply("Modlog não está configurado. Use `modlog set #canal`.", mention_author=False)

    def _get_modlog_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        data = _load()
        cid = data.get(str(guild.id))
        if not cid:
            return None
        ch = guild.get_channel(int(cid))
        return ch if isinstance(ch, discord.TextChannel) else None

    @commands.Cog.listener("on_command_completion")
    async def on_command_completion(self, ctx: commands.Context):
        if ctx.guild is None:
            return
        if not _is_moderation_command(ctx):
            return
        ch = self._get_modlog_channel(ctx.guild)
        if ch is None:
            return
        if not ch.permissions_for(ctx.guild.me).send_messages:
            return

        embed = discord.Embed(title="🛡️ Moderação", color=discord.Color.orange())
        embed.add_field(name="Comando", value=f"`{ctx.command.qualified_name}`", inline=False)
        embed.add_field(name="Autor", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Canal", value=f"{ctx.channel.mention}", inline=True)
        embed.add_field(name="Mensagem", value=str(getattr(getattr(ctx, "message", None), "id", "-")), inline=True)
        try:
            await ch.send(embed=embed)
        except Exception:
            pass

    @commands.Cog.listener("on_member_ban")
    async def on_member_ban(self, guild: discord.Guild, user: discord.User | discord.Member):
        ch = self._get_modlog_channel(guild)
        if ch is None or not ch.permissions_for(guild.me).send_messages:
            return
        embed = discord.Embed(title="⛔ Ban", color=discord.Color.red())
        embed.description = f"{user} ({user.id}) foi banido."
        try:
            await ch.send(embed=embed)
        except Exception:
            pass

    @commands.Cog.listener("on_member_unban")
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        ch = self._get_modlog_channel(guild)
        if ch is None or not ch.permissions_for(guild.me).send_messages:
            return
        embed = discord.Embed(title="✅ Unban", color=discord.Color.green())
        embed.description = f"{user} ({user.id}) foi desbanido."
        try:
            await ch.send(embed=embed)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(ModLog(bot))
