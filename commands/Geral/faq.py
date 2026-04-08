import json
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "faq.json"
DEFAULT_FAQ = [
    {"question": "Qual é o prefixo do bot?", "answer": "Use o prefixo configurado no servidor ou mencione o bot."},
    {"question": "Como vejo os comandos?", "answer": "Use o comando help ou comandos."},
    {"question": "Como falar com a staff?", "answer": "Use sugestao, tickets ou chame um moderador."},
]


def _load_faq() -> list[dict]:
    if not DB_PATH.exists():
        return DEFAULT_FAQ
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list) and data:
            return data
    except Exception:
        pass
    return DEFAULT_FAQ


def _save_faq(entries: list[dict]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


class FAQ(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="faq", invoke_without_command=True, help="Mostra ou gerencia perguntas frequentes.")
    async def faq(self, ctx: commands.Context):
        entries = _load_faq()
        embed = discord.Embed(title="FAQ", color=discord.Color.green())
        for entry in entries[:10]:
            embed.add_field(name=entry.get("question", "Pergunta"), value=entry.get("answer", "Sem resposta."), inline=False)
        await ctx.reply(embed=embed)

    @faq.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def faq_add(self, ctx: commands.Context, pergunta: str, *, resposta: str):
        entries = _load_faq()
        entries.append({"question": pergunta, "answer": resposta})
        _save_faq(entries)
        await ctx.reply("Entrada adicionada ao FAQ.")

    @faq.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def faq_remove(self, ctx: commands.Context, index: int):
        entries = _load_faq()
        real_index = index - 1
        if real_index < 0 or real_index >= len(entries):
            return await ctx.reply("Indice invalido.")
        removed = entries.pop(real_index)
        _save_faq(entries)
        await ctx.reply(f"Entrada removida: {removed.get('question', 'Pergunta')}.")

    @faq.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def faq_clear(self, ctx: commands.Context):
        _save_faq(DEFAULT_FAQ)
        await ctx.reply("FAQ resetado para o padrao.")


async def setup(bot: commands.Bot):
    await bot.add_cog(FAQ(bot))