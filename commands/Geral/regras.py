import json
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "rules.json"
DEFAULT_RULES = [
    "Respeite todos os membros.",
    "Evite spam, flood e divulgação sem permissão.",
    "Conteúdo ilegal, gore ou discriminatório não é permitido.",
    "Siga as orientações da staff.",
]


def _load_rules() -> list[str]:
    if not DB_PATH.exists():
        return DEFAULT_RULES
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list) and data:
            return [str(item) for item in data]
    except Exception:
        pass
    return DEFAULT_RULES


def _save_rules(entries: list[str]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


class Regras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="regras", aliases=["rules"], invoke_without_command=True, help="Mostra ou gerencia as regras do servidor.")
    async def regras(self, ctx: commands.Context):
        rules = _load_rules()
        embed = discord.Embed(title=f"Regras de {ctx.guild.name}", color=discord.Color.blue())
        embed.description = "\n".join(f"**{index}.** {rule}" for index, rule in enumerate(rules, start=1))
        await ctx.reply(embed=embed)

    @regras.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def regras_add(self, ctx: commands.Context, *, texto: str):
        rules = _load_rules()
        rules.append(texto)
        _save_rules(rules)
        await ctx.reply("Regra adicionada.")

    @regras.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def regras_remove(self, ctx: commands.Context, index: int):
        rules = _load_rules()
        real_index = index - 1
        if real_index < 0 or real_index >= len(rules):
            return await ctx.reply("Indice invalido.")
        removed = rules.pop(real_index)
        _save_rules(rules)
        await ctx.reply(f"Regra removida: {removed}")

    @regras.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def regras_set(self, ctx: commands.Context, index: int, *, texto: str):
        rules = _load_rules()
        real_index = index - 1
        if real_index < 0 or real_index >= len(rules):
            return await ctx.reply("Indice invalido.")
        rules[real_index] = texto
        _save_rules(rules)
        await ctx.reply("Regra atualizada.")

    @regras.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def regras_clear(self, ctx: commands.Context):
        _save_rules(DEFAULT_RULES)
        await ctx.reply("Regras resetadas para o padrao.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Regras(bot))