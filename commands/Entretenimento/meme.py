import discord
import aiohttp
from discord.ext import commands

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="meme", description="Receba um meme aleatório da internet.")
    async def meme(self, ctx: commands.Context):
        """Envia uma imagem ou meme aleatório."""
        await self.fetch_and_send_meme(ctx)

    async def fetch_and_send_meme(self, target):
        """Busca e envia um meme aleatório."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    meme_url = data["url"]
                    if isinstance(target, commands.Context):
                        await target.reply(meme_url, mention_author=False)
                    elif isinstance(target, discord.Interaction):
                        await target.response.send_message(meme_url)
                else:
                    error_message = "Não consegui encontrar um meme agora, tente novamente mais tarde."
                    if isinstance(target, commands.Context):
                        await target.reply(error_message, mention_author=False)
                    elif isinstance(target, discord.Interaction):
                        await target.response.send_message(error_message)

async def setup(bot):
    await bot.add_cog(Meme(bot))
