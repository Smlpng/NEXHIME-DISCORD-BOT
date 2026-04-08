import discord
from discord.ext import commands


class MemberCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="membercount", aliases=["membros", "contagem"], help="Mostra a contagem detalhada de membros do servidor.")
    async def membercount(self, ctx: commands.Context):
        guild = ctx.guild
        humans = sum(1 for member in guild.members if not member.bot)
        bots = sum(1 for member in guild.members if member.bot)
        online = sum(1 for member in guild.members if member.status != discord.Status.offline)
        boosted = guild.premium_subscription_count or 0

        embed = discord.Embed(title=f"Membros de {guild.name}", color=discord.Color.green())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Total", value=str(guild.member_count), inline=True)
        embed.add_field(name="Humanos", value=str(humans), inline=True)
        embed.add_field(name="Bots", value=str(bots), inline=True)
        embed.add_field(name="Online", value=str(online), inline=True)
        embed.add_field(name="Boosts", value=str(boosted), inline=True)
        embed.add_field(name="Canais", value=f"Texto: {len(guild.text_channels)} | Voz: {len(guild.voice_channels)}", inline=True)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberCount(bot))