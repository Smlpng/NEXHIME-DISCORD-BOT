import discord
from discord.ext import commands
import pyfiglet

class AsciiArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ascii", description="Converte texto em arte ASCII.")
    async def ascii(self, ctx: commands.Context, *, text: str):
        """Converte texto em arte ASCII com espaçamento entre as letras e sem o símbolo extra no início."""
        try:
            # Modifica o texto para adicionar um pequeno espaço entre cada letra
            spaced_text = ' '.join(text)

            # Gera a arte ASCII usando a fonte "standard"
            ascii_art = pyfiglet.figlet_format(spaced_text, font="standard")  # Fonte "standard"

            # Remove a linha em branco no final
            ascii_art = ascii_art.strip()

            if len(ascii_art) > 2000:
                # Caso a arte seja muito longa para enviar em uma única mensagem
                await ctx.reply("A arte ASCII gerada é muito longa. Não consigo enviar.", mention_author=False)
            else:
                await ctx.reply(f"```{ascii_art}```", mention_author=False)

        except Exception as e:
            await ctx.reply(f"Erro ao gerar arte ASCII: {e}", mention_author=False)

# Função de configuração para adicionar o Cog ao bot
async def setup(bot):
    await bot.add_cog(AsciiArt(bot))
