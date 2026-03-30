import random
import time

import discord
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import claim_daily_nex, get_active_hero, get_daily_remaining_seconds
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR
from commands.RPG.utils.progress import add_nex_spent


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_seconds = 24 * 60 * 60

    @staticmethod
    def _format_remaining(seconds_left: int) -> str:
        hours, remainder = divmod(max(seconds_left, 0), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}h {minutes}m"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    @commands.hybrid_command(name="daily")
    async def daily(self, ctx):
        """Coleta sua recompensa diária de nex."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message(
                "Seu perfil economico foi criado, mas voce ainda precisa de um heroi para resgatar a recompensa diaria."
            )

        now_ts = time.time()
        reward = random.randint(180, 320)
        claimed, remaining = claim_daily_nex(inte.user.id, reward, self.cooldown_seconds, now_ts)
        if not claimed:
            if remaining <= 0:
                remaining = get_daily_remaining_seconds(inte.user.id, self.cooldown_seconds, now_ts)
            return await inte.response.send_message(
                f"Voce ja resgatou seu daily hoje. Tente novamente em {self._format_remaining(remaining)}.",
                ephemeral=True,
            )

        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="Recompensa diária", color=RPG_PRIMARY_COLOR)
        embed.description = f"{inte.user.mention} recebeu **{reward} nex** pela recompensa diária."
        embed.add_field(name="Carteira atual", value=f"{hero['nex']} nex", inline=True)
        embed.add_field(name="Próximo resgate", value="Daqui a 24 horas", inline=True)
        embed.set_footer(text="Volte amanhã para coletar mais nex.")
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Daily(bot))