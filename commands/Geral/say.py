from discord.ext import commands
import discord

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", aliases=["dizer", "falar", "echo"], description="Faz o bot repetir uma mensagem.")
    async def say(self, ctx: commands.Context, *, mensagem: str):
        # Deleta a mensagem original apenas se não for slash command
        if ctx.message and ctx.interaction is None:
            await ctx.message.delete()
        await ctx.send(mensagem)


async def setup(bot: commands.Bot):
    await bot.add_cog(Say(bot))
