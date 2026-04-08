import asyncio
import random

import discord
from discord.ext import commands


RACERS = ["🐢", "🐇", "🐉", "🦍", "🐸", "🦊"]


class Corrida(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="corrida", aliases=["race"], help="Faz uma corrida rapida de emojis.")
    async def corrida(self, ctx: commands.Context):
        racers = random.sample(RACERS, 4)
        progress = {emoji: 0 for emoji in racers}

        def render() -> str:
            lines = []
            for emoji in racers:
                track = "-" * progress[emoji]
                finish = "🏁"
                lines.append(f"{emoji} {track}{finish}")
            return "\n".join(lines)

        message = await ctx.reply(embed=discord.Embed(title="Corrida", description=render(), color=discord.Color.green()))
        while True:
            await asyncio.sleep(1)
            for emoji in racers:
                progress[emoji] += random.randint(1, 3)
            winner = next((emoji for emoji in racers if progress[emoji] >= 15), None)
            if winner is not None:
                embed = discord.Embed(title="Corrida", description=render(), color=discord.Color.green())
                embed.add_field(name="Vencedor", value=winner, inline=False)
                await message.edit(embed=embed)
                return
            await message.edit(embed=discord.Embed(title="Corrida", description=render(), color=discord.Color.green()))


async def setup(bot: commands.Bot):
    await bot.add_cog(Corrida(bot))