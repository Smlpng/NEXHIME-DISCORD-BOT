import discord
from discord.ext import commands


class Slowmode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="slowmode",
        aliases=["modo_lento"],
        help="Define o slowmode do canal atual (em segundos). Use 0 para desligar.",
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, segundos: int):
        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.reply("Este comando funciona em canais de texto.", mention_author=False)
        segundos = max(0, min(int(segundos), 21600))
        try:
            await ctx.channel.edit(slowmode_delay=segundos, reason=f"Slowmode por {ctx.author}")
            if segundos == 0:
                await ctx.reply("✅ Slowmode desativado.", mention_author=False)
            else:
                await ctx.reply(f"✅ Slowmode definido para {segundos}s.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("Não tenho permissão para editar este canal.", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Slowmode(bot))
