import json
from pathlib import Path

import discord
from discord.ext import commands

DB_PATH = Path("DataBase") / "mod_state.json"

def _load():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        with DB_PATH.open("w", encoding="utf-8") as f:
            json.dump({}, f)
    with DB_PATH.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save(data): 
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(DB_PATH)

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

    @commands.hybrid_command(name="avisar", aliases=["warn"], description="Avisa um usuário (registra ocorrência).")
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

    @commands.hybrid_command(name="remover_aviso", aliases=["unwarn"], description="Remove o último aviso de um usuário.")
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

    @commands.hybrid_command(name="avisos", aliases=["warns"], description="Mostra os avisos de um usuário.")
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
