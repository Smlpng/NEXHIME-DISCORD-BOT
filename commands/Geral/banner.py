import discord
from discord.ext import commands


class Banner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="banner", aliases=["profilebanner"], help="Mostra o banner de um usuario.")
    async def banner(self, ctx: commands.Context, membro: discord.Member | discord.User | None = None):
        target = membro or ctx.author
        try:
            fetched_user = await self.bot.fetch_user(target.id)
        except discord.HTTPException:
            fetched_user = target

        banner_asset = getattr(fetched_user, "banner", None)
        accent_color = getattr(fetched_user, "accent_color", None)
        if banner_asset is None and accent_color is None:
            return await ctx.reply("Esse usuario nao possui banner nem cor de perfil configurada.")

        embed = discord.Embed(title=f"Banner de {target}", color=accent_color or discord.Color.blurple())
        if banner_asset is not None:
            embed.set_image(url=banner_asset.url)
        else:
            embed.description = f"Esse usuario nao tem banner, mas a cor de perfil dele e {accent_color}."
        embed.set_footer(text=f"ID: {target.id}")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Banner(bot))