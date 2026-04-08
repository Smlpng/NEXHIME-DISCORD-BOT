import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


LEVEL_MULTIPLIERS = [1.2, 1.55, 2.05, 2.8, 4.0]
COLUMN_LABELS = ["Esquerda", "Centro", "Direita"]


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class TowerChoiceButton(discord.ui.Button):
    def __init__(self, column_index: int, disabled: bool):
        super().__init__(label=COLUMN_LABELS[column_index], style=discord.ButtonStyle.primary, disabled=disabled)
        self.column_index = column_index

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, TowerView):
            await view.pick_column(interaction, self.column_index)


class TowerView(discord.ui.View):
    def __init__(self, cog: "Torre", user_id: int, bet_amount: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.session_id = random.randint(100000, 999999)
        self.message: discord.Message | None = None
        self.level_index = 0
        self.safe_columns = [random.randint(0, 2) for _ in LEVEL_MULTIPLIERS]
        self.revealed: dict[int, int] = {}
        self.finished = False
        self.finish_reason: str | None = None
        self.final_payout = 0
        self._rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Apenas quem iniciou esta torre pode continuar a subida.", ephemeral=True)
            return False
        return True

    def _wallet_balance(self) -> int:
        hero = get_active_hero(self.user_id)
        if hero is None:
            return 0
        return int(hero.get("nex", 0))

    def _current_multiplier(self) -> float:
        if self.level_index <= 0:
            return 1.0
        return LEVEL_MULTIPLIERS[self.level_index - 1]

    def _current_payout(self) -> int:
        return int(round(self.bet_amount * self._current_multiplier()))

    def _status_text(self) -> str:
        if self.finish_reason == "cashout":
            lucro = self.final_payout - self.bet_amount
            return f"Voce sacou {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
        if self.finish_reason == "loss":
            return "Voce encontrou a casa quebrada da torre e perdeu a aposta."
        if self.finish_reason == "cleared":
            lucro = self.final_payout - self.bet_amount
            return f"Voce chegou ao topo e recebeu {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
        if self.finish_reason == "refund":
            return "A aposta foi devolvida porque voce saiu antes da primeira escolha."
        if self.finish_reason == "timeout":
            lucro = self.final_payout - self.bet_amount
            return f"Tempo esgotado. O saque automatico fechou em {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
        return "Suba nivel por nivel. Cada acerto aumenta o multiplicador, mas um erro derruba tudo."

    def build_embed(self) -> discord.Embed:
        color = RPG_PRIMARY_COLOR
        if self.finish_reason == "loss":
            color = discord.Color.red()
        elif self.finished:
            color = discord.Color.green()

        embed = discord.Embed(title="🏯 Torre", description=self._status_text(), color=color)
        embed.add_field(name="Aposta", value=f"{_format_nex(self.bet_amount)} nex", inline=True)
        embed.add_field(name="Andar atual", value=f"{self.level_index + 1}/{len(LEVEL_MULTIPLIERS)}" if not self.finished else str(len(self.revealed)), inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(self._wallet_balance())} nex", inline=True)
        embed.add_field(name="Multiplicador", value=f"{self._current_multiplier():.2f}x", inline=True)
        embed.add_field(name="Saque atual", value=f"{_format_nex(self._current_payout())} nex", inline=True)
        next_value = "Topo" if self.level_index >= len(LEVEL_MULTIPLIERS) else f"{LEVEL_MULTIPLIERS[self.level_index]:.2f}x"
        embed.add_field(name="Proximo alvo", value=next_value, inline=True)

        lines = []
        for idx in range(len(LEVEL_MULTIPLIERS)):
            if idx in self.revealed:
                picked = self.revealed[idx]
                safe = self.safe_columns[idx]
                if picked == safe:
                    lines.append(f"Nivel {idx + 1}: ✅ {COLUMN_LABELS[picked]}")
                else:
                    lines.append(f"Nivel {idx + 1}: 💥 {COLUMN_LABELS[picked]}")
            elif self.finished:
                lines.append(f"Nivel {idx + 1}: 🔹 {COLUMN_LABELS[self.safe_columns[idx]]}")
            elif idx == self.level_index:
                lines.append(f"Nivel {idx + 1}: ? ? ?")
            else:
                lines.append(f"Nivel {idx + 1}: --")
        embed.add_field(name="Escalada", value="\n".join(lines), inline=False)
        embed.set_footer(text=f"Partida #{self.session_id}")
        return embed

    def _rebuild_items(self) -> None:
        self.clear_items()
        if self.finished:
            replay_button = discord.ui.Button(label="Nova torre", emoji="🎮", style=discord.ButtonStyle.success)
            replay_button.callback = self.restart_game
            self.add_item(replay_button)
            return

        for column_index in range(3):
            self.add_item(TowerChoiceButton(column_index, disabled=False))

        cashout_button = discord.ui.Button(label="Sacar", emoji="💰", style=discord.ButtonStyle.secondary, row=1)
        cashout_button.callback = self.cashout
        self.add_item(cashout_button)

    async def _sync_message(self, interaction: discord.Interaction | None = None) -> None:
        self._rebuild_items()
        embed = self.build_embed()
        if interaction is not None:
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)
            return
        if self.message is not None:
            await self.message.edit(embed=embed, view=self)

    async def pick_column(self, interaction: discord.Interaction, column_index: int) -> None:
        if self.finished:
            return
        self.revealed[self.level_index] = column_index
        safe_column = self.safe_columns[self.level_index]
        if column_index != safe_column:
            await self.finish_game(interaction, "loss", payout=0)
            return

        self.level_index += 1
        if self.level_index >= len(LEVEL_MULTIPLIERS):
            await self.finish_game(interaction, "cleared", payout=self._current_payout())
            return
        await self._sync_message(interaction)

    async def cashout(self, interaction: discord.Interaction) -> None:
        if self.level_index <= 0:
            await self.finish_game(interaction, "refund", payout=self.bet_amount)
            return
        await self.finish_game(interaction, "cashout", payout=self._current_payout())

    async def restart_game(self, interaction: discord.Interaction) -> None:
        await self.cog.restart_game(interaction, self.bet_amount)

    async def finish_game(self, interaction: discord.Interaction | None, reason: str, payout: int) -> None:
        if self.finished:
            return
        self.finished = True
        self.finish_reason = reason
        self.final_payout = payout
        self.cog.active_games.pop(self.user_id, None)
        if payout > 0:
            update_active_hero_resources(self.user_id, nex=payout)
        await self._sync_message(interaction)

    async def on_timeout(self) -> None:
        if self.finished:
            return
        payout = self.bet_amount if self.level_index <= 0 else self._current_payout()
        try:
            await self.finish_game(None, "timeout", payout=payout)
        except discord.HTTPException:
            self.cog.active_games.pop(self.user_id, None)


