import discord
from discord.ext import commands
import random

# IDs especiais para lógica de compatibilidade
ID_MEMBRO1 = 0  # Sael
ID_MEMBRO2 = 0  # Outro user

class ShipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="shippar",
        aliases=["ship"],
        description="Calcula a compatibilidade entre duas pessoas.",
    )
    async def ship(self, ctx: commands.Context, nome1: str = None, nome2: str = None):
        """Ja desejou saber se você e seu par darão certo?"""
        if not nome1 and not nome2:
            await ctx.reply(
                "❌ Você precisa digitar dois nomes para testar a compatibilidade!",
                mention_author=False,
            )
            return
        elif nome1 and not nome2:
            nome2 = nome1
            nome1 = ctx.author.display_name

        # Simula a lógica de IDs apenas se os nomes forem exatamente os mesmos dos membros especiais
        if (nome1 == "Sael" and nome2 == "Mlhr Staff Vazio") or (nome1 == "Mlhr Staff Vazio" and nome2 == "Sael"):
            compatibilidade = 100
        elif nome1 in ["Sael", "Mlhr Staff Vazio"] or nome2 in ["Sael", "Mlhr Staff Vazio"]:
            compatibilidade = 0
        else:
            compatibilidade = random.randint(0, 100)

        # Gera a barra de compatibilidade
        total_barras = 10
        preenchido = int((compatibilidade / 100) * total_barras)
        barra = "█" * preenchido + "░" * (total_barras - preenchido)

        # Geração do nome ship
        metade1 = nome1[:len(nome1) // 2]
        metade2 = nome2[len(nome2) // 2:]
        nome_ship = metade1 + metade2

        # Mensagem personalizada
        if compatibilidade == 100:
            mensagem = "💞 Feitos um para o outro! Um casal perfeito! 💖"
        elif compatibilidade >= 75:
            mensagem = "😍 Uma conexão incrível! O amor está no ar!"
        elif compatibilidade >= 50:
            mensagem = "😊 Há potencial aqui! Talvez um encontro?"
        elif compatibilidade >= 25:
            mensagem = "🤔 Pode ser só amizade... ou algo mais?"
        else:
            mensagem = "💔 Melhor continuar como amigos... 😅"

        embed = discord.Embed(title="💘 Teste de Compatibilidade 💘", color=discord.Color.pink())
        embed.add_field(name="👩‍❤️‍👨 Casal", value=f"{nome1} + {nome2}", inline=False)
        embed.add_field(name="💖 Compatibilidade", value=f"{barra} | {compatibilidade}%", inline=False)
        embed.add_field(name="💑 Nome do Casal", value=nome_ship, inline=False)
        embed.add_field(name="", value=mensagem, inline=False)
        await ctx.reply(embed=embed, mention_author=False)

# Adicionar o comando ao bot
async def setup(bot):
    await bot.add_cog(ShipCommand(bot))
