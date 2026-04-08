import json
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "antiinvite.json"


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


class AntiInvite(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="antiinvite", invoke_without_command=True, help="Ativa ou desativa o bloqueio de convites do Discord.")
    @commands.has_permissions(manage_guild=True)
    async def antiinvite(self, ctx: commands.Context):
        data = _load()
        enabled = bool(data.get(str(ctx.guild.id), False))
        await ctx.reply(f"O antiinvite esta {'ativado' if enabled else 'desativado'} neste servidor.")

    @antiinvite.command(name="on")
    @commands.has_permissions(manage_guild=True)
    async def antiinvite_on(self, ctx: commands.Context):
        data = _load()
        data[str(ctx.guild.id)] = True
        _save(data)
        await ctx.reply("Antiinvite ativado.")

    @antiinvite.command(name="off")
    @commands.has_permissions(manage_guild=True)
    async def antiinvite_off(self, ctx: commands.Context):
        data = _load()
        data[str(ctx.guild.id)] = False
        _save(data)
        await ctx.reply("Antiinvite desativado.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        data = _load()
        if not data.get(str(message.guild.id), False):
            return
        if message.author.guild_permissions.manage_guild:
            return
        content = message.content.lower()
        if "discord.gg/" not in content and "discord.com/invite/" not in content:
            return
        try:
            await message.delete()
        except discord.HTTPException:
            return
        try:
            await message.channel.send(
                f"{message.author.mention}, convites de Discord nao sao permitidos aqui.",
                delete_after=6,
            )
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiInvite(bot))