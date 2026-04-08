import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import list_hero_progress_leaderboard
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


class TopHerois(commands.Cog):
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

    @commands.command(name="topherois", aliases=["herorank", "rankherois"])
    async def topherois(self, ctx):
        """Ranking de progressao geral dos herois ativos."""
        inte = CommandContextAdapter(ctx)
        rows = list_hero_progress_leaderboard(limit=10)
        if not rows:
            return await inte.response.send_message("Ainda nao ha herois suficientes para montar o ranking.")

        medals = {1: "ðŸ¥‡", 2: "ðŸ¥ˆ", 3: "ðŸ¥‰"}
        lines = []
        for index, row in enumerate(rows, start=1):
            name = await self._resolve_name(row["user_id"], inte.guild)
            prefix = medals.get(index, f"{index}.")
            lines.append(
                f"{prefix} **{name}**\n"
                f"Nivel {row['level']} | XP {row['xp']} | Abates {row['kills']} | Melhorias {row['upgrades']} | Bestiario {row['seen']} | Score {row['score']}"
            )

        embed = discord.Embed(title="Top Herois", description="\n\n".join(lines), color=RPG_PRIMARY_COLOR)
        embed.set_footer(text="Score baseado em nivel, XP, abates, melhorias e progresso no bestiario.")
        await inte.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(TopHerois(bot))