import discord
from discord.ext import commands
import json

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes_file = 'DataBase/quotes.json'
        self.load_quotes()

    def load_quotes(self):
        """Carrega as citações do arquivo JSON."""
        try:
            with open(self.quotes_file, "r", encoding="utf-8") as f:
                self.quotes = json.load(f)
        except FileNotFoundError:
            self.quotes = {}

    def save_quotes(self):
        """Salva as citações no arquivo JSON."""
        with open(self.quotes_file, "w", encoding="utf-8") as f:
            json.dump(self.quotes, f, indent=4, ensure_ascii=False)

    @commands.hybrid_command(name="quote", aliases=["citation"], description="Salva ou exibe sua citação favorita.")
    async def quote(self, ctx: commands.Context, *, text: str | None = None):
        """Salva ou exibe uma citação favorita do servidor."""
        if text:
            # Remover espaços extras e quebras desnecessárias
            clean_text = " ".join(text.split())

            # Verificar se a chave já existe e é uma lista, se não, criar uma lista
            if ctx.author.name not in self.quotes:
                self.quotes[ctx.author.name] = []
            elif isinstance(self.quotes[ctx.author.name], str):  # Corrige caso a chave seja uma string
                self.quotes[ctx.author.name] = [self.quotes[ctx.author.name]]

            # Salva a citação
            self.quotes[ctx.author.name].append(clean_text)
            self.save_quotes()
            await ctx.reply(f"Citação de {ctx.author.name} salva: \"{clean_text}\"", mention_author=False)
        else:
            # Exibe as citações numeradas
            if ctx.author.name in self.quotes and self.quotes[ctx.author.name]:
                citations = "\n".join(f"{i+1}. {citation}" for i, citation in enumerate(self.quotes[ctx.author.name]))
                await ctx.reply(f"Citações de {ctx.author.name}: \n{citations}", mention_author=False)
            else:
                await ctx.reply(f"Você ainda não tem uma citação salva, {ctx.author.name}.", mention_author=False)

    @commands.hybrid_command(name="remover_quote", aliases=["delquote"], description="Exclui uma citação pelo número.")
    async def delquote(self, ctx: commands.Context, index: int):
        """Exclui uma citação especificada pelo número."""
        if ctx.author.name in self.quotes and len(self.quotes[ctx.author.name]) >= index > 0:
            # Remove a citação pela posição
            removed_citation = self.quotes[ctx.author.name].pop(index - 1)
            self.save_quotes()
            await ctx.reply(f"Citação excluída: \"{removed_citation}\"", mention_author=False)
        else:
            await ctx.reply(f"Não há uma citação válida com esse número, {ctx.author.name}.", mention_author=False)

    @commands.hybrid_command(name="ver_quotes", description="Exibe as citações de um usuário.")
    async def showquote(self, ctx: commands.Context, member: discord.Member | None = None):
        """Exibe as citações de um usuário, ou do autor do comando se não especificado."""
        if member is None:
            member = ctx.author

        if member.name in self.quotes and self.quotes[member.name]:
            citations = "\n".join(f"{i+1}. {citation}" for i, citation in enumerate(self.quotes[member.name]))
            await ctx.reply(f"Citações de {member.name}: \n{citations}", mention_author=False)
        else:
            await ctx.reply(f"{member.name} não tem citações salvas.", mention_author=False)

async def setup(bot):
    await bot.add_cog(Quote(bot))
