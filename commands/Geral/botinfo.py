import platform

import discord
from discord.ext import commands


class BotInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=["sobre", "info_bot"], help="Mostra informações do bot.")
    async def botinfo(self, ctx: commands.Context):
        prefix_count = len({command.qualified_name for command in self.bot.walk_commands()})
        slash_count = len({command.qualified_name for command in self.bot.tree.walk_commands()})

        embed = discord.Embed(title="Informações do bot", color=discord.Color.blurple())
        embed.add_field(name="👤 Usuário", value=str(self.bot.user) if self.bot.user else "(desconhecido)", inline=False)
        embed.add_field(name="🏠 Servidores", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(
            name="👥 Membros (aprox.)",
            value=str(sum(g.member_count or 0 for g in self.bot.guilds)),
            inline=True,
        )
        embed.add_field(name="⌨️ Comandos (prefixo)", value=str(prefix_count), inline=True)
        embed.add_field(name="/ Comandos (slash)", value=str(slash_count), inline=True)
        embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
        embed.add_field(name="📦 discord.py", value=getattr(discord, "__version__", "?"), inline=True)
        embed.add_field(name="📶 Latência", value=f"{round(self.bot.latency * 1000)} ms", inline=True)

        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotInfo(bot))
