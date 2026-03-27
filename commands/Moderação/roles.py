import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _hierarchy_ok(self, ctx: commands.Context, target: discord.Member) -> bool:
        return ctx.guild.me.top_role > target.top_role and ctx.author.top_role > target.top_role

    @commands.hybrid_command(name="adicionar_cargo", aliases=["addrole"], description="Adiciona um cargo a um membro.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: commands.Context, membro: discord.Member, cargo: discord.Role):
        if not self._hierarchy_ok(ctx, membro) or ctx.guild.me.top_role <= cargo:
            return await ctx.reply("Hierarquia não permite adicionar esse cargo ao membro.")
        await membro.add_roles(cargo, reason=f"Por {ctx.author}")
        await ctx.reply(f"Cargo {cargo.name} adicionado a {membro.mention}.")

    @commands.hybrid_command(name="remover_cargo", aliases=["removerole"], description="Remove um cargo de um membro.")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: commands.Context, membro: discord.Member, cargo: discord.Role):
        if not self._hierarchy_ok(ctx, membro) or ctx.guild.me.top_role <= cargo:
            return await ctx.reply("Hierarquia não permite remover esse cargo do membro.")
        await membro.remove_roles(cargo, reason=f"Por {ctx.author}")
        await ctx.reply(f"Cargo {cargo.name} removido de {membro.mention}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
