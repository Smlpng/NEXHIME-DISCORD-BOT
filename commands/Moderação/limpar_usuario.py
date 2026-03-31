import discord
from discord.ext import commands


class LimparUsuario(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="limpar_usuario",
        aliases=["clear_user", "purge_user"],
        help="Limpa N mensagens de um usuário no canal (máx 100).",
    )
    @commands.has_permissions(manage_messages=True)
    async def limpar_usuario(self, ctx: commands.Context, membro: discord.Member, quantidade: int):
        if not hasattr(ctx.channel, "purge"):
            return await ctx.reply("Este comando funciona em canais onde posso apagar mensagens.", mention_author=False)
        quantidade = max(1, min(int(quantidade), 100))

        def check(msg: discord.Message) -> bool:
            return msg.author.id == membro.id

        deleted = await ctx.channel.purge(limit=quantidade + 1, check=check)
        removed = max(0, len(deleted))
        await ctx.send(
            f"Removidas {removed} mensagens de {membro.mention}.",
            delete_after=5,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LimparUsuario(bot))
