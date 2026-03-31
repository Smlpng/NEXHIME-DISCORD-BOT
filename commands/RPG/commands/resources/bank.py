import discord
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import (
    deposit_nex_to_bank,
    get_active_hero,
    get_bank_balance,
    transfer_bank_nex,
    withdraw_nex_from_bank,
)
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR, add_spacer


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
        embed.add_field(name="Movimentações", value="Use depositar, sacar e transferir para mover seu nex com segurança.", inline=False)
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

        if amount <= 0:
            return await inte.response.send_message("Informe uma quantidade positiva para depositar.")

        if not deposit_nex_to_bank(inte.user.id, amount):
            return await inte.response.send_message("Voce nao tem nex suficiente na carteira para esse deposito.")

        hero = get_active_hero(inte.user.id)
        embed = self._build_bank_embed(inte.user.display_name, hero["nex"], get_bank_balance(inte.user.id))
        embed.description = f"Depósito concluído: {amount} nex foram enviados para o banco."
        await inte.response.send_message(embed=embed)

    @commands.command(name="sacar")
    async def sacar(self, ctx, amount: int):
        """Saca nex do banco para a carteira."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce ainda nao tem um heroi para receber o saque de nex na carteira.")

        if amount <= 0:
            return await inte.response.send_message("Informe uma quantidade positiva para sacar.")

        if not withdraw_nex_from_bank(inte.user.id, amount):
            return await inte.response.send_message("Voce nao tem saldo suficiente em nex no banco para esse saque.")

        hero = get_active_hero(inte.user.id)
        embed = self._build_bank_embed(inte.user.display_name, hero["nex"], get_bank_balance(inte.user.id))
        embed.description = f"Saque concluído: {amount} nex voltaram para a sua carteira."
        await inte.response.send_message(embed=embed)

    @commands.command(name="transferir")
    async def transferir(self, ctx, member: discord.Member, amount: int):
        """Transfere nex do seu banco para o banco de outro jogador."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        if member.bot:
            return await inte.response.send_message("Voce nao pode transferir nex para bots.")
        if member.id == inte.user.id:
            return await inte.response.send_message("Voce nao pode transferir nex para si mesmo.")
        if amount <= 0:
            return await inte.response.send_message("Informe uma quantidade positiva para transferir.")

        if not transfer_bank_nex(inte.user.id, member.id, amount):
            return await inte.response.send_message("Voce nao tem saldo suficiente em nex no banco para essa transferencia.")

        hero = get_active_hero(inte.user.id)
        wallet = hero["nex"] if hero else 0
        embed = self._build_bank_embed(inte.user.display_name, wallet, get_bank_balance(inte.user.id))
        embed.description = f"Transferência concluída: {amount} nex foram enviados para o banco de {member.display_name}."
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Bank(bot))
