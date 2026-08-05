import json
from pathlib import Path

import discord
from discord.ext import commands


WARNS_PATH = Path("DataBase") / "mod_state.json"


def _load_warns() -> dict:
    WARNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not WARNS_PATH.exists():
        WARNS_PATH.write_text("{}", encoding="utf-8")
    try:
        return json.loads(WARNS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


class Historico(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="historico", aliases=["modhistory"], help="Mostra o historico basico de moderacao de um membro.")
    @commands.has_permissions(manage_messages=True)
    async def historico(self, ctx: commands.Context, membro: discord.Member):
        data = _load_warns()
        warns = data.get(str(ctx.guild.id), {}).get(str(membro.id), []) if ctx.guild else []
        active_timeout = getattr(membro, "timed_out_until", None)
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted") if ctx.guild else None
        has_muted_role = bool(muted_role and muted_role in membro.roles)

        embed = discord.Embed(title=f"Historico de {membro}", color=discord.Color.orange())
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="Conta criada", value=discord.utils.format_dt(membro.created_at, style="F"), inline=False)
        if membro.joined_at is not None:
            embed.add_field(name="Entrou no servidor", value=discord.utils.format_dt(membro.joined_at, style="F"), inline=False)

        embed.add_field(name="Total de avisos", value=str(len(warns)), inline=True)
        embed.add_field(name="Timeout ativo", value="Sim" if active_timeout else "Nao", inline=True)
        embed.add_field(name="Cargo Muted", value="Sim" if has_muted_role else "Nao", inline=True)

        if active_timeout:
            embed.add_field(name="Timeout ate", value=discord.utils.format_dt(active_timeout, style="F"), inline=False)

        if warns:
            recent = []
            for index, warn in enumerate(warns[-5:], start=max(1, len(warns) - 4)):
                timestamp = warn.get("timestamp")
                when = f"<t:{timestamp}:f>" if timestamp else "data desconhecida"
                recent.append(f"**{index}.** {warn.get('reason', 'Sem motivo')}\nPor <@{warn.get('by', 0)}> em {when}")
            embed.add_field(name="Ultimos avisos", value="\n\n".join(recent)[:1024], inline=False)
        else:
            embed.add_field(name="Ultimos avisos", value="Nenhum aviso registrado.", inline=False)

        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Historico(bot))