import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import (
    deposit_nex_to_bank,
    get_active_hero,
    get_bank_balance,
    transfer_wallet_nex,
    withdraw_nex_from_bank,
)
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR, add_spacer
from commands.EconomiaRPG.utils.validators import format_nex, validate_positive_amount, validate_wallet_balance


class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _build_bank_embed(display_name: str, wallet: int, bank_balance: int):
        embed = discord.Embed(title=f"Banco de {display_name}", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Carteira", value=f"{wallet} nex", inline=True)
        embed.add_field(name="Banco", value=f"{bank_balance} nex", inline=True)
        embed.add_field(name="Total", value=f"{wallet + bank_balance} nex", inline=False)
        add_spacer(embed)
        embed.add_field(name="MovimentaÃ§Ãµes", value="Use depositar, sacar e transferir para mover seu nex com seguranÃ§a.", inline=False)
        return embed

    @commands.command(name="banco")
    async def banco(self, ctx):
        """Mostra a carteira e o saldo bancario."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        bank_balance = get_bank_balance(inte.user.id)
        wallet = hero["nex"] if hero else 0

        embed = self._build_bank_embed(inte.user.display_name, wallet, bank_balance)
        embed.set_footer(text="Resumo da sua economia atual.")

        await inte.response.send_message(embed=embed)

    @commands.command(name="depositar")
    async def depositar(self, ctx, amount: int):
        """Deposita nex da carteira no banco."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce ainda nao tem um heroi para depositar nex da carteira.")

        amount_validation = validate_positive_amount(amount)
        if not amount_validation.ok:
            return await inte.response.send_message(amount_validation.message.replace("quantidade", "quantidade para depositar"))

        balance_validation = validate_wallet_balance(inte.user.id, amount, context="esse deposito")
        if not balance_validation.ok:
            return await inte.response.send_message(balance_validation.message)

        if not deposit_nex_to_bank(inte.user.id, amount):
            return await inte.response.send_message("Voce nao tem nex suficiente na carteira para esse deposito.")

        hero = get_active_hero(inte.user.id)
        embed = self._build_bank_embed(inte.user.display_name, hero["nex"], get_bank_balance(inte.user.id))
        embed.description = f"Deposito concluido: {format_nex(amount)} nex foram enviados para o banco."
        await inte.response.send_message(embed=embed)

    @commands.command(name="sacar")
    async def sacar(self, ctx, amount: int):
        """Saca nex do banco para a carteira."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce ainda nao tem um heroi para receber o saque de nex na carteira.")

        amount_validation = validate_positive_amount(amount, field_name="quantidade para sacar")
        if not amount_validation.ok:
            return await inte.response.send_message(amount_validation.message)

        if not withdraw_nex_from_bank(inte.user.id, amount):
            return await inte.response.send_message("Voce nao tem saldo suficiente em nex no banco para esse saque.")

        hero = get_active_hero(inte.user.id)
        embed = self._build_bank_embed(inte.user.display_name, hero["nex"], get_bank_balance(inte.user.id))
        embed.description = f"Saque concluido: {format_nex(amount)} nex voltaram para a sua carteira."
        await inte.response.send_message(embed=embed)

    @commands.command(name="transferir")
    async def transferir(self, ctx, member: discord.Member, amount: int):
        """Transfere nex da sua carteira para a carteira de outro jogador."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        if member.bot:
            return await inte.response.send_message("Voce nao pode transferir nex para bots.")
        if member.id == inte.user.id:
            return await inte.response.send_message("Voce nao pode transferir nex para si mesmo.")
        amount_validation = validate_positive_amount(amount, field_name="quantidade para transferir")
        if not amount_validation.ok:
            return await inte.response.send_message(amount_validation.message)

        balance_validation = validate_wallet_balance(inte.user.id, amount, context="essa transferencia")
        if not balance_validation.ok:
            return await inte.response.send_message(balance_validation.message)

        target_hero = get_active_hero(member.id)
        if target_hero is None:
            return await inte.response.send_message(
                f"{member.display_name} ainda nao tem um heroi ativo para receber nex."
            )

        if not transfer_wallet_nex(inte.user.id, member.id, amount):
            hero = get_active_hero(inte.user.id)
            wallet = hero["nex"] if hero else 0
            return await inte.response.send_message(
                f"Voce nao tem nex suficiente na carteira para essa transferencia. Carteira atual: {format_nex(wallet)} nex."
            )

        hero = get_active_hero(inte.user.id)
        wallet = hero["nex"] if hero else 0
        embed = self._build_bank_embed(inte.user.display_name, wallet, get_bank_balance(inte.user.id))
        embed.description = f"Transferencia concluida: {format_nex(amount)} nex foram enviados para a carteira de {member.display_name}."
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Bank(bot))
