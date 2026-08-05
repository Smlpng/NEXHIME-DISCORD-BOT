import json
from pathlib import Path

import discord
from discord.ext import commands


WARN_DB = Path("DataBase") / "mod_state.json"
NOTE_DB = Path("DataBase") / "mod_notes.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


class Audit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="audit", aliases=["modaudit"], help="Resumo rapido de moderacao de um membro.")
    @commands.has_permissions(manage_messages=True)
    async def audit(self, ctx: commands.Context, membro: discord.Member):
        warn_data = _load_json(WARN_DB)
        note_data = _load_json(NOTE_DB)
        warns = warn_data.get(str(ctx.guild.id), {}).get(str(membro.id), [])
        notes = note_data.get(str(ctx.guild.id), {}).get(str(membro.id), [])

        timeout_until = None
        communication_disabled_until = getattr(membro, "timed_out_until", None)
        if communication_disabled_until is None:
            communication_disabled_until = getattr(membro, "communication_disabled_until", None)
        if communication_disabled_until is not None:
            timeout_until = communication_disabled_until

        embed = discord.Embed(title=f"Audit de {membro}", color=discord.Color.orange())
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="ID", value=str(membro.id), inline=True)
        embed.add_field(name="Conta criada", value=membro.created_at.strftime("%d/%m/%Y %H:%M UTC"), inline=True)
        embed.add_field(name="Entrou no servidor", value=membro.joined_at.strftime("%d/%m/%Y %H:%M UTC") if membro.joined_at else "Desconhecido", inline=True)
        embed.add_field(name="Avisos", value=str(len(warns)), inline=True)
        embed.add_field(name="Notas internas", value=str(len(notes)), inline=True)
        embed.add_field(name="Em call", value=membro.voice.channel.mention if membro.voice and membro.voice.channel else "Nao", inline=True)
        embed.add_field(name="Timeout", value=f"Ate {discord.utils.format_dt(timeout_until, 'R')}" if timeout_until else "Nao", inline=False)

        if warns:
            last_warn = warns[-1]
            embed.add_field(
                name="Ultimo aviso",
                value=f"<t:{last_warn.get('timestamp', 0)}:f> por <@{last_warn.get('by', 0)}>\n{last_warn.get('reason', 'Sem motivo')}",
                inline=False,
            )
        if notes:
            last_note = notes[-1]
            embed.add_field(
                name="Ultima nota",
                value=f"<t:{last_note.get('timestamp', 0)}:f> por <@{last_note.get('by', 0)}>\n{last_note.get('text', 'Sem texto')}",
                inline=False,
            )
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Audit(bot))