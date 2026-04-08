import asyncio
import json
import urllib.parse
import urllib.request

import discord
from discord.ext import commands


class Traduz(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _translate_blocking(target_lang: str, text: str) -> str | None:
        query = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={query}&langpair=auto|{urllib.parse.quote(target_lang)}"
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        translated = data.get("responseData", {}).get("translatedText")
        return translated if translated else None

    @commands.command(name="traduz", aliases=["translate"], help="Traduz um texto. Ex: !traduz en ola mundo")
    async def traduz(self, ctx: commands.Context, idioma: str, *, texto: str):
        try:
            resultado = await asyncio.to_thread(self._translate_blocking, idioma, texto)
        except Exception:
            resultado = None
        if not resultado:
            return await ctx.reply("Nao foi possivel traduzir esse texto agora.")
        embed = discord.Embed(title="Traducao", color=discord.Color.blurple())
        embed.add_field(name="Original", value=texto[:1024], inline=False)
        embed.add_field(name=f"Traduzido ({idioma})", value=resultado[:1024], inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Traduz(bot))