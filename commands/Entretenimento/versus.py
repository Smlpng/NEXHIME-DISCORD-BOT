import discord
from discord.ext import commands


class Versus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="versus", aliases=["vs"], help="Abre uma disputa por voto entre dois usuarios em um tema.")
    async def versus(self, ctx: commands.Context, membro1: discord.Member, membro2: discord.Member, *, tema: str):
        if membro1.id == membro2.id:
            return await ctx.reply("Escolha duas pessoas diferentes para o versus.")
        embed = discord.Embed(title="Versus", description=f"**Tema:** {tema}", color=discord.Color.red())
        embed.add_field(name="Competidor 1", value=membro1.mention, inline=True)
        embed.add_field(name="Competidor 2", value=membro2.mention, inline=True)
        embed.set_footer(text="Reaja para votar.")
        message = await ctx.reply(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")


async def setup(bot: commands.Bot):
    await bot.add_cog(Versus(bot))