import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="trancar", aliases=["lock"], help="Bloqueia o canal atual para @everyone.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
        await ctx.reply("Canal bloqueado.")

    @commands.command(name="destrancar", aliases=["unlock"], help="Desbloqueia o canal atual para @everyone.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
        await ctx.reply("Canal desbloqueado.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Lock(bot))
