from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document

DB_PATH = Path("DataBase") / "mod_state.json"

def _load():
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}

def _save(data): 
    save_json_document(DB_PATH, data)

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _can_moderate(ctx: commands.Context, membro: discord.Member) -> bool:
        if membro == ctx.author:
            return False
        if membro.bot:
            return False
        if membro == ctx.guild.owner:
            return False
        return ctx.author.top_role > membro.top_role and ctx.guild.me.top_role > membro.top_role

    @commands.command(name="avisar", aliases=["warn"], help="Avisa um usuário (registra ocorrência).")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, membro: discord.Member, *, motivo: str):
        if not self._can_moderate(ctx, membro):
            return await ctx.reply("Não é possível avisar este membro por causa da hierarquia, por ser bot ou por ser você mesmo.")
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        g = data.setdefault(gid, {})
        lst = g.setdefault(uid, [])
        lst.append({
            "by": ctx.author.id,
            "reason": motivo,
            "timestamp": int(discord.utils.utcnow().timestamp()),
        })
        _save(data)
        await ctx.reply(f"{membro.mention} recebeu um aviso: {motivo}\nTotal de avisos: {len(lst)}")

    @commands.command(name="remover_aviso", aliases=["unwarn"], help="Remove o último aviso de um usuário.")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx: commands.Context, membro: discord.Member):
        if not self._can_moderate(ctx, membro):
            return await ctx.reply("Não é possível gerenciar os avisos deste membro.")
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        if gid in data and uid in data[gid] and data[gid][uid]:
            data[gid][uid].pop()
            _save(data)
            remaining = len(data[gid][uid])
            return await ctx.reply(f"Último aviso de {membro.mention} removido. Restam {remaining} avisos.")
        await ctx.reply("Este usuário não possui avisos.")

    @commands.command(name="avisos", aliases=["warns"], help="Mostra os avisos de um usuário.")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx: commands.Context, membro: discord.Member):
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        lst = data.get(gid, {}).get(uid, [])
        if not lst:
            return await ctx.reply("Sem avisos.")
        desc = "\n".join(
            f"**{index}.** Por <@{warning['by']}> em <t:{warning.get('timestamp', 0)}:f>\n{warning['reason']}"
            for index, warning in enumerate(lst, start=1)
        )
        emb = discord.Embed(title=f"Avisos de {membro}", description=desc, color=discord.Color.orange())
        emb.set_footer(text=f"Total de avisos: {len(lst)}")
        await ctx.reply(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))
