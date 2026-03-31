import discord
from discord.ext import commands
from PIL import Image, ImageOps
import io
import aiohttp
import os

class Queimar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.template_path = "assets/queimar/fogueira.png"  # imagem base do Bob Esponja

    @commands.command(name="queimar", aliases=["burn"], help="Queima uma imagem com o Bob Esponja (meme).")
    async def queimar(self, ctx: commands.Context, user: discord.User = None):
        """Queime algo com o Bob Esponja"""
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

        # Redimensionar para caber no papel do Bob
        sobreposicao = ImageOps.fit(sobreposicao, (144, 193))

        # Colar na posição correta
        fundo.paste(sobreposicao, (38, 50), sobreposicao)

        # Enviar imagem final
        with io.BytesIO() as img_bin:
            fundo.save(img_bin, format="PNG")
            img_bin.seek(0)
            await ctx.reply(
                file=discord.File(img_bin, filename="queimar.png"),
                mention_author=False,
            )

async def setup(bot):
    await bot.add_cog(Queimar(bot))
