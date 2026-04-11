import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import asyncio

from mongo import load_json_document


QUESTIONS_DOCUMENT = "DataBase/showdomilhao_perguntas.json"

class AlternativaButton(Button):
    def __init__(self, index, correta):
        super().__init__(label=str(index + 1), style=discord.ButtonStyle.primary)
        self.index = index
        self.correta = correta

    async def callback(self, interaction: discord.Interaction):
        view: RodadaView = self.view

        if self.index == self.correta:
            await interaction.response.send_message("✅ Resposta correta! Preparando a próxima pergunta...", ephemeral=True)
            await asyncio.sleep(1.5)
            await view.cog.enviar_pergunta(interaction, view.perguntas, view.index + 1, view.valor * 2)
        else:
            pergunta = view.perguntas[view.index]
            resposta_correta = pergunta["correta"] + 1
            texto_erro = f"❌ Resposta errada!\nA alternativa correta era: **{resposta_correta}**.\nVocê ganhou **R$ {view.valor:,}**!"
            await interaction.response.send_message(texto_erro)
            view.stop()

class RodadaView(View):
    def __init__(self, cog, perguntas, index, valor):
        super().__init__(timeout=30)
        self.cog = cog
        self.perguntas = perguntas
        self.index = index
        self.valor = valor

        correta = perguntas[index]["correta"]
        for i in range(4):
            self.add_item(AlternativaButton(i, correta))

class ShowDoMilhao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="show_do_milhão", aliases=["showdomilhao", "show_do_milhao"], help="Jogo do Show do Milhão.")
    async def show_do_milhao(self, ctx: commands.Context):
        """Já pensou em participar do Show do Milhão?"""
        todas_perguntas = load_json_document(QUESTIONS_DOCUMENT, [])

        if not isinstance(todas_perguntas, list) or len(todas_perguntas) < 1:
            await ctx.reply("❌ Nenhuma pergunta do Show do Milhão foi encontrada no MongoDB.", mention_author=False)
            return

        perguntas = random.sample(todas_perguntas, k=min(10, len(todas_perguntas)))
        await self.enviar_pergunta(ctx, perguntas, 0, 1000)

    async def enviar_pergunta(self, origem, perguntas, index, valor):
        if index >= len(perguntas):
            embed = discord.Embed(
                title="🏆 Você venceu o Show do Milhão!",
                description=f"Parabéns! Você respondeu todas as perguntas corretamente e ganhou **R$ 1.000.000**!",
                color=discord.Color.green()
            )
            if isinstance(origem, commands.Context):
                await origem.send(embed=embed)
            else:
                await origem.followup.send(embed=embed)
            return

        pergunta = perguntas[index]
        embed = discord.Embed(
            title=f"🎤 Show do Milhão - Pergunta {index + 1}",
            description=f"**{pergunta['pergunta']}**",  # Adicionando negrito à pergunta
            color=discord.Color.gold()
        )

        # Corrigindo definitivamente a exibição das alternativas
        for i, alternativa in enumerate(pergunta["alternativas"]):
            embed.add_field(name=f"🔘 Alternativa {i+1}", value=alternativa, inline=False)

        embed.set_footer(text=f"Valor atual: R$ {valor:,}")

        view = RodadaView(self, perguntas, index, valor)

        if isinstance(origem, commands.Context):
            await origem.send(embed=embed, view=view)
        elif isinstance(origem, discord.Interaction):
            if origem.response.is_done():
                await origem.followup.send(embed=embed, view=view)
            else:
                await origem.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShowDoMilhao(bot))
