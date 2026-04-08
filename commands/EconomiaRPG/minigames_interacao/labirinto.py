import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR
from commands.EconomiaRPG.utils.validators import validate_bet_amount


PATHS = ["esquerda", "centro", "direita"]


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class MazeButton(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label.title(), style=discord.ButtonStyle.primary)
        self.path_name = label

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, MazeView):
            await view.pick(interaction, self.path_name)


class MazeView(discord.ui.View):
    def __init__(self, user_id: int, bet_amount: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.level = 0
        self.safe_paths = [random.choice(PATHS) for _ in range(4)]
        self.finished = False
        self.message: discord.Message | None = None
        for path in PATHS:
            self.add_item(MazeButton(path))
        cashout = discord.ui.Button(label="Sacar", style=discord.ButtonStyle.secondary, row=1)
        cashout.callback = self.cashout
        self.add_item(cashout)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Apenas quem abriu o labirinto pode jogar.", ephemeral=True)
            return False
        return True

    def _payout(self) -> int:
        multipliers = [1.0, 1.4, 1.9, 2.6, 3.8]
        return int(round(self.bet_amount * multipliers[self.level]))

    def _embed(self, text: str) -> discord.Embed:
        embed = discord.Embed(title="🌀 Labirinto", description=text, color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Andar", value=f"{self.level}/4", inline=True)
        embed.add_field(name="Saque atual", value=f"{_format_nex(self._payout())} nex", inline=True)
        return embed

    async def pick(self, interaction: discord.Interaction, chosen_path: str):
        if self.finished:
            return
        if chosen_path != self.safe_paths[self.level]:
            self.finished = True
            return await interaction.response.edit_message(embed=self._embed("Voce caiu numa armadilha e perdeu a aposta."), view=None)
        self.level += 1
        if self.level >= 4:
            self.finished = True
            payout = self._payout()
            update_active_hero_resources(self.user_id, nex=payout)
            return await interaction.response.edit_message(embed=self._embed(f"Voce escapou do labirinto e recebeu {_format_nex(payout)} nex."), view=None)
        await interaction.response.edit_message(embed=self._embed("Caminho certo. Continue avancando ou saque agora."), view=self)

    async def cashout(self, interaction: discord.Interaction):
        if self.finished:
            return
        self.finished = True
        payout = self.bet_amount if self.level == 0 else self._payout()
        update_active_hero_resources(self.user_id, nex=payout)
        await interaction.response.edit_message(embed=self._embed(f"Voce sacou {_format_nex(payout)} nex e saiu do labirinto."), view=None)

    async def on_timeout(self):
        if self.finished:
            return
        self.finished = True
        payout = self.bet_amount if self.level == 0 else self._payout()
        update_active_hero_resources(self.user_id, nex=payout)
        if self.message is not None:
            try:
                await self.message.edit(embed=self._embed(f"Tempo esgotado. O saque automatico fechou em {_format_nex(payout)} nex."), view=None)
            except discord.HTTPException:
                pass


class Labirinto(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="labirinto", aliases=["maze"], help="Escolha caminhos seguros e saque antes de cair.")
    async def labirinto(self, ctx: commands.Context, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para entrar no labirinto.")
        bet_validation = validate_bet_amount(inte.user.id, bet_amount, context="entrar no labirinto")
        if not bet_validation.ok:
            return await inte.response.send_message(bet_validation.message)
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel reservar sua aposta.")

        view = MazeView(inte.user.id, bet_amount)
        message = await inte.response.send_message(embed=view._embed("Escolha um caminho para entrar no labirinto."), view=view)
        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(Labirinto(bot))