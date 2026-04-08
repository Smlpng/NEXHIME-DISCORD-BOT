import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import list_economy_leaderboard
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _resolve_name(self, user_id: int, guild: discord.Guild | None) -> str:
        if guild is not None:
            member = guild.get_member(user_id)
            if member is not None:
                return member.display_name
        user = self.bot.get_user(user_id)
        if user is not None:
            return user.display_name
        try:
            fetched = await self.bot.fetch_user(user_id)
            return fetched.display_name
        except discord.HTTPException:
            return str(user_id)

    @commands.command(name="rank")
    async def rank(self, ctx):
        """Mostra o ranking econÃ´mico do RPG."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        leaderboard = list_economy_leaderboard(limit=10)
        if not leaderboard:
            return await inte.response.send_message("Ainda nao ha dados suficientes para gerar o ranking economico.")

        embed = discord.Embed(title="Ranking econÃ´mico", color=RPG_PRIMARY_COLOR)
        lines = []
        medals = {1: "ðŸ¥‡", 2: "ðŸ¥ˆ", 3: "ðŸ¥‰"}
        for index, row in enumerate(leaderboard, start=1):
            name = await self._resolve_name(row["user_id"], inte.guild)
            prefix = medals.get(index, f"{index}.")
            lines.append(
                f"{prefix} **{name}**\n"
                f"Total: {row['total']} nex | Carteira: {row['nex']} | Banco: {row['bank']}"
            )

        embed.description = "\n\n".join(lines)
        embed.set_footer(text="Ranking global baseado no total de nex entre carteira e banco.")
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Rank(bot))