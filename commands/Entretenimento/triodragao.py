import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO

class TrioDragao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trio_dragão", aliases=["trio_dragao"], help="Cria um meme do trio de dragões.")
    async def triodragao(
        self,
        ctx: commands.Context,
        user1: discord.Member = None,
        user2: discord.Member = None,
        user3: discord.Member = None,
    ):
        """Crie um meme com seus amigos"""
        # Padrões: preenche com autor caso não mencione tudo
        users = [user1, user2, user3]
        for i in range(3):
            if users[i] is None:
                users[i] = ctx.author

        # Baixando avatares em PNG 128x128
        avatar_imgs = []
        for user in users:
            avatar_asset = user.display_avatar.replace(format="png", size=128)
            buffer = BytesIO(await avatar_asset.read())
            avatar = Image.open(buffer).convert("RGBA").resize((96, 96))  # Ajustável
            avatar_imgs.append(avatar)

        # Carregando imagem base
        try:
            base = Image.open("assets/templates/trio_dragoes/trio_dragao_Template.png").convert("RGBA")
        except FileNotFoundError:
            await ctx.reply(
                "❌ Imagem base não encontrada. Certifique-se de que `assets/templates/dragoes/triodragao.png` existe.",
                mention_author=False,
            )
            return


        # Coordenadas (x, y) onde cada avatar será colado
        positions = [
            (39, 323),   # Dragão sério 1
            (292, 298),  # Dragão sério 2
            (520, 323)   # Dragão bobo
        ]

        # Colando cada avatar nas posições
        for img, pos in zip(avatar_imgs, positions):
            base.paste(img, pos, img)

        # Salvando em memória e enviando
        with BytesIO() as image_binary:
            base.save(image_binary, "PNG")
            image_binary.seek(0)
            await ctx.reply(
                file=discord.File(fp=image_binary, filename="triodragao.png"),
                mention_author=False,
            )

# Setup
async def setup(bot):
    await bot.add_cog(TrioDragao(bot))
