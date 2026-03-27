import discord
from discord.ext import commands
from PIL import Image, ImageOps
import io
import aiohttp
import os

class PiseiNaMerda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.template_path = "assets/pisei/namerda.png"  # imagem base do Pisei na Merda

    @commands.hybrid_command(name="pisei", aliases=["steppedinshit"], description="Cria o meme 'pisei na merda' com uma imagem.")
    async def pisar(self, ctx: commands.Context, user: discord.User = None):
        """Droga, pisei na merda!"""
        imagem_alvo = None

        # 1. Se o usuário mandou uma imagem junto
        if ctx.message.attachments:
            imagem_alvo = await ctx.message.attachments[0].read()

        # 2. Se mencionou alguém (usar avatar)
        elif user:
            async with aiohttp.ClientSession() as session:
                async with session.get(user.display_avatar.url) as resp:
                    if resp.status == 200:
                        imagem_alvo = await resp.read()

        # 3. Procurar última imagem do chat (até 20 mensagens acima)
        else:
            async for msg in ctx.channel.history(limit=20):
                if msg.attachments:
                    imagem_alvo = await msg.attachments[0].read()
                    break

        if not imagem_alvo:
            return await ctx.reply(
                "❌ Nenhuma imagem encontrada. Envie uma imagem, mencione alguém ou use após uma imagem.",
                mention_author=False,
            )

        # Abrir imagens
        fundo = Image.open(self.template_path).convert("RGBA")
        sobreposicao = Image.open(io.BytesIO(imagem_alvo)).convert("RGBA")

        # Redimensionar para caber no pé
        sobreposicao = ImageOps.fit(sobreposicao, (100, 100))

        # Colar na posição correta
        fundo.paste(sobreposicao, (132, 410), sobreposicao)

        # Enviar imagem final
        with io.BytesIO() as img_bin:
            fundo.save(img_bin, format="PNG")
            img_bin.seek(0)
            await ctx.reply(
                file=discord.File(img_bin, filename="piseinamerda.png"),
                mention_author=False,
            )

async def setup(bot):
    await bot.add_cog(PiseiNaMerda(bot))
