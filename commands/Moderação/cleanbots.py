import discord
from discord.ext import commands


class CleanBots(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="cleanbots", aliases=["limparbots"], help="Limpa mensagens recentes de bots e webhooks.")
    @commands.has_permissions(manage_messages=True)
    async def cleanbots(self, ctx: commands.Context, quantidade: int = 50):
        quantidade = max(1, min(quantidade, 500))
        deleted = await ctx.channel.purge(limit=quantidade, check=lambda m: m.author.bot or m.webhook_id is not None)
        await ctx.send(f"{len(deleted)} mensagens de bots/webhooks foram removidas.", delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(CleanBots(bot))