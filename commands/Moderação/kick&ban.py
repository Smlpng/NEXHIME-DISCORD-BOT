import discord
from discord.ext import commands

class KickBan(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _hierarchy_ok(self, ctx: commands.Context, target: discord.Member) -> bool:
        return ctx.author.top_role > target.top_role and ctx.guild.me.top_role > target.top_role

    @commands.hybrid_command(name="expulsar", aliases=["kick"], description="Expulsa um membro do servidor.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, membro: discord.Member, *, motivo: str = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não é possível moderar alguém com cargo igual/superior.")
        await membro.kick(reason=motivo or f"Por {ctx.author}")
        await ctx.reply(f"{membro} expulso.")

    @commands.hybrid_command(name="banir", aliases=["ban"], description="Bane um membro do servidor.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, membro: discord.Member, *, motivo: str = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não é possível moderar alguém com cargo igual/superior.")
        await membro.ban(reason=motivo or f"Por {ctx.author}")
        await ctx.reply(f"{membro} banido.")

    @commands.hybrid_command(name="desbanir", aliases=["unban"], description="Desbane um usuário pelo nome#tag ou ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, identificador: str):
        # aceita ID ou nome#discriminador
        bans = await ctx.guild.bans()
        target = None
        if identificador.isdigit():
            uid = int(identificador)
            for e in bans:
                if e.user.id == uid:
                    target = e.user
                    break
        else:
            name, _, disc = identificador.partition("#")
            for e in bans:
                if e.user.name == name and str(e.user.discriminator) == disc:
                    target = e.user
                    break
        if not target:
            return await ctx.reply("Usuário não encontrado na lista de banidos.")
        await ctx.guild.unban(target, reason=f"Por {ctx.author}")
        await ctx.reply(f"{target} desbanido.")

    @commands.hybrid_command(name="softban", description="Softban: bane e desbane para limpar mensagens.")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx: commands.Context, membro: discord.Member, *, motivo: str = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não é possível moderar alguém com cargo igual/superior.")
        await ctx.guild.ban(membro, reason=motivo or f"Por {ctx.author}", delete_message_days=1)
        await ctx.guild.unban(membro, reason="Softban revert")
        await ctx.reply(f"{membro} recebeu softban.")

async def setup(bot: commands.Bot):
    await bot.add_cog(KickBan(bot))
