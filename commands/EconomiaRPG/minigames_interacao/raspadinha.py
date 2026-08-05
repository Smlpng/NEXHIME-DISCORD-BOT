import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


SCRATCH_SYMBOLS = ["🪙", "💎", "👑", "🍀", "⭐", "💀"]
SCRATCH_SIZE = 6
SCRATCH_COLUMNS = 3


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _calculate_multiplier(cards: list[str]) -> float:
    counts: dict[str, int] = {}
    for symbol in cards:
        counts[symbol] = counts.get(symbol, 0) + 1

    highest = max(counts.values())
    top_symbol = max(counts, key=counts.get)

    if highest == 6 and top_symbol == "ðŸ‘‘":
        return 14.0
    if highest == 6:
        return 10.0
    if highest == 5 and top_symbol == "ðŸ’Ž":
        return 7.5
    if highest == 5:
        return 6.0
    if highest == 4 and top_symbol == "ðŸ’Ž":
        return 4.5
    if highest == 4:
        return 3.5
    if highest == 3:
        return 2.0
    if highest == 2:
        return 1.2
    return 0.0


class ScratchButton(discord.ui.Button):
    def __init__(self, index: int, revealed: bool, symbol: str, finished: bool):
        emoji = symbol if revealed else "❔"
        style = discord.ButtonStyle.success if revealed and symbol != "💀" else discord.ButtonStyle.secondary
        if revealed and symbol == "💀":
            style = discord.ButtonStyle.danger

        super().__init__(label="\u200b", emoji=emoji, style=style, row=index // SCRATCH_COLUMNS, disabled=revealed or finished)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, ScratchView):
            await view.reveal_card(interaction, self.index)


class ScratchView(discord.ui.View):
    def __init__(self, cog: "Raspadinha", user_id: int, bet_amount: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.session_id = random.randint(100000, 999999)
        self.message: discord.Message | None = None
        self.finished = False
        self.final_payout = 0
        self.finish_reason: str | None = None
        self.cards = [random.choice(SCRATCH_SYMBOLS) for _ in range(SCRATCH_SIZE)]
        self.revealed_cards: set[int] = set()
        self._rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Apenas quem comprou esta raspadinha pode raspar os bilhetes.", ephemeral=True)
            return False
        return True

    def _wallet_balance(self) -> int:
        hero = get_active_hero(self.user_id)
        if hero is None:
            return 0
        return int(hero.get("nex", 0))

    def _visible_rows(self) -> list[str]:
        rows = []
        for row_start in range(0, SCRATCH_SIZE, SCRATCH_COLUMNS):
            row = []
            for index in range(row_start, row_start + SCRATCH_COLUMNS):
                    row.append(self.cards[index] if index in self.revealed_cards or self.finished else "❔")
            rows.append(" ".join(row))
        return rows

    def _status_text(self) -> str:
        if self.finish_reason == "completed":
            lucro = self.final_payout - self.bet_amount
            if self.final_payout > 0:
                return f"Cartela concluida. Premio final: {_format_nex(self.final_payout)} nex ({lucro:+,} nex).".replace(",", ".")
            return "Cartela concluida. Nenhuma combinacao premiada apareceu."
        if self.finish_reason == "timeout":
            lucro = self.final_payout - self.bet_amount
            if self.final_payout > 0:
                return f"A raspadinha expirou e foi revelada automaticamente: {_format_nex(self.final_payout)} nex ({lucro:+,} nex).".replace(",", ".")
            return "A raspadinha expirou e foi revelada automaticamente sem premio."
        return "Clique nos 6 botoes abaixo para raspar sua cartela e revelar os simbolos."

    def build_embed(self) -> discord.Embed:
        color = RPG_PRIMARY_COLOR if not self.finished else discord.Color.green()
        embed = discord.Embed(title="🎟 Raspadinha", description="\n".join(self._visible_rows()), color=color)
        embed.add_field(name="Aposta", value=f"{_format_nex(self.bet_amount)} nex", inline=True)
        embed.add_field(name="Raspados", value=f"{len(self.revealed_cards)}/{SCRATCH_SIZE}", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(self._wallet_balance())} nex", inline=True)
        embed.add_field(name="Status", value=self._status_text(), inline=False)
        embed.set_footer(text=f"Partida #{self.session_id} | 6 iguais pagam muito, 3+ iguais ja premiam.")
        return embed

    def _rebuild_items(self) -> None:
        self.clear_items()

        for index in range(SCRATCH_SIZE):
            revealed = index in self.revealed_cards
            self.add_item(ScratchButton(index, revealed, self.cards[index], self.finished))

        if self.finished:
            replay_button = discord.ui.Button(
                label="Nova raspadinha",
                    emoji="🎟",
                style=discord.ButtonStyle.success,
                row=2,
            )
            replay_button.callback = self.restart_game
            self.add_item(replay_button)
            return

        reveal_button = discord.ui.Button(
            label="Raspar aleatorio",
                emoji="🎲",
            style=discord.ButtonStyle.primary,
            row=2,
            disabled=len(self.revealed_cards) >= SCRATCH_SIZE,
        )
        reveal_button.callback = self.reveal_random
        self.add_item(reveal_button)

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

    async def reveal_card(self, interaction: discord.Interaction, index: int) -> None:
        if self.finished or index in self.revealed_cards:
            if interaction.response.is_done():
                await interaction.followup.send("Esse bilhete ja foi raspado.", ephemeral=True)
            else:
                await interaction.response.send_message("Esse bilhete ja foi raspado.", ephemeral=True)
            return

        self.revealed_cards.add(index)

        if len(self.revealed_cards) >= SCRATCH_SIZE:
            await self.finish_game(interaction, "completed")
            return

        await self._sync_message(interaction)

    async def reveal_random(self, interaction: discord.Interaction) -> None:
        hidden = [index for index in range(SCRATCH_SIZE) if index not in self.revealed_cards]
        if not hidden:
            await self._sync_message(interaction)
            return
        await self.reveal_card(interaction, random.choice(hidden))

    async def restart_game(self, interaction: discord.Interaction) -> None:
        await self.cog.restart_game(interaction, self.bet_amount)

    async def finish_game(self, interaction: discord.Interaction | None, reason: str) -> None:
        if self.finished:
            return

        self.finished = True
        self.finish_reason = reason
        self.revealed_cards = set(range(SCRATCH_SIZE))

        multiplier = _calculate_multiplier(self.cards)
        self.final_payout = int(round(self.bet_amount * multiplier)) if multiplier > 0 else 0

        self.cog.active_games.pop(self.user_id, None)
        if self.final_payout > 0:
            update_active_hero_resources(self.user_id, nex=self.final_payout)

        await self._sync_message(interaction)

    async def on_timeout(self) -> None:
        if self.finished:
            return
        try:
            await self.finish_game(None, "timeout")
        except discord.HTTPException:
            self.cog.active_games.pop(self.user_id, None)


class Raspadinha(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games: dict[int, ScratchView] = {}

    async def _start_game(self, inte: CommandContextAdapter, bet_amount: int):
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo para comprar a raspadinha.")
        if inte.user.id in self.active_games:
            return await inte.response.send_message("Voce ja tem uma raspadinha aberta. Termine a atual antes de comprar outra.")
        if bet_amount <= 0:
            return await inte.response.send_message("Informe uma aposta positiva. Ex: !raspadinha 750")

        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            return await inte.response.send_message(
                f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex."
            )

        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            return await inte.response.send_message("Nao foi possivel debitar sua aposta. Tente novamente.")

        view = ScratchView(self, inte.user.id, bet_amount)
        self.active_games[inte.user.id] = view
        message = await inte.response.send_message(embed=view.build_embed(), view=view)
        view.message = message

    async def restart_game(self, interaction: discord.Interaction, bet_amount: int) -> None:
        if interaction.user.id in self.active_games:
            await interaction.response.send_message("Voce ja tem uma raspadinha em andamento.", ephemeral=True)
            return

        hero = get_active_hero(interaction.user.id)
        wallet = int(hero.get("nex", 0)) if hero else 0
        if hero is None:
            await interaction.response.send_message("Nao consegui localizar seu heroi ativo.", ephemeral=True)
            return
        if wallet < bet_amount:
            await interaction.response.send_message(
                f"Saldo insuficiente para uma nova raspadinha. Carteira atual: {_format_nex(wallet)} nex.",
                ephemeral=True,
            )
            return
        if not update_active_hero_resources(interaction.user.id, nex=-bet_amount):
            await interaction.response.send_message("Nao foi possivel debitar a nova aposta.", ephemeral=True)
            return

        view = ScratchView(self, interaction.user.id, bet_amount)
        view.message = interaction.message
        self.active_games[interaction.user.id] = view
        await interaction.response.edit_message(embed=view.build_embed(), view=view)

    @commands.command(
        name="raspadinha",
        aliases=["scratch", "cartela"],
        help="Compra uma raspadinha interativa usando nex. Ex: !raspadinha 750",
    )
    async def raspadinha(self, ctx: commands.Context, bet_amount: int):
        inte = CommandContextAdapter(ctx)
        await self._start_game(inte, bet_amount)


async def setup(bot: commands.Bot):
    await bot.add_cog(Raspadinha(bot))