class Torre(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games: dict[int, TowerView] = {}

    async def _start_game(self, inte: CommandContextAdapter, bet_amount: int) -> None:
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            await inte.response.send_message("Nao consegui localizar seu heroi ativo para iniciar a torre.")
            return
        if inte.user.id in self.active_games:
            await inte.response.send_message("Voce ja tem uma partida de torre aberta.")
            return
        if bet_amount <= 0:
            await inte.response.send_message("Informe uma aposta positiva. Ex: !torre 500")
            return
        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex.")
            return
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            await inte.response.send_message("Nao foi possivel reservar sua aposta. Tente novamente.")
            return

        view = TowerView(self, inte.user.id, bet_amount)
        self.active_games[inte.user.id] = view
        message = await inte.response.send_message(embed=view.build_embed(), view=view)
        view.message = message

    async def restart_game(self, interaction: discord.Interaction, bet_amount: int) -> None:
        if interaction.user.id in self.active_games:
            await interaction.response.send_message("Voce ja tem uma partida em andamento.", ephemeral=True)
            return
        hero = get_active_hero(interaction.user.id)
        wallet = int(hero.get("nex", 0)) if hero else 0
        if hero is None:
            await interaction.response.send_message("Nao consegui localizar seu heroi ativo.", ephemeral=True)
            return
        if wallet < bet_amount:
            await interaction.response.send_message(
                f"Saldo insuficiente para uma nova partida. Carteira atual: {_format_nex(wallet)} nex.",
                ephemeral=True,
            )
            return
        if not update_active_hero_resources(interaction.user.id, nex=-bet_amount):
            await interaction.response.send_message("Nao foi possivel reservar a nova aposta.", ephemeral=True)
            return

        view = TowerView(self, interaction.user.id, bet_amount)
        view.message = interaction.message
        self.active_games[interaction.user.id] = view
        await interaction.response.edit_message(embed=view.build_embed(), view=view)

    @commands.command(name="torre", aliases=["tower", "subida"], help="Suba uma torre de risco e saque antes de cair. Ex: !torre 500")
    async def torre(self, ctx: commands.Context, bet_amount: int) -> None:
        inte = CommandContextAdapter(ctx)
        await self._start_game(inte, bet_amount)


async def setup(bot: commands.Bot):
    await bot.add_cog(Torre(bot))