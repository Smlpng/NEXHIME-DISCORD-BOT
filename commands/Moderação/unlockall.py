import discord
from discord.ext import commands


class UnlockAll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="unlockall", help="Remove restricoes de envio do cargo everyone em todos os canais de texto.")
    @commands.has_permissions(manage_channels=True)
    async def unlockall(self, ctx: commands.Context):
        everyone = ctx.guild.default_role
        updated = 0
        for channel in ctx.guild.text_channels:
            overwrite = channel.overwrites_for(everyone)
            if overwrite.send_messages is None:
                continue
            overwrite.send_messages = None
            try:
                await channel.set_permissions(everyone, overwrite=overwrite, reason=f"Unlockall por {ctx.author}")
                updated += 1
            except discord.HTTPException:
                continue
        await ctx.reply(f"Unlockall concluido em {updated} canal(is).")


async def setup(bot: commands.Bot):
    await bot.add_cog(UnlockAll(bot))