import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR
from commands.EconomiaRPG.utils.validators import validate_amount_range, validate_bet_amount


BOARD_COLUMNS = 4
BOARD_SIZE = 16
HOUSE_EDGE = 0.93
MIN_MINES = 1
MAX_MINES = 8


def _format_nex(value: int) -> str:
	return f"{int(value):,}".replace(",", ".")


def _calculate_multiplier(mines: int, safe_reveals: int) -> float:
	if safe_reveals <= 0:
		return 1.0

	remaining_safe = BOARD_SIZE - mines
	remaining_total = BOARD_SIZE
	survival_chance = 1.0

	for _ in range(safe_reveals):
		survival_chance *= remaining_safe / remaining_total
		remaining_safe -= 1
		remaining_total -= 1

	if survival_chance <= 0:
		return 1.0
	return HOUSE_EDGE / survival_chance


def _calculate_payout(bet_amount: int, mines: int, safe_reveals: int) -> int:
	if safe_reveals <= 0:
		return bet_amount
	return max(int(round(bet_amount * _calculate_multiplier(mines, safe_reveals))), 0)


class MinesTileButton(discord.ui.Button):
	def __init__(self, tile_index: int, revealed: bool, tile_value: str, finished: bool):
		if revealed:
			emoji = "💎" if tile_value == "safe" else "💣"
			style = discord.ButtonStyle.success if tile_value == "safe" else discord.ButtonStyle.danger
			disabled = True
		else:
			emoji = "⬛"
			style = discord.ButtonStyle.secondary
			disabled = finished

		super().__init__(label="\u200b", emoji=emoji, style=style, row=tile_index // BOARD_COLUMNS, disabled=disabled)
		self.tile_index = tile_index

	async def callback(self, interaction: discord.Interaction):
		view = self.view
		if isinstance(view, MinesGameView):
			await view.reveal_tile(interaction, self.tile_index)


class MinesGameView(discord.ui.View):
	def __init__(self, cog: "Mines", user_id: int, bet_amount: int, mines_count: int):
		super().__init__(timeout=180)
		self.cog = cog
		self.user_id = user_id
		self.bet_amount = bet_amount
		self.mines_count = mines_count
		self.session_id = random.randint(100000, 999999)
		self.message: discord.Message | None = None
		self.finished = False
		self.finish_reason: str | None = None
		self.final_payout = 0
		self.board = ["safe"] * BOARD_SIZE
		self.revealed_tiles: set[int] = set()

		for tile_index in random.sample(range(BOARD_SIZE), self.mines_count):
			self.board[tile_index] = "mine"

		self._rebuild_items()

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		if interaction.user.id != self.user_id:
			await interaction.response.send_message("Apenas quem iniciou esta partida pode jogar nela.", ephemeral=True)
			return False
		return True

	@property
	def safe_reveals(self) -> int:
		return sum(1 for index in self.revealed_tiles if self.board[index] == "safe")

	@property
	def max_safe_tiles(self) -> int:
		return BOARD_SIZE - self.mines_count

	def _hidden_tiles(self) -> list[int]:
		return [index for index in range(BOARD_SIZE) if index not in self.revealed_tiles]

	def _current_multiplier(self) -> float:
		return _calculate_multiplier(self.mines_count, self.safe_reveals)

	def _next_multiplier(self) -> float | None:
		if self.safe_reveals >= self.max_safe_tiles:
			return None
		return _calculate_multiplier(self.mines_count, self.safe_reveals + 1)

	def _current_payout(self) -> int:
		return _calculate_payout(self.bet_amount, self.mines_count, self.safe_reveals)

	def _wallet_balance(self) -> int:
		hero = get_active_hero(self.user_id)
		if hero is None:
			return 0
		return int(hero.get("nex", 0))

	def _status_text(self) -> str:
		if self.finish_reason == "lost":
			return "Voce encontrou uma mina e perdeu a aposta inteira."
		if self.finish_reason == "cashout":
			lucro = self.final_payout - self.bet_amount
			return (
				f"Voce retirou {self.safe_reveals} pedra(s) preciosa(s) e saiu com "
				f"{_format_nex(self.final_payout)} nex ({'+' if lucro >= 0 else ''}{_format_nex(lucro)})."
			)
		if self.finish_reason == "cleared":
			lucro = self.final_payout - self.bet_amount
			return (
				f"Voce limpou todo o tabuleiro e recebeu {_format_nex(self.final_payout)} nex "
				f"({'+' if lucro >= 0 else ''}{_format_nex(lucro)})."
			)
		if self.finish_reason == "timeout":
			lucro = self.final_payout - self.bet_amount
			return (
				f"A partida expirou e o saque foi feito automaticamente em {_format_nex(self.final_payout)} nex "
				f"({'+' if lucro >= 0 else ''}{_format_nex(lucro)})."
			)
		if self.finish_reason == "timeout_refund":
			return "A partida expirou antes da primeira jogada, entao a aposta foi devolvida automaticamente."
		if self.finish_reason == "refund":
			return "A aposta foi devolvida porque voce encerrou a partida sem abrir nenhuma casa."
		return "Abra casas seguras para aumentar o multiplicador, mas saia antes de achar uma mina."

	def build_embed(self) -> discord.Embed:
		color = RPG_PRIMARY_COLOR
		if self.finish_reason == "lost":
			color = discord.Color.red()
		elif self.finish_reason in {"cashout", "cleared", "timeout", "timeout_refund", "refund"}:
			color = discord.Color.green()

		embed = discord.Embed(
			title="💣 Mines",
			description=self._status_text(),
			color=color,
		)
		embed.add_field(name="Aposta", value=f"🪙 {_format_nex(self.bet_amount)} nex", inline=True)
		embed.add_field(name="Minas", value=f"💣 {self.mines_count}/{BOARD_SIZE}", inline=True)
		embed.add_field(name="Carteira", value=f"💰 {_format_nex(self._wallet_balance())} nex", inline=True)

		embed.add_field(name="Pedras achadas", value=f"💎 {self.safe_reveals}/{self.max_safe_tiles}", inline=True)

		current_multiplier = self._current_multiplier()
		current_payout = self._current_payout()
		embed.add_field(
			name="Multiplicador atual",
			value=f"📈 {current_multiplier:.2f}x\n({_format_nex(current_payout)} nex)",
			inline=True,
		)

		next_multiplier = self._next_multiplier()
		if next_multiplier is None:
			next_text = "Tabuleiro limpo"
		else:
			next_payout = _calculate_payout(self.bet_amount, self.mines_count, self.safe_reveals + 1)
			next_text = f"{next_multiplier:.2f}x\n({_format_nex(next_payout)} nex)"
		embed.add_field(name="Proximo multiplicador", value=f"🎯 {next_text}", inline=True)

		embed.set_footer(text=f"Partida #{self.session_id}")
		return embed

	def _rebuild_items(self) -> None:
		self.clear_items()

		for tile_index in range(BOARD_SIZE):
			revealed = tile_index in self.revealed_tiles
			if self.finished:
				revealed = True
			self.add_item(MinesTileButton(tile_index, revealed, self.board[tile_index], self.finished))

		if self.finished:
			replay_button = discord.ui.Button(
				label="Comecar nova partida",
				emoji="🎮",
				style=discord.ButtonStyle.success,
				row=4,
			)
			replay_button.callback = self.restart_game
			self.add_item(replay_button)
			return

		random_button = discord.ui.Button(
			label="Aleatorio",
			emoji="🎲",
			style=discord.ButtonStyle.primary,
			row=4,
			disabled=not self._hidden_tiles(),
		)
		random_button.callback = self.random_pick
		self.add_item(random_button)

		cashout_button = discord.ui.Button(
			label="Retirar",
			emoji="💰",
			style=discord.ButtonStyle.success,
			row=4,
		)
		cashout_button.callback = self.cashout
		self.add_item(cashout_button)

		refresh_button = discord.ui.Button(
			label="Atualizar",
			emoji="🔄",
			style=discord.ButtonStyle.secondary,
			row=4,
		)
		refresh_button.callback = self.refresh_message
		self.add_item(refresh_button)

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

	async def reveal_tile(self, interaction: discord.Interaction, tile_index: int) -> None:
		if self.finished or tile_index in self.revealed_tiles:
			if interaction.response.is_done():
				await interaction.followup.send("Essa casa ja foi aberta.", ephemeral=True)
			else:
				await interaction.response.send_message("Essa casa ja foi aberta.", ephemeral=True)
			return

		self.revealed_tiles.add(tile_index)

		if self.board[tile_index] == "mine":
			await self.finish_game(interaction, "lost")
			return

		if self.safe_reveals >= self.max_safe_tiles:
			await self.finish_game(interaction, "cleared", payout=self._current_payout())
			return

		await self._sync_message(interaction)

	async def random_pick(self, interaction: discord.Interaction) -> None:
		hidden_tiles = self._hidden_tiles()
		if not hidden_tiles:
			await self._sync_message(interaction)
			return
		await self.reveal_tile(interaction, random.choice(hidden_tiles))

	async def cashout(self, interaction: discord.Interaction) -> None:
		if self.safe_reveals <= 0:
			await self.finish_game(interaction, "refund", payout=self.bet_amount)
			return
		await self.finish_game(interaction, "cashout", payout=self._current_payout())

	async def refresh_message(self, interaction: discord.Interaction) -> None:
		await self._sync_message(interaction)

	async def restart_game(self, interaction: discord.Interaction) -> None:
		await self.cog.restart_game(interaction, self.bet_amount, self.mines_count)

	async def finish_game(self, interaction: discord.Interaction | None, reason: str, payout: int = 0) -> None:
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

		payout = self.bet_amount if self.safe_reveals <= 0 else self._current_payout()
		reason = "timeout_refund" if self.safe_reveals <= 0 else "timeout"
		try:
			await self.finish_game(None, reason, payout=payout)
		except discord.HTTPException:
			self.cog.active_games.pop(self.user_id, None)
			self.stop()


class Mines(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.active_games: dict[int, MinesGameView] = {}

	async def _start_game(self, inte: CommandContextAdapter, bet_amount: int, mines_count: int):
		await economy_profile_created(inte)

		hero = get_active_hero(inte.user.id)
		if hero is None:
			return await inte.response.send_message("Nao consegui localizar seu heroi ativo para iniciar a partida.")

		if inte.user.id in self.active_games:
			return await inte.response.send_message("Voce ja tem uma partida de mines aberta. Termine a atual antes de iniciar outra.")

		bet_validation = validate_bet_amount(inte.user.id, bet_amount, context="esse jogo")
		if not bet_validation.ok:
			return await inte.response.send_message(f"{bet_validation.message} Ex: !mines 1000 3")

		mine_validation = validate_amount_range(mines_count, field_name="minas", minimum=MIN_MINES, maximum=MAX_MINES)
		if not mine_validation.ok:
			return await inte.response.send_message(f"{mine_validation.message} Ex: !mines 1000 3")

		paid = update_active_hero_resources(inte.user.id, nex=-bet_amount)
		if not paid:
			return await inte.response.send_message("Nao foi possivel reservar sua aposta. Tente novamente.")

		view = MinesGameView(self, inte.user.id, bet_amount, mines_count)
		self.active_games[inte.user.id] = view
		message = await inte.response.send_message(embed=view.build_embed(), view=view)
		view.message = message

	async def restart_game(self, interaction: discord.Interaction, bet_amount: int, mines_count: int) -> None:
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
				f"Saldo insuficiente para reiniciar. Carteira atual: {_format_nex(wallet)} nex.",
				ephemeral=True,
			)
			return

		paid = update_active_hero_resources(interaction.user.id, nex=-bet_amount)
		if not paid:
			await interaction.response.send_message("Nao foi possivel reservar a nova aposta.", ephemeral=True)
			return

		view = MinesGameView(self, interaction.user.id, bet_amount, mines_count)
		view.message = interaction.message
		self.active_games[interaction.user.id] = view
		await interaction.response.edit_message(embed=view.build_embed(), view=view)

	@commands.command(
		name="mines",
		aliases=["campo_minado", "mine"],
		help="Jogo de mines com aposta em nex. Ex: !mines 1000 3",
	)
	async def mines(self, ctx: commands.Context, bet_amount: int, mines_count: int = 3):
		inte = CommandContextAdapter(ctx)
		await self._start_game(inte, bet_amount, mines_count)


async def setup(bot: commands.Bot):
	await bot.add_cog(Mines(bot))
