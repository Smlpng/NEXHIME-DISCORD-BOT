import discord
from discord.ext import commands

class CheckHibridos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="check_hibridos", aliases=["ch", "faltam_hibridos"], help="Verifica se ainda existe algum comando híbrido (slash) carregado.")
    @commands.has_permissions(administrator=True)
    async def check_hibridos(self, ctx: commands.Context):
        hybrid_cmds = []

        for command in self.bot.commands:
            if command.name == "help" and not command.cog:
                continue
            if isinstance(command, commands.HybridCommand):
                hybrid_cmds.append(command)

        if not hybrid_cmds:
            embed = discord.Embed(
                title="✅ Tudo Atualizado!",
                description="Nenhum comando híbrido (slash) foi encontrado. O bot está em modo **apenas prefixo**.",
                color=discord.Color.green()
            )
            return await ctx.send(embed=embed)

        # Agrupa os comandos híbridos por Cog/Pasta
        grouped_cmds = {}

        for cmd in hybrid_cmds:
            cog_name = cmd.cog_name or "Sem Categoria/Main"
            if cog_name not in grouped_cmds:
                grouped_cmds[cog_name] = []
            grouped_cmds[cog_name].append(f"`{cmd.name}`")

        # Ordena as categorias e comandos
        sorted_grouped = {k: sorted(v) for k, v in sorted(grouped_cmds.items())}

        desc = f"Encontrei **{len(hybrid_cmds)} comandos** que ainda estão como híbridos (slash + prefixo).\n\n"
        
        for cog, cmds in sorted_grouped.items():
            desc += f"📁 **{cog}**\n {', '.join(cmds)}\n\n"

        embed = discord.Embed(
            title="⚠️ Ainda existem comandos híbridos",
            description=desc,
            color=discord.Color.red()
        )
        embed.set_footer(text="Atenção: Apenas administradores podem ver este painel.")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CheckHibridos(bot))
