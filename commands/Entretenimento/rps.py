import random

from discord.ext import commands


_VALID = {"pedra", "papel", "tesoura"}


def _winner(user_choice: str, bot_choice: str) -> int:
    if user_choice == bot_choice:
        return 0
    wins = {
        "pedra": "tesoura",
        "papel": "pedra",
        "tesoura": "papel",
    }
    return 1 if wins[user_choice] == bot_choice else -1


class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="rps",
        aliases=["ppt", "pedra_papel_tesoura"],
        help="Joga pedra/papel/tesoura contra o bot.",
    )
    async def rps(self, ctx: commands.Context, escolha: str):
        escolha = (escolha or "").strip().lower()
        if escolha not in _VALID:
            return await ctx.reply("Escolha `pedra`, `papel` ou `tesoura`.", mention_author=False)
        bot_choice = random.choice(sorted(_VALID))
        outcome = _winner(escolha, bot_choice)
        if outcome == 0:
            msg = "🤝 Empate!"
        elif outcome > 0:
            msg = "✅ Você ganhou!"
        else:
            msg = "❌ Você perdeu!"
        await ctx.reply(
            f"Você: **{escolha}** | Bot: **{bot_choice}**\n{msg}",
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(RPS(bot))
