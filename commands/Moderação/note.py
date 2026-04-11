from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "mod_notes.json"


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


class Note(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="note", invoke_without_command=True, help="Gerencia notas internas da moderacao.")
    @commands.has_permissions(manage_messages=True)
    async def note(self, ctx: commands.Context):
        await ctx.reply("Use `note add`, `note list` ou `note clear`.")

    @note.command(name="add")
    @commands.has_permissions(manage_messages=True)
    async def note_add(self, ctx: commands.Context, membro: discord.Member, *, texto: str):
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        entry = {
            "by": ctx.author.id,
            "text": texto,
            "timestamp": int(discord.utils.utcnow().timestamp()),
        }
        data.setdefault(gid, {}).setdefault(uid, []).append(entry)
        _save(data)
        await ctx.reply(f"Nota registrada para {membro.mention}.")

    @note.command(name="list")
    @commands.has_permissions(manage_messages=True)
    async def note_list(self, ctx: commands.Context, membro: discord.Member):
        data = _load()
        notes = data.get(str(ctx.guild.id), {}).get(str(membro.id), [])
        if not notes:
            return await ctx.reply("Esse membro nao possui notas internas.")
        description = "\n\n".join(
            f"**{index}.** <t:{note['timestamp']}:f> por <@{note['by']}>\n{note['text']}"
            for index, note in enumerate(notes, start=1)
        )
        embed = discord.Embed(title=f"Notas de {membro}", description=description[:4096], color=discord.Color.orange())
        await ctx.reply(embed=embed)

    @note.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def note_clear(self, ctx: commands.Context, membro: discord.Member):
        data = _load()
        guild_notes = data.get(str(ctx.guild.id), {})
        if str(membro.id) not in guild_notes:
            return await ctx.reply("Esse membro nao possui notas internas.")
        guild_notes.pop(str(membro.id), None)
        _save(data)
        await ctx.reply(f"Notas internas de {membro.mention} removidas.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Note(bot))