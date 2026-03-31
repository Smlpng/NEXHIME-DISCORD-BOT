import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import random

class TrianguloAmoroso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.template_path = "assets/triangulo/template.png"
        self.font_path = "assets/fonts/Impact.ttf"

    @commands.command(name="triângulo", aliases=["triangulo"], help="Cria um triângulo amoroso (meme).")
    async def triangulo(self, ctx: commands.Context, membro: discord.Member = None):
        """Crie um triangulo amoroso"""
        # Coordenadas onde cada avatar será colado (200x200 cada)
        positions = [
            (0, 0),       # O CARA QUE VOCÊ GOSTA
            (200, 0),     # A MÃE DELE
            (400, 0),     # IRMÃO DELE
            (0, 200),     # PRIMEIRO AMOR DELE
            (200, 200),   # MELHOR AMIGO DELE
            (400, 200),   # VOCÊ
        ]

        # Coordenadas específicas para os textos das labels
        text_positions = [
            (40.5, 115),    # O CARA QUE VOCÊ GOSTA
            (248, 129),     # A MÃE DELE
            (438, 129),     # IRMÃO DELE
            (43, 308),      # PRIMEIRO AMOR DELE
            (240, 308),     # MELHOR AMIGO DELE
            (474, 326),     # VOCÊ
        ]

        # Novas coordenadas para os usernames (no canto superior esquerdo)
        username_positions = [
            (10, 10),     # O CARA QUE VOCÊ GOSTA
            (210, 10),    # A MÃE DELE
            (410, 10),    # IRMÃO DELE
            (10, 210),    # PRIMEIRO AMOR DELE
            (210, 210),   # MELHOR AMIGO DELE
            (410, 210),   # VOCÊ
        ]

        # Determina os usuários para cada slot
        membros = [m for m in ctx.guild.members if not m.bot]

        if membro:
            autor = ctx.author
            alvo = membro
        else:
            autor = random.choice(membros)
            alvo = random.choice([m for m in membros if m != autor])

        selecionados = [alvo, autor] + random.sample(
            [m for m in membros if m not in (autor, alvo)], 4
        )
        random.shuffle(selecionados[2:])  # Embaralha os aleatórios

        # Carrega o template
        base = Image.open(self.template_path).convert("RGBA")

        async with aiohttp.ClientSession() as session:
            for i, membro in enumerate(selecionados):
                async with session.get(membro.avatar.replace(static_format='png').url) as resp:
                    if resp.status == 200:
                        avatar_bytes = await resp.read()
                        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                        avatar = avatar.resize((200, 200))
                        base.paste(avatar, positions[i], avatar)

        # Desenhar os textos
        draw = ImageDraw.Draw(base)
        font = ImageFont.truetype(self.font_path, 26)

        labels = [
            "O CARA QUE\nVOCE GOSTA",
            "O PAI DELE",
            "O IRMAO DELE",
            "O PRIMEIRO\nAMOR DELE",
            "O MELHOR\nAMIGO DELE",
            "VOCE"
        ]

        # Desenhar os nomes de usuário (username no canto superior esquerdo de cada avatar)
        username_font = ImageFont.truetype(self.font_path, 18)
        for i, membro in enumerate(selecionados):
            name = membro.name
            name_x, name_y = username_positions[i]
            # Contorno preto
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    draw.text((name_x + dx, name_y + dy), name, font=username_font, fill="black")
            # Texto branco
            draw.text((name_x, name_y), name, font=username_font, fill="white")

        # Desenhar as labels (VOCÊ, MELHOR AMIGO DELE, etc)
        for i, label in enumerate(labels):
            text_x, text_y = text_positions[i]
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    draw.text((text_x + dx, text_y + dy), label, font=font, fill="black")
            draw.text((text_x, text_y), label, font=font, fill="white")

         # Salva o resultado
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        arquivo = discord.File(buffer, filename="triangulo.png")

        # Envia a imagem como resposta ao comando do autor e marca a mensagem
        await ctx.reply(content=f"{ctx.author.mention}", file=arquivo, mention_author=False)



async def setup(bot):
    await bot.add_cog(TrianguloAmoroso(bot))





