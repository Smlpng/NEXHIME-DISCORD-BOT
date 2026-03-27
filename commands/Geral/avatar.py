import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", aliases=["av", "pfp", "foto"], description="Mostra o avatar de um usuário")
    async def avatar(self, ctx: commands.Context, membro: discord.Member = None):
        m = membro or ctx.author
        await ctx.reply(m.display_avatar.url)

async def setup(bot: commands.Bot):
    await bot.add_cog(Avatar(bot))
