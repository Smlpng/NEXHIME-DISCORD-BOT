import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="serverinfo", help="Mostra informações do servidor.")
    async def serverinfo(self, ctx: commands.Context):
        g = ctx.guild
        emb = discord.Embed(title=f"Servidor: {g.name}", color=discord.Color.green())
        emb.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        emb.add_field(name="ID", value=str(g.id))
        emb.add_field(name="Dono", value=g.owner.mention if g.owner else "Desconhecido")
        emb.add_field(name="Membros", value=str(g.member_count))
        emb.add_field(name="Canais", value=f"Texto: {len(g.text_channels)} | Voz: {len(g.voice_channels)}", inline=False)
        emb.add_field(name="Cargos", value=str(len(g.roles)))
        emb.add_field(name="Criado em", value=g.created_at.strftime("%Y-%m-%d %H:%M UTC"))
        await ctx.reply(embed=emb)

async def setup(bot: commands.Bot):
    # Função exigida pela extensão; precisa ser async e usar await
    await bot.add_cog(ServerInfo(bot))