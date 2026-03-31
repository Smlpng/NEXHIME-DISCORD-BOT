import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="limpar", aliases=["clear"], help="Limpa N mensagens (máx 100).")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, quantidade: int):
        quantidade = max(1, min(quantidade, 100))
        deleted = await ctx.channel.purge(limit=quantidade+1)
        await ctx.send(f"Removidas {len(deleted)-1} mensagens.", delete_after=5)

    @commands.command(name="nuke", help="Clona o canal e remove o antigo (limpeza completa).")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx: commands.Context):
        pos = ctx.channel.position
        new_chan = await ctx.channel.clone(reason=f"Nuke por {ctx.author}")
        await ctx.channel.delete(reason="Nuke")
        await new_chan.edit(position=pos)
        await new_chan.send("Canal foi reiniciado.")
        await new_chan.send("https://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464831")

async def setup(bot: commands.Bot):
    await bot.add_cog(Maintenance(bot))
