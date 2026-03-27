import discord
from discord.ext import commands

class CheckHibridos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="check_hibridos", aliases=["ch", "faltam_hibridos"], description="Lista todos os comandos que ainda NÃO são híbridos (slash)")
    @commands.has_permissions(administrator=True)
    async def check_hibridos(self, ctx: commands.Context):
        non_hybrid_cmds = []

        # itera por todos os comandos carregados no bot
        for command in self.bot.commands:
            # Pula o help padrão ou comandos escondidos desnecessariamente se tiver
            if command.name == "help" and not command.cog:
                continue
                
            # Verifica se o comando é uma instância de HybridCommand
            if not isinstance(command, commands.HybridCommand):
                non_hybrid_cmds.append(command)

        if not non_hybrid_cmds:
            embed = discord.Embed(
                title="✅ Tudo Atualizado!",
                description="Todos os seus comandos já foram convertidos para híbridos e suportam Slash Commands (`/`)!",
                color=discord.Color.green()
            )
            return await ctx.send(embed=embed)

        # Agrupa os comandos que não são híbridos por Cog/Pasta
        grouped_cmds = {}
        for cmd in non_hybrid_cmds:
            cog_name = cmd.cog_name or "Sem Categoria/Main"
            if cog_name not in grouped_cmds:
                grouped_cmds[cog_name] = []
            grouped_cmds[cog_name].append(f"`{cmd.name}`")

        # Ordena as categorias e comandos
        sorted_grouped = {k: sorted(v) for k, v in sorted(grouped_cmds.items())}

        desc = f"Encontrei **{len(non_hybrid_cmds)} comandos** que ainda são os padrões antigos (apenas texto/prefixo).\n\n"
        
        for cog, cmds in sorted_grouped.items():
            desc += f"📁 **{cog}**\n {', '.join(cmds)}\n\n"

        embed = discord.Embed(
            title="⚠️ Comandos Falta Serem Híbridos",
            description=desc,
            color=discord.Color.red()
        )
        embed.set_footer(text="Atenção: Apenas administradores podem ver este painel.")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CheckHibridos(bot))
