import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import random

class Wanted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.template_path = "assets/wanted/wanted.png"
        self.font_path = "assets/fonts/timesbd.ttf"  # Times New Roman

    def draw_bold_text(self, draw, position, text, font, fill, thickness=1):
        x, y = position
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                draw.text((x + dx, y + dy), text, font=font, fill=fill)

    @commands.hybrid_command(name="procurado", aliases=["wanted"], description="Crie uma imagem de procurado com sua foto")
    async def wanted(self, ctx: commands.Context, membro: discord.Member | None = None):
        """Crie uma imagem de procurado com sua foto"""
        membro = membro or ctx.author

        # Carrega o template
        base = Image.open(self.template_path).convert("RGBA")

        # Tamanho e posição do avatar
        avatar_size = (1422, 1030)
        avatar_position = (162, 532)

        # Cor em RGBA (#4f3c20)
        text_color = (79, 60, 32, 255)

        async with aiohttp.ClientSession() as session:
            async with session.get(membro.avatar.replace(static_format='png').url) as resp:
                if resp.status == 200:
                    avatar_bytes = await resp.read()
                    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                    avatar = avatar.resize(avatar_size)
                    base.paste(avatar, avatar_position, avatar)

        draw = ImageDraw.Draw(base)
        font_times = ImageFont.truetype(self.font_path, 146)

        # Texto: Nome do usuário
        username_text = membro.name
        username_x = 870  # Novo centro X
        username_y = 1776

        bbox = font_times.getbbox(username_text)
        text_width = bbox[2] - bbox[0]
        self.draw_bold_text(draw, (username_x - text_width // 2, username_y), username_text, font_times, text_color, thickness=1)

        # Texto: Valor aleatório
        random_number = f"{random.randint(1_000_000, 9_999_999_999):,}".replace(",", ".")
        random_text = f"{random_number}"
        random_x = 870
        random_y = 2073

        bbox_random = font_times.getbbox(random_text)
        random_width = bbox_random[2] - bbox_random[0]
        self.draw_bold_text(draw, (random_x - random_width // 2, random_y), random_text, font_times, text_color, thickness=1)

        # Salva a imagem
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="wanted.png")
        await ctx.reply(file=file, mention_author=True)

async def setup(bot):
    await bot.add_cog(Wanted(bot))
