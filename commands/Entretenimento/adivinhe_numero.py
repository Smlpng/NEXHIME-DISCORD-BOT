import random

from discord.ext import commands


class AdivinheNumero(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="adivinhe_número", aliases=["guessnumber", "número"], help="Tente adivinhar um número em um intervalo.")
    async def adivinhe_numero(self, ctx: commands.Context, inicio: int = 1, fim: int = 20):
        if inicio >= fim:
            return await ctx.reply("O inicio precisa ser menor que o fim.")
        secret = random.randint(inicio, fim)
        await ctx.reply(f"Pensei em um número entre **{inicio}** e **{fim}**. Use `!palpite <número>` para tentar.")
        self.bot.guess_number_games = getattr(self.bot, "guess_number_games", {})
        self.bot.guess_number_games[(ctx.guild.id if ctx.guild else 0, ctx.author.id)] = (inicio, fim, secret)

    @commands.command(name="palpite", help="Envia um palpite para o jogo adivinhe_número.")
    async def palpite(self, ctx: commands.Context, numero: int):
        games = getattr(self.bot, "guess_number_games", {})
        key = (ctx.guild.id if ctx.guild else 0, ctx.author.id)
        if key not in games:
            return await ctx.reply("Você não tem nenhum jogo de número ativo.")
        inicio, fim, secret = games[key]
        if numero == secret:
            games.pop(key, None)
            return await ctx.reply(f"Acertou. O número era **{secret}**.")
        tip = "maior" if número < secret else "menor"
        await ctx.reply(f"Errou. O número secreto e {tip} que **{número}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdivinheNumero(bot))