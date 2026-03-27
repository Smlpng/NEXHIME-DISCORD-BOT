import discord
from discord.ext import commands
from io import BytesIO
from PIL import Image
import aiohttp

class AddSticker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="add_sticker", description="Adiciona uma figurinha ao servidor.")
    @commands.has_permissions(manage_emojis=True)
    async def add_sticker(self, ctx, name: str = None, *, link: str = None):
        """
        Adiciona uma figurinha ao servidor.
        Uso: !add_sticker [nome] [link/reply/anexo]
        Aceita: PNG, JPG, WEBP, GIF
        """
        
        image_url = None
        
        # Verificar se há reply
        if ctx.message.reference:
            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_message.attachments:
                image_url = replied_message.attachments[0].url
            elif replied_message.embeds:
                image_url = replied_message.embeds[0].image.url if replied_message.embeds[0].image else None
        
        # Verificar se há anexo na mensagem atual
        elif ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        
        # Verificar se há link fornecido
        elif link:
            image_url = link
        
        if not image_url:
            await ctx.send("❌ Nenhuma imagem fornecida! Use anexo, reply ou link.")
            return
        
        if not name:
            await ctx.send("❌ Você deve fornecer um nome para a figurinha!")
            return
        
        try:
            # Download da imagem/gif
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Erro ao baixar a imagem!")
                        return
                    image_data = await resp.read()
            
            # Validar se é imagem válida
            img = Image.open(BytesIO(image_data))
            img.verify()
            
            # Reabrir imagem para verificar formato
            img = Image.open(BytesIO(image_data))
            file_format = img.format
            
            # Se não for GIF, converter para PNG
            if file_format != "GIF":
                png_data = BytesIO()
                img.save(png_data, format="PNG")
                image_data = png_data.getvalue()
            
            # Adicionar figurinha ao servidor
            emoji = await ctx.guild.create_custom_emoji(
                name=name,
                image=image_data
            )
            
            await ctx.send(f"✅ Figurinha {emoji} `{name}` adicionada com sucesso!")
        
        except Image.UnidentifiedImageError:
            await ctx.send("❌ Arquivo não é uma imagem/GIF válida!")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erro ao adicionar figurinha: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ Erro inesperado: {str(e)}")

async def setup(bot):
    await bot.add_cog(AddSticker(bot))
