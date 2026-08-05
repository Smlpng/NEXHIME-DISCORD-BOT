import os, json, random
import discord
from discord.ext import commands

DB_DIR = "DataBase"
DB_PATH = os.path.join(DB_DIR, "quotes.json")

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

class Quotes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="citação", aliases=["quotes"], help="Salva uma citação para este servidor.")
    async def quote(self, ctx: commands.Context, *, texto: str):
        data = _load()
        gid = str(ctx.guild.id)
        lst = data.setdefault(gid, [])
        lst.append({"by": ctx.author.id, "text": texto})
        _save(data)
        await ctx.reply("Citação salva.")

    @commands.command(name="remover_citação", aliases=["delete_quote"], help="Remove uma citação pelo índice (veja o comando ver_citação).")
    @commands.has_permissions(manage_messages=True)
    async def delquote(self, ctx: commands.Context, indice: int):
        data = _load()
        gid = str(ctx.guild.id)
        lst = data.get(gid, [])
        if 1 <= indice <= len(lst):
            removed = lst.pop(indice-1)
            _save(data)
            await ctx.reply(f"Removida: {removed['text']}")
        else:
            await ctx.reply("Índice inválido.")

    @commands.command(name="ver_citação", aliases=["show_quotes"], help="Mostra uma citação (por índice ou aleatória).")
    async def showquote(self, ctx: commands.Context, indice: int = None):
        data = _load()
        gid = str(ctx.guild.id)
        lst = data.get(gid, [])
        if not lst:
            return await ctx.reply("Não há citações salvas.")
        if indice is None:
            q = random.choice(lst)
            idx = lst.index(q) + 1
        else:
            if not (1 <= indice <= len(lst)):
                return await ctx.reply("Índice inválido.")
            q = lst[indice-1]
            idx = indice
        author = f"<@{q['by']}>" if "by" in q else "Desconhecido"
        await ctx.reply(f"[{idx}] {q['text']} — {author}")

async def setup(bot: commands.Bot):
    # Função exigida pela extensão; precisa ser async e usar await
    await bot.add_cog(Quotes(bot))