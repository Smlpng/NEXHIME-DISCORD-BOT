import discord
from discord.ext import commands


class Nickname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _hierarchy_ok(ctx: commands.Context, target: discord.Member) -> bool:
        if target == ctx.author:
            return True
        if target == ctx.guild.owner:
            return False
        return ctx.author.top_role > target.top_role and ctx.guild.me.top_role > target.top_role

    @commands.hybrid_command(
        name="nickname",
        aliases=["nick"],
        description="Altera o apelido (nickname) de um membro.",
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx: commands.Context, membro: discord.Member, *, novo_nome: str):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não consigo mudar o nick por causa da hierarquia.", mention_author=False)
        novo_nome = (novo_nome or "").strip()
        if len(novo_nome) > 32:
            return await ctx.reply("O nick pode ter no máximo 32 caracteres.", mention_author=False)
        try:
            await membro.edit(nick=novo_nome, reason=f"Nick por {ctx.author}")
            await ctx.reply(f"✅ Nick de {membro.mention} atualizado.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("Não tenho permissão para alterar apelidos.", mention_author=False)

    @commands.hybrid_command(
        name="reset_nick",
        aliases=["resetnick", "unnick"],
        description="Remove o apelido de um membro (volta ao nome padrão).",
    )
    @commands.has_permissions(manage_nicknames=True)
    async def reset_nick(self, ctx: commands.Context, membro: discord.Member):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não consigo mudar o nick por causa da hierarquia.", mention_author=False)
        try:
            await membro.edit(nick=None, reason=f"Reset nick por {ctx.author}")
            await ctx.reply(f"✅ Nick de {membro.mention} resetado.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("Não tenho permissão para alterar apelidos.", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Nickname(bot))
