import discord
from discord.ext import commands


class MassRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="massrole", invoke_without_command=True, help="Adiciona ou remove um cargo em lote.")
    @commands.has_permissions(manage_roles=True)
    async def massrole(self, ctx: commands.Context):
        await ctx.reply("Use `massrole add @cargo [@filtro]` ou `massrole remove @cargo [@filtro]`.")

    async def _run_massrole(self, ctx: commands.Context, mode: str, cargo: discord.Role, filtro: discord.Role | None):
        if ctx.guild.me.top_role <= cargo:
            return await ctx.reply("Eu nao consigo gerenciar esse cargo por causa da hierarquia.")
        if ctx.author.top_role <= cargo:
            return await ctx.reply("Voce nao pode aplicar em massa um cargo igual ou acima do seu.")

        affected = 0
        failed = 0
        candidates = [member for member in ctx.guild.members if not member.bot]
        if filtro is not None:
            candidates = [member for member in candidates if filtro in member.roles]

        for member in candidates:
            if ctx.guild.me.top_role <= member.top_role:
                failed += 1
                continue
            try:
                if mode == "add":
                    if cargo in member.roles:
                        continue
                    await member.add_roles(cargo, reason=f"Massrole add por {ctx.author}")
                else:
                    if cargo not in member.roles:
                        continue
                    await member.remove_roles(cargo, reason=f"Massrole remove por {ctx.author}")
                affected += 1
            except discord.HTTPException:
                failed += 1

        action = "adicionado a" if mode == "add" else "removido de"
        filtro_texto = f" com filtro em {filtro.mention}" if filtro is not None else ""
        await ctx.reply(f"Cargo {cargo.mention} {action} {affected} membro(s){filtro_texto}. Falhas: {failed}.")

    @massrole.command(name="add")
    @commands.has_permissions(manage_roles=True)
    async def massrole_add(self, ctx: commands.Context, cargo: discord.Role, filtro: discord.Role | None = None):
        await self._run_massrole(ctx, "add", cargo, filtro)

    @massrole.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def massrole_remove(self, ctx: commands.Context, cargo: discord.Role, filtro: discord.Role | None = None):
        await self._run_massrole(ctx, "remove", cargo, filtro)


async def setup(bot: commands.Bot):
    await bot.add_cog(MassRole(bot))