import os
import json
import discord
from discord.ext import commands

DB_DIR = "databases"
DB_PATH = os.path.join(DB_DIR, "mod_state.json")

def _load():
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def _save(data): 
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_PATH)

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="avisar", aliases=["warn"], description="Avisa um usuário (registra ocorrência).")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, membro: discord.Member, *, motivo: str):
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        g = data.setdefault(gid, {})
        lst = g.setdefault(uid, [])
        lst.append({"by": ctx.author.id, "reason": motivo})
        _save(data)
        await ctx.reply(f"{membro.mention} recebeu um aviso: {motivo}")

    @commands.hybrid_command(name="remover_aviso", aliases=["unwarn"], description="Remove o último aviso de um usuário.")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx: commands.Context, membro: discord.Member):
        data = _load()
        gid = str(ctx.guild.id)
        uid = str(membro.id)
        if gid in data and uid in data[gid] and data[gid][uid]:
            data[gid][uid].pop()
            _save(data)
            return await ctx.reply(f"Último aviso de {membro.mention} removido.")
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
        desc = "\n".join(f"- Por <@{w['by']}>: {w['reason']}" for w in lst)
        emb = discord.Embed(title=f"Avisos de {membro}", description=desc, color=discord.Color.orange())
        await ctx.reply(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))
