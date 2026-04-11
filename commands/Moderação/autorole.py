from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "autorole.json"


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


class AutoRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="autorole", invoke_without_command=True, help="Configura o cargo automatico de entrada.")
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx: commands.Context):
        data = _load()
        role_id = data.get(str(ctx.guild.id))
        role = ctx.guild.get_role(int(role_id)) if role_id else None
        await ctx.reply(f"Autorole atual: {role.mention if role else 'nenhum'}")

    @autorole.command(name="set")
    @commands.has_permissions(manage_roles=True)
    async def autorole_set(self, ctx: commands.Context, cargo: discord.Role):
        if ctx.guild.me.top_role <= cargo:
            return await ctx.reply("Eu nao consigo aplicar esse cargo por causa da hierarquia.")
        data = _load()
        data[str(ctx.guild.id)] = cargo.id
        _save(data)
        await ctx.reply(f"Autorole definido para {cargo.mention}.")

    @autorole.command(name="clear", aliases=["off", "remove"])
    @commands.has_permissions(manage_roles=True)
    async def autorole_clear(self, ctx: commands.Context):
        data = _load()
        data.pop(str(ctx.guild.id), None)
        _save(data)
        await ctx.reply("Autorole removido.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = _load()
        role_id = data.get(str(member.guild.id))
        if not role_id:
            return
        role = member.guild.get_role(int(role_id))
        if role is None:
            return
        try:
            await member.add_roles(role, reason="Autorole")
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRole(bot))