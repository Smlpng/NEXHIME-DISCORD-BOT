import discord
from discord.ext import commands
import asyncio

class RemindMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="remindme",
        aliases=["lembrete", "lembrar", "remind"],
        help="Envia um lembrete após um tempo (ex: 10m, 2h, 1d)."
    )
    async def remindme(self, ctx: commands.Context, time: str, *, message: str):
        """Envia uma mensagem de lembrete após o tempo especificado na DM."""
        try:
            # Converte o tempo para segundos
            time_seconds = self.convert_time_to_seconds(time)
            if time_seconds is None:
                await ctx.reply("Formato de tempo inválido. Use algo como '5m', '1h', '2d'.", mention_author=False)
                return

            # Envia uma mensagem informando que o lembrete foi configurado
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send(f"Lembrete configurado para `{time}`.")
            else:
                await ctx.reply(f"Lembrete configurado para `{time}`.", mention_author=False)

            # Espera pelo tempo especificado e envia o lembrete
            await asyncio.sleep(time_seconds)

            # Envia o lembrete na DM do usuário
            await ctx.author.send(f"Lembrete: {message}")

        except Exception as e:
            await ctx.send(f"Erro ao configurar o lembrete: {e}")

    def convert_time_to_seconds(self, time_str: str):
        """Converte o tempo no formato 'Xd', 'Xh', 'Xm', 'Xs' para segundos."""
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = time_str[-1]
        if unit not in time_units:
            return None
        try:
            value = int(time_str[:-1])
            return value * time_units[unit]
        except ValueError:
            return None

async def setup(bot):
    await bot.add_cog(RemindMe(bot))
