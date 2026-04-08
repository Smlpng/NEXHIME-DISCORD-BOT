import random
import time

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, transfer_wallet_nex
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


def _format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


class Roubar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns: dict[int, float] = {}
        self.cooldown_seconds = 20 * 60

    @staticmethod
    def _format_cooldown(seconds_left: int) -> str:
        minutes, seconds = divmod(max(seconds_left, 0), 60)
        if minutes and seconds:
            return f"{minutes}m {seconds}s"
        if minutes:
            return f"{minutes}m"
        return f"{seconds}s"

    @commands.command(
        name="roubar",
        aliases=["assaltar", "furtar"],
        help="Tenta roubar nex da carteira de outro jogador. Ex: !roubar @usuario",
    )
    async def roubar(self, ctx: commands.Context, member: discord.Member):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        if member.bot:
            return await inte.response.send_message("Voce nao pode roubar bots.")
        if member.id == inte.user.id:
            return await inte.response.send_message("Voce nao pode roubar a si mesmo.")

        attacker = get_active_hero(inte.user.id)
        target = get_active_hero(member.id)
        if attacker is None:
            return await inte.response.send_message("Nao consegui localizar seu heroi ativo.")
        if target is None:
            return await inte.response.send_message(f"{member.display_name} ainda nao tem um heroi ativo.")

        now = time.time()
        available_at = self.cooldowns.get(inte.user.id, 0)
        if available_at > now:
            remaining = self._format_cooldown(int(available_at - now))
            return await inte.response.send_message(
                f"Voce precisa esperar {remaining} para tentar outro roubo.",
                ephemeral=True,
            )

        attacker_wallet = int(attacker.get("nex", 0))
        target_wallet = int(target.get("nex", 0))
        if target_wallet < 50:
            return await inte.response.send_message(
                f"{member.display_name} esta com pouco nex na carteira para valer o risco."
            )

        self.cooldowns[inte.user.id] = now + self.cooldown_seconds

        steal_min = max(25, int(target_wallet * 0.08))
        steal_max = max(steal_min, int(target_wallet * 0.18))
        steal_amount = min(random.randint(steal_min, steal_max), target_wallet, 2500)

        success_chance = 0.42
        if target_wallet > attacker_wallet:
            success_chance -= 0.05
        if attacker_wallet >= target_wallet:
            success_chance += 0.05
        success_chance = max(0.2, min(success_chance, 0.55))

        embed = discord.Embed(title="ðŸ•µï¸ Roubo", color=RPG_PRIMARY_COLOR)

        if random.random() <= success_chance and transfer_wallet_nex(member.id, inte.user.id, steal_amount):
            updated_attacker = get_active_hero(inte.user.id)
            embed.description = f"{inte.user.mention} passou a mao em **{_format_nex(steal_amount)} nex** de {member.mention}."
            embed.add_field(name="Resultado", value="Roubo bem-sucedido.", inline=True)
            embed.add_field(name="Carteira atual", value=f"{_format_nex(updated_attacker['nex'])} nex", inline=True)
            embed.add_field(name="Cooldown", value="20m", inline=True)
            return await inte.response.send_message(embed=embed)

        fine_base = max(20, int(max(attacker_wallet, 1) * 0.1))
        fine_amount = min(fine_base, attacker_wallet, 1200)

        if fine_amount > 0:
            transfer_wallet_nex(inte.user.id, member.id, fine_amount)
            updated_attacker = get_active_hero(inte.user.id)
            embed.description = (
                f"{inte.user.mention} foi pego tentando roubar {member.mention} e perdeu "
                f"**{_format_nex(fine_amount)} nex** de multa."
            )
            embed.add_field(name="Resultado", value="Roubo falhou.", inline=True)
            embed.add_field(name="Carteira atual", value=f"{_format_nex(updated_attacker['nex'])} nex", inline=True)
            embed.add_field(name="Cooldown", value="20m", inline=True)
        else:
            embed.description = (
                f"{inte.user.mention} falhou ao tentar roubar {member.mention}, mas estava sem nex para pagar multa."
            )
            embed.add_field(name="Resultado", value="Roubo falhou.", inline=True)
            embed.add_field(name="Carteira atual", value="0 nex", inline=True)
            embed.add_field(name="Cooldown", value="20m", inline=True)

        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roubar(bot))