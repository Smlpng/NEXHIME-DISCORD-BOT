import discord
from discord.ext import commands
from datetime import datetime

class UserInfo(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="userinfo", aliases=["whois", "user", "eu"], help="Mostra informações de um usuário.")
    async def userinfo(self, ctx: commands.Context, membro: discord.Member=None):
        m = membro or ctx.author
        emb = discord.Embed(title=f"Informações de {m}", color=m.color if hasattr(m, "color") else discord.Color.blurple())
        emb.set_thumbnail(url=m.display_avatar.url)
        emb.add_field(name="ID", value=str(m.id))
        emb.add_field(name="Bot", value="Sim" if m.bot else "Não")
        emb.add_field(name="Criou conta em", value=m.created_at.strftime("%Y-%m-%d %H:%M UTC"))
        if m.joined_at:
            emb.add_field(name="Entrou no servidor em", value=m.joined_at.strftime("%Y-%m-%d %H:%M UTC"), inline=False)
        roles = [r.mention for r in m.roles if r != m.guild.default_role]
        emb.add_field(name="Cargos", value=", ".join(roles) if roles else "Nenhum", inline=False)
        emb.set_footer(text=f"Requisitado por {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=emb)

async def setup(bot: commands.Bot):
    # Função exigida pela extensão; precisa ser async e usar await
    await bot.add_cog(UserInfo(bot))