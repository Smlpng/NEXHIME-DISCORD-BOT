import discord
from discord.ext import commands
from discord import app_commands
import os
import inspect

class ComandosDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = []

        for cog_name in os.listdir("commands"):
            if os.path.isdir(f"commands/{cog_name}"):
                options.append(discord.SelectOption(label=cog_name.capitalize(), value=cog_name))

        super().__init__(placeholder="Escolha uma categoria de comandos", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        comandos = []

        for comando in self.bot.commands:
            try:
                comando_path = inspect.getfile(comando.callback)
                if f"commands/{categoria}" in comando_path.replace("\\", "/").lower():
                    comandos.append(f"`n!{comando.name}` - {comando.help or 'Sem descrição.'}")
            except:
                continue


        if comandos:
            embed = discord.Embed(
                title=f"📚 Comandos da categoria: {categoria.capitalize()}",
                description="\n".join(comandos),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title=f"Nenhum comando encontrado na categoria {categoria}.",
                color=discord.Color.red()
            )

        await interaction.response.edit_message(embed=embed, view=self.view)


class ComandosDropdownView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(ComandosDropdown(bot))


class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="comandos",
        aliases=["commands", "cmds"],
        description="Mostra os comandos por categoria."
    )
    async def comandos(self, ctx):
        embed = discord.Embed(
            title="📜 Lista de Comandos",
            description="Selecione uma categoria abaixo para ver os comandos disponíveis.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=ComandosDropdownView(self.bot))


async def setup(bot):
    await bot.add_cog(Comandos(bot))
