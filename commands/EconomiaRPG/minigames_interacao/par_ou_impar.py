import random

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class NumberChoiceButton(discord.ui.Button):
    def __init__(self, number: int):
        super().__init__(label=str(number), style=discord.ButtonStyle.primary)
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, ParOuImparGameView):
            await view.pick_number(interaction, self.number)


class ParityButton(discord.ui.Button):
    def __init__(self, label: str, value: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, ParOuImparGameView):
            await view.choose_parity(interaction, self.value)


class ParOuImparGameView(discord.ui.View):
    def __init__(self, cog: "ParOuImpar", challenger: discord.abc.User, target: discord.abc.User, bet_amount: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.challenger = challenger
        self.target = target
        self.bet_amount = bet_amount
        self.session_id = random.randint(100000, 999999)
        self.message: discord.Message | None = None
        self.parity_choice: str | None = None
        self.player_numbers: dict[int, int] = {}
        self.finished = False
        self.finish_reason: str | None = None
        self.winner_id: int | None = None
        self._rebuild_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in {self.challenger.id, self.target.id}:
            await interaction.response.send_message("Apenas os dois jogadores podem participar deste duelo.", ephemeral=True)
            return False
        return True

    def _wallet_balance(self, user_id: int) -> int:
        hero = get_active_hero(user_id)
        if hero is None:
            return 0
        return int(hero.get("nex", 0))

    def _status_text(self) -> str:
        if self.finish_reason == "win":
            total = self.player_numbers[self.challenger.id] + self.player_numbers[self.target.id]
            parity_label = "Par" if total % 2 == 0 else "Impar"
            winner = self.challenger if self.winner_id == self.challenger.id else self.target
            return (
                f"Soma: {total} ({parity_label}). {winner.mention} venceu e levou "
                f"{_format_nex(self.bet_amount * 2)} nex."
            )
        if self.finish_reason == "refund":
            return "O duelo expirou antes do resultado. As apostas foram devolvidas."
        if self.parity_choice is None:
            return f"{self.challenger.mention} precisa escolher Par ou Impar para abrir a rodada."
        return "Agora cada jogador escolhe um numero de 0 a 5. Quando os dois travarem a escolha, o resultado sai na hora."

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(title="✌️ Par ou Impar", description=self._status_text(), color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Aposta por jogador", value=f"{_format_nex(self.bet_amount)} nex", inline=True)
        embed.add_field(name="Pot total", value=f"{_format_nex(self.bet_amount * 2)} nex", inline=True)
        embed.add_field(name="Mesa", value=f"Partida #{self.session_id}", inline=True)
        embed.add_field(name="Desafiante", value=self.challenger.mention, inline=True)
        embed.add_field(name="Oponente", value=self.target.mention, inline=True)
        embed.add_field(name="Paridade escolhida", value=self.parity_choice or "Aguardando", inline=True)
        challenger_pick = self.player_numbers.get(self.challenger.id)
        target_pick = self.player_numbers.get(self.target.id)
        embed.add_field(name=self.challenger.display_name, value=str(challenger_pick) if self.finished and challenger_pick is not None else "Travado" if challenger_pick is not None else "Pendente", inline=True)
        embed.add_field(name=self.target.display_name, value=str(target_pick) if self.finished and target_pick is not None else "Travado" if target_pick is not None else "Pendente", inline=True)
        embed.add_field(name="Carteira desafiante", value=f"{_format_nex(self._wallet_balance(self.challenger.id))} nex", inline=True)
        embed.add_field(name="Carteira oponente", value=f"{_format_nex(self._wallet_balance(self.target.id))} nex", inline=True)
        embed.set_footer(text="O desafiante escolhe a paridade. O vencedor leva o pot inteiro.")
        return embed

    def _rebuild_items(self) -> None:
        self.clear_items()
        if self.finished:
            return
        if self.parity_choice is None:
            self.add_item(ParityButton("Par", "Par"))
            self.add_item(ParityButton("Impar", "Impar"))
            return

        for number in range(6):
            self.add_item(NumberChoiceButton(number))

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

    async def choose_parity(self, interaction: discord.Interaction, value: str) -> None:
        if interaction.user.id != self.challenger.id:
            await interaction.response.send_message("Somente o desafiante pode escolher a paridade.", ephemeral=True)
            return
        if self.parity_choice is not None:
            await interaction.response.send_message("A paridade ja foi escolhida para esta rodada.", ephemeral=True)
            return
        self.parity_choice = value
        await self._sync_message(interaction)

    async def pick_number(self, interaction: discord.Interaction, number: int) -> None:
        if self.parity_choice is None:
            await interaction.response.send_message("A rodada ainda nao teve a paridade definida.", ephemeral=True)
            return
        if interaction.user.id in self.player_numbers:
            await interaction.response.send_message("Voce ja travou seu numero nesta rodada.", ephemeral=True)
            return
        self.player_numbers[interaction.user.id] = number
        if len(self.player_numbers) < 2:
            await self._sync_message(interaction)
            return
        await self.finish_game(interaction, refund=False)

    async def finish_game(self, interaction: discord.Interaction | None, refund: bool) -> None:
        if self.finished:
            return
        self.finished = True
        self.finish_reason = "refund" if refund else "win"
        self.cog._release_users(self.challenger.id, self.target.id)

        if refund:
            update_active_hero_resources(self.challenger.id, nex=self.bet_amount)
            update_active_hero_resources(self.target.id, nex=self.bet_amount)
        else:
            challenger_number = self.player_numbers[self.challenger.id]
            target_number = self.player_numbers[self.target.id]
            total = challenger_number + target_number
            result_is_even = total % 2 == 0
            challenger_wins = (self.parity_choice == "Par" and result_is_even) or (self.parity_choice == "Impar" and not result_is_even)
            winner_id = self.challenger.id if challenger_wins else self.target.id
            self.winner_id = winner_id
            update_active_hero_resources(winner_id, nex=self.bet_amount * 2)

        await self._sync_message(interaction)

    async def on_timeout(self) -> None:
        if self.finished:
            return
        try:
            await self.finish_game(None, refund=True)
        except discord.HTTPException:
            self.cog._release_users(self.challenger.id, self.target.id)


class ParOuImparInviteView(discord.ui.View):
    def __init__(self, cog: "ParOuImpar", challenger: discord.abc.User, target: discord.abc.User, bet_amount: int):
        super().__init__(timeout=120)
        self.cog = cog
        self.challenger = challenger
        self.target = target
        self.bet_amount = bet_amount
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Somente o jogador desafiado pode responder este convite.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        challenger_hero = get_active_hero(self.challenger.id)
        target_hero = get_active_hero(self.target.id)
        if challenger_hero is None or target_hero is None:
            self.cog._release_users(self.challenger.id, self.target.id)
            await interaction.response.edit_message(content="Um dos dois jogadores nao possui heroi ativo.", embed=None, view=None)
            return

        challenger_wallet = int(challenger_hero.get("nex", 0))
        target_wallet = int(target_hero.get("nex", 0))
        if challenger_wallet < self.bet_amount or target_wallet < self.bet_amount:
            self.cog._release_users(self.challenger.id, self.target.id)
            await interaction.response.edit_message(
                content="Um dos jogadores nao tem saldo suficiente para pagar a aposta.",
                embed=None,
                view=None,
            )
            return

        if not update_active_hero_resources(self.challenger.id, nex=-self.bet_amount):
            self.cog._release_users(self.challenger.id, self.target.id)
            await interaction.response.edit_message(content="Nao foi possivel reservar a aposta do desafiante.", embed=None, view=None)
            return
        if not update_active_hero_resources(self.target.id, nex=-self.bet_amount):
            update_active_hero_resources(self.challenger.id, nex=self.bet_amount)
            self.cog._release_users(self.challenger.id, self.target.id)
            await interaction.response.edit_message(content="Nao foi possivel reservar a aposta do oponente.", embed=None, view=None)
            return

        game_view = ParOuImparGameView(self.cog, self.challenger, self.target, self.bet_amount)
        game_view.message = interaction.message
        self.cog.active_games[(self.challenger.id, self.target.id)] = game_view
        await interaction.response.edit_message(content=None, embed=game_view.build_embed(), view=game_view)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.cog._release_users(self.challenger.id, self.target.id)
        await interaction.response.edit_message(content=f"{self.target.mention} recusou o duelo.", embed=None, view=None)

    async def on_timeout(self) -> None:
        self.cog._release_users(self.challenger.id, self.target.id)
        if self.message is not None:
            try:
                await self.message.edit(content="O convite de par ou impar expirou.", embed=None, view=None)
            except discord.HTTPException:
                pass


class ParOuImpar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.busy_users: set[int] = set()
        self.active_games: dict[tuple[int, int], ParOuImparGameView] = {}

    def _reserve_users(self, user_a: int, user_b: int) -> bool:
        if user_a in self.busy_users or user_b in self.busy_users:
            return False
        self.busy_users.add(user_a)
        self.busy_users.add(user_b)
        return True

    def _release_users(self, user_a: int, user_b: int) -> None:
        self.busy_users.discard(user_a)
        self.busy_users.discard(user_b)
        self.active_games.pop((user_a, user_b), None)
        self.active_games.pop((user_b, user_a), None)

    @commands.command(
        name="parouimpar",
        aliases=["par_impar", "dueloimpar"],
        help="Desafia outro jogador para um par ou impar apostando nex. Ex: !parouimpar @user 500",
    )
    async def parouimpar(self, ctx: commands.Context, member: discord.Member, bet_amount: int) -> None:
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        if member.bot:
            await inte.response.send_message("Voce nao pode desafiar bots.")
            return
        if member.id == inte.user.id:
            await inte.response.send_message("Voce nao pode desafiar a si mesmo.")
            return
        if bet_amount <= 0:
            await inte.response.send_message("Informe uma aposta positiva. Ex: !parouimpar @user 500")
            return

        challenger_hero = get_active_hero(inte.user.id)
        target_hero = get_active_hero(member.id)
        if challenger_hero is None:
            await inte.response.send_message("Nao consegui localizar seu heroi ativo.")
            return
        if target_hero is None:
            await inte.response.send_message(f"{member.display_name} ainda nao possui heroi ativo.")
            return
        if int(challenger_hero.get("nex", 0)) < bet_amount:
            await inte.response.send_message(
                f"Voce nao tem nex suficiente. Carteira atual: {_format_nex(challenger_hero.get('nex', 0))} nex."
            )
            return
        if int(target_hero.get("nex", 0)) < bet_amount:
            await inte.response.send_message(
                f"{member.display_name} nao tem saldo suficiente para cobrir a aposta agora."
            )
            return
        if not self._reserve_users(inte.user.id, member.id):
            await inte.response.send_message("Um dos dois jogadores ja esta ocupado em outro minigame multiplayer.")
            return

        view = ParOuImparInviteView(self, inte.user, member, bet_amount)
        embed = discord.Embed(title="✌️ Convite de Par ou Impar", color=RPG_PRIMARY_COLOR)
        embed.description = (
            f"{inte.user.mention} desafiou {member.mention} para um duelo valendo {_format_nex(bet_amount)} nex cada."
        )
        embed.add_field(name="Pot total", value=f"{_format_nex(bet_amount * 2)} nex", inline=True)
        embed.add_field(name="Resposta", value="O jogador desafiado tem 2 minutos para aceitar.", inline=True)
        message = await inte.response.send_message(embed=embed, view=view)
        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(ParOuImpar(bot))