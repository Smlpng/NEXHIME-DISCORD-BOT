import ast
import operator

import discord
from discord.ext import commands


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_MAX_POWER = 1000


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left = _eval(node.left)
        right = _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POWER:
            raise ValueError("Expoente muito grande.")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Expressão não suportada.")


class Calc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="calc",
        aliases=["calcular", "calculadora"],
        help="Calcula uma expressão matemática. Ex: !calc 2 + 2 * 3",
    )
    async def calc(self, ctx: commands.Context, *, expressao: str):
        """Avalia uma expressão matemática simples de forma segura."""
        expressao = expressao.strip()
        try:
            tree = ast.parse(expressao, mode="eval")
            result = _eval(tree)
        except ZeroDivisionError:
            return await ctx.reply("❌ Divisão por zero.", mention_author=False)
        except (ValueError, TypeError, SyntaxError) as exc:
            return await ctx.reply(f"❌ Expressão inválida: {exc}", mention_author=False)
        except Exception:
            return await ctx.reply("❌ Não foi possível calcular essa expressão.", mention_author=False)

        formatted = f"{result:g}" if result == result else "NaN"
        embed = discord.Embed(
            title="🧮 Calculadora",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Expressão", value=f"`{expressao}`", inline=False)
        embed.add_field(name="Resultado", value=f"**{formatted}**", inline=False)
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Calc(bot))
