import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap

class Cerebro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.font_path = "assets/fonts/Impact.ttf"  # Troque se necessário
        self.template_path = "assets/cerebro/cerebro.png"

    @commands.hybrid_command(name="cérebro", aliases=["cerebro", "brain"], description="Cria um meme Expanding Brain.")
    async def cerebro(self, ctx: commands.Context, *, ideias: str):
        """Crie um meme com Expanding Brain"""
        partes = [parte.strip() for parte in ideias.split('|')]

        if len(partes) != 4:
            return await ctx.reply(
                "Você precisa enviar **4 ideias separadas por `|`**.\nExemplo: `!cerebro ideia1 | ideia2 | ideia3 | ideia4`",
                mention_author=False,
            )

        imagem = Image.open(self.template_path).convert("RGBA")
        draw = ImageDraw.Draw(imagem)

        # Tamanho da área onde o texto será desenhado
        largura_max = 750  # ajuste conforme sua imagem
        altura_max = 180   # altura de cada "bloco"

        # Coordenadas de início de cada bloco
        posicoes = [40, 260, 500, 720]

        for texto, y in zip(partes, posicoes):
            fonte_tamanho = 48
            fonte = ImageFont.truetype(self.font_path, fonte_tamanho)

            # Reduz o tamanho da fonte se o texto for muito largo
            while fonte.getlength(texto) > largura_max and fonte_tamanho > 10:
                fonte_tamanho -= 2
                fonte = ImageFont.truetype(self.font_path, fonte_tamanho)

            # Quebra de linha se necessário
            linhas = textwrap.wrap(texto, width=30)

            for i, linha in enumerate(linhas):
                draw.text((20, y + i * (fonte.size + 5)), linha, font=fonte, fill=(0, 0, 0))

        # Enviar
        with io.BytesIO() as imagem_binaria:
            imagem.save(imagem_binaria, "PNG")
            imagem_binaria.seek(0)
            await ctx.reply(
                file=discord.File(imagem_binaria, filename="cerebro.png"),
                mention_author=False,
            )

async def setup(bot):
    await bot.add_cog(Cerebro(bot))
