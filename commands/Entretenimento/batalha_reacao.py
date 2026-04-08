import asyncio
import random

import discord
from discord.ext import commands


TARGETS = ["🍌", "🔥", "⚔️", "👑", "🐉"]


class BatalhaReacao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="batalha_reacao", aliases=["reactionbattle"], help="Quem reagir primeiro ao emoji certo vence.")
    async def batalha_reacao(self, ctx: commands.Context):
        target = random.choice(TARGETS)
        message = await ctx.reply("Preparem-se para a batalha de reacao...")
        await asyncio.sleep(random.uniform(2.0, 4.5))
        await message.edit(content=f"REAJAM COM {target}")
        await message.add_reaction(target)

        def check(reaction: discord.Reaction, user: discord.User):
            return reaction.message.id == message.id and str(reaction.emoji) == target and not user.bot

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=20, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Ninguem reagiu a tempo.")
        await ctx.send(f"{user.mention} venceu a batalha de reacao.")


async def setup(bot: commands.Bot):
    await bot.add_cog(BatalhaReacao(bot))