import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class CoinDuelInviteView(discord.ui.View):
    def __init__(self, challenger: discord.abc.User, target: discord.abc.User, bet_amount: int):
        super().__init__(timeout=120)
        self.challenger = challenger
        self.target = target
        self.bet_amount = bet_amount

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Somente o jogador desafiado pode aceitar.", ephemeral=True)

        challenger = get_active_hero(self.challenger.id)
        target = get_active_hero(self.target.id)
        if challenger is None or target is None:
            return await interaction.response.edit_message(content="Um dos jogadores nao possui heroi ativo.", embed=None, view=None)
        if int(challenger.get("nex", 0)) < self.bet_amount or int(target.get("nex", 0)) < self.bet_amount:
            return await interaction.response.edit_message(content="Um dos jogadores nao tem saldo suficiente para cobrir a aposta.", embed=None, view=None)

        if not update_active_hero_resources(self.challenger.id, nex=-self.bet_amount):
            return await interaction.response.edit_message(content="Nao foi possivel reservar a aposta do desafiante.", embed=None, view=None)
        if not update_active_hero_resources(self.target.id, nex=-self.bet_amount):
            update_active_hero_resources(self.challenger.id, nex=self.bet_amount)
            return await interaction.response.edit_message(content="Nao foi possivel reservar a aposta do oponente.", embed=None, view=None)

        winner = random.choice([self.challenger, self.target])
        face = random.choice(["cara", "coroa"])
        update_active_hero_resources(winner.id, nex=self.bet_amount * 2)
        embed = discord.Embed(title="🪙 Cara ou Coroa Duelo", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Moeda", value=face.title(), inline=True)
        embed.add_field(name="Vencedor", value=winner.mention, inline=True)
        embed.add_field(name="Premio", value=f"{_format_nex(self.bet_amount * 2)} nex", inline=True)
        await interaction.response.edit_message(content=None, embed=embed, view=None)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Somente o jogador desafiado pode recusar.", ephemeral=True)
        await interaction.response.edit_message(content=f"{self.target.mention} recusou o duelo de moeda.", embed=None, view=None)


class CaraOuCoroaDuelo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="caraoucoroa_duelo", aliases=["coinflipduel", "moedaduelo"], help="Desafia outro jogador para cara ou coroa apostado.")
    async def caraoucoroa_duelo(self, ctx: commands.Context, membro: discord.Member, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        if membro.bot:
            return await inte.response.send_message("Voce nao pode desafiar bots.")
        if membro.id == inte.user.id:
            return await inte.response.send_message("Voce nao pode desafiar a si mesmo.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva.")

        challenger = get_active_hero(inte.user.id)
        target = get_active_hero(membro.id)
        if challenger is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo.")
        if target is None:
            return await inte.response.send_message(f"{membro.display_name} ainda nao possui heroi ativo.")

        view = CoinDuelInviteView(inte.user, membro, bet_amount)
        embed = discord.Embed(title="🪙 Duelo de moeda", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} desafiou {membro.mention} para uma aposta de {_format_nex(bet_amount)} nex cada."
        await inte.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(CaraOuCoroaDuelo(bot))