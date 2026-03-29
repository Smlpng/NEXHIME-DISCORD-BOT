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


class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="banco")
    async def banco(self, ctx):
        """Mostra a carteira e o saldo bancario."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        bank_balance = get_bank_balance(inte.user.id)
        wallet = hero["nex"] if hero else 0

        embed = discord.Embed(title="Banco do Bando", color=discord.Color.gold())
        embed.add_field(name="Carteira", value=f"{wallet} nex", inline=True)
        embed.add_field(name="Banco", value=f"{bank_balance} nex", inline=True)
        embed.add_field(name="Total", value=f"{wallet + bank_balance} nex", inline=False)
        embed.set_footer(text="Use depositar, sacar e transferir para mover seu nex.")

        await inte.response.send_message(embed=embed)

    @commands.hybrid_command(name="depositar")
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

        await inte.response.send_message(f"Voce depositou {amount} nex no banco.")

    @commands.hybrid_command(name="sacar")
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

        await inte.response.send_message(f"Voce sacou {amount} nex do banco.")

    @commands.hybrid_command(name="transferir")
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

        await inte.response.send_message(
            f"Voce transferiu {amount} nex para {member.display_name}. O valor foi enviado para o banco do jogador."
        )


async def setup(bot):
    await bot.add_cog(Bank(bot))
