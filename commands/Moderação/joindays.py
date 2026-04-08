import discord
from discord.ext import commands


class JoinDays(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="joindays", aliases=["idadeconta", "idadeguild"], help="Mostra ha quantos dias um usuario criou a conta e entrou no servidor.")
    async def joindays(self, ctx: commands.Context, membro: discord.Member | None = None):
        target = membro or ctx.author
        now = discord.utils.utcnow()
        account_days = (now - target.created_at).days
        join_days = (now - target.joined_at).days if target.joined_at else None

        embed = discord.Embed(title=f"Tempo de {target}", color=discord.Color.blurple())
        embed.add_field(name="Conta criada", value=f"Ha {account_days} dias", inline=True)
        embed.add_field(name="Entrou no servidor", value=f"Ha {join_days} dias" if join_days is not None else "Desconhecido", inline=True)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(JoinDays(bot))