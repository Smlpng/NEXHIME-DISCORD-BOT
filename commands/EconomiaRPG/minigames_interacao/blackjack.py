import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


CARD_RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _draw_card() -> str:
    return random.choice(CARD_RANKS)


def _hand_value(hand: list[str]) -> int:
    total = 0
    aces = 0
    for card in hand:
        if card == "A":
            total += 11
            aces += 1
        elif card in {"J", "Q", "K"}:
            total += 10
        else:
            total += int(card)

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def _hand_text(hand: list[str], hide_first: bool = False) -> str:
    if hide_first and hand:
        shown = ["?", *hand[1:]]
        return " ".join(shown)
    return " ".join(hand)


class BlackjackView(discord.ui.View):
    def __init__(self, cog: "Blackjack", user_id: int, bet_amount: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.session_id = random.randint(100000, 999999)
        self.message: discord.Message | None = None
        self.player_hand = [_draw_card(), _draw_card()]
        self.dealer_hand = [_draw_card(), _draw_card()]
        self.finished = False
        self.finish_reason: str | None = None
        self.final_payout = 0
        self._rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Apenas quem abriu esta mesa pode jogar a mao atual.", ephemeral=True)
            return False
        return True

    def _wallet_balance(self) -> int:
        hero = get_active_hero(self.user_id)
        if hero is None:
            return 0
        return int(hero.get("nex", 0))

    def _status_text(self) -> str:
        if self.finish_reason == "blackjack":
            lucro = self.final_payout - self.bet_amount
            return f"Blackjack natural. Voce recebeu {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
        if self.finish_reason == "win":
            lucro = self.final_payout - self.bet_amount
            return f"Voce venceu a mesa e recebeu {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
        if self.finish_reason == "push":
            return "Empate com o dealer. Sua aposta foi devolvida."
        if self.finish_reason == "loss":
            return "A casa venceu esta rodada."
        if self.finish_reason == "timeout":
            if self.final_payout > 0:
                lucro = self.final_payout - self.bet_amount
                return f"Tempo esgotado. A rodada foi encerrada e voce ficou com {_format_nex(self.final_payout)} nex ({lucro:+,}).".replace(",", ".")
            return "Tempo esgotado. A casa ficou com a aposta."
        return "Tente chegar o mais perto possivel de 21 sem estourar."

    def build_embed(self) -> discord.Embed:
        player_value = _hand_value(self.player_hand)
        dealer_value = _hand_value(self.dealer_hand)
        color = RPG_PRIMARY_COLOR if not self.finished else discord.Color.green() if self.final_payout > 0 else discord.Color.red()
        if self.finish_reason == "push":
            color = discord.Color.gold()

        embed = discord.Embed(title="🃏 Blackjack", description=self._status_text(), color=color)
        embed.add_field(name="Aposta", value=f"{_format_nex(self.bet_amount)} nex", inline=True)
        embed.add_field(name="Carteira", value=f"{_format_nex(self._wallet_balance())} nex", inline=True)
        embed.add_field(name="Mesa", value=f"Partida #{self.session_id}", inline=True)
        embed.add_field(
            name="Sua mao",
            value=f"{_hand_text(self.player_hand)}\nTotal: {player_value}",
            inline=False,
        )
        embed.add_field(
            name="Dealer",
            value=(
                f"{_hand_text(self.dealer_hand, hide_first=not self.finished)}\n"
                f"Total: {dealer_value if self.finished else '?'}"
            ),
            inline=False,
        )
        embed.set_footer(text="Blackjack paga 2.5x. Vitoria comum paga 2x.")
        return embed

    def _rebuild_items(self) -> None:
        self.clear_items()
        if self.finished:
            replay_button = discord.ui.Button(label="Nova mao", emoji="🎮", style=discord.ButtonStyle.success)
            replay_button.callback = self.restart_game
            self.add_item(replay_button)
            return

        hit_button = discord.ui.Button(label="Comprar", emoji="➕", style=discord.ButtonStyle.primary)
        hit_button.callback = self.hit
        self.add_item(hit_button)

        stand_button = discord.ui.Button(label="Parar", emoji="✋", style=discord.ButtonStyle.secondary)
        stand_button.callback = self.stand
        self.add_item(stand_button)

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

    async def hit(self, interaction: discord.Interaction) -> None:
        if self.finished:
            return
        self.player_hand.append(_draw_card())
        if _hand_value(self.player_hand) > 21:
            await self.finish_game(interaction, "loss", payout=0)
            return
        await self._sync_message(interaction)

    async def stand(self, interaction: discord.Interaction | None = None) -> None:
        if self.finished:
            return
        while _hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(_draw_card())

        player_value = _hand_value(self.player_hand)
        dealer_value = _hand_value(self.dealer_hand)
        if dealer_value > 21 or player_value > dealer_value:
            await self.finish_game(interaction, "win", payout=self.bet_amount * 2)
        elif dealer_value == player_value:
            await self.finish_game(interaction, "push", payout=self.bet_amount)
        else:
            await self.finish_game(interaction, "loss", payout=0)

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
        try:
            await self.stand(None)
            if not self.finished:
                await self.finish_game(None, "timeout", payout=0)
            else:
                self.finish_reason = "timeout"
                await self._sync_message(None)
        except discord.HTTPException:
            self.cog.active_games.pop(self.user_id, None)


class Blackjack(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games: dict[int, BlackjackView] = {}

    async def _start_game(self, inte: CommandContextAdapter, bet_amount: int) -> None:
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            await inte.response.send_message("Nao consegui localizar seu heroi ativo para iniciar o blackjack.")
            return
        if inte.user.id in self.active_games:
            await inte.response.send_message("Voce ja tem uma mesa de blackjack aberta.")
            return
        if bet_amount <= 0:
            await inte.response.send_message("Informe uma aposta positiva. Ex: !blackjack 500")
            return
        wallet = int(hero.get("nex", 0))
        if wallet < bet_amount:
            await inte.response.send_message(f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(wallet)} nex.")
            return
        if not update_active_hero_resources(inte.user.id, nex=-bet_amount):
            await inte.response.send_message("Nao foi possivel reservar sua aposta. Tente novamente.")
            return

        view = BlackjackView(self, inte.user.id, bet_amount)
        self.active_games[inte.user.id] = view
        message = await inte.response.send_message(embed=view.build_embed(), view=view)
        view.message = message

        if _hand_value(view.player_hand) == 21:
            dealer_value = _hand_value(view.dealer_hand)
            if dealer_value == 21:
                await view.finish_game(None, "push", payout=bet_amount)
            else:
                await view.finish_game(None, "blackjack", payout=int(round(bet_amount * 2.5)))

    async def restart_game(self, interaction: discord.Interaction, bet_amount: int) -> None:
        if interaction.user.id in self.active_games:
            await interaction.response.send_message("Voce ja tem uma mesa em andamento.", ephemeral=True)
            return
        hero = get_active_hero(interaction.user.id)
        wallet = int(hero.get("nex", 0)) if hero else 0
        if hero is None:
            await interaction.response.send_message("Nao consegui localizar seu heroi ativo.", ephemeral=True)
            return
        if wallet < bet_amount:
            await interaction.response.send_message(
                f"Saldo insuficiente para uma nova mao. Carteira atual: {_format_nex(wallet)} nex.",
                ephemeral=True,
            )
            return
        if not update_active_hero_resources(interaction.user.id, nex=-bet_amount):
            await interaction.response.send_message("Nao foi possivel reservar a nova aposta.", ephemeral=True)
            return

        view = BlackjackView(self, interaction.user.id, bet_amount)
        view.message = interaction.message
        self.active_games[interaction.user.id] = view
        await interaction.response.edit_message(embed=view.build_embed(), view=view)

        if _hand_value(view.player_hand) == 21:
            dealer_value = _hand_value(view.dealer_hand)
            if dealer_value == 21:
                await view.finish_game(None, "push", payout=bet_amount)
            else:
                await view.finish_game(None, "blackjack", payout=int(round(bet_amount * 2.5)))

    @commands.command(name="blackjack", aliases=["bj", "vinteum"], help="Mesa de blackjack apostando nex. Ex: !blackjack 500")
    async def blackjack(self, ctx: commands.Context, bet_amount: int) -> None:
        inte = CommandContextAdapter(ctx)
        await self._start_game(inte, bet_amount)


async def setup(bot: commands.Bot):
    await bot.add_cog(Blackjack(bot))