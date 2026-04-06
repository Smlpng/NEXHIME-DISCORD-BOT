import asyncio
import random
import re

import discord
from discord.ext import commands


def _parse_duration(value: str) -> int | None:
    """Converts strings like '1m', '2h', '30s', '1d' to seconds."""
    match = re.fullmatch(r"(\d+)([smhd])", value.strip().lower())
    if not match:
        return None
    amount = int(match.group(1))
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[match.group(2)]
    return max(1, amount * mult)


_GIVEAWAY_EMOJI = "🎉"


class Sorteio(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="sorteio",
        aliases=["giveaway", "rifar"],
        help="Cria um sorteio. Ex: !sorteio 5m Nitro. Reaja com 🎉 para participar.",
    )
    @commands.has_permissions(manage_guild=True)
    async def sorteio(self, ctx: commands.Context, duracao: str, *, premio: str):
        """Cria um sorteio onde membros reagem para participar."""
        seconds = _parse_duration(duracao)
        if seconds is None:
            return await ctx.reply(
                "❌ Duração inválida. Use algo como `30s`, `5m`, `2h`, `1d`.",
                mention_author=False,
            )

        end_ts = int(discord.utils.utcnow().timestamp()) + seconds
        embed = discord.Embed(
            title="🎉 SORTEIO 🎉",
            description=(
                f"**Prêmio:** {premio}\n\n"
                f"Reaja com {_GIVEAWAY_EMOJI} para participar!\n"
                f"⏳ Encerra em <t:{end_ts}:R> (<t:{end_ts}:f>)"
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Promovido por {ctx.author.display_name}")
        message = await ctx.send(embed=embed)
        try:
            await message.add_reaction(_GIVEAWAY_EMOJI)
        except Exception:
            pass

        await asyncio.sleep(seconds)

        try:
            message = await ctx.channel.fetch_message(message.id)
        except Exception:
            return

        reaction = discord.utils.get(message.reactions, emoji=_GIVEAWAY_EMOJI)
        participants = []
        if reaction:
            async for user in reaction.users():
                if not user.bot:
                    participants.append(user)

        if not participants:
            result_embed = discord.Embed(
                title="🎉 Sorteio Encerrado",
                description=f"**Prêmio:** {premio}\n\n❌ Nenhum participante válido.",
                color=discord.Color.red(),
            )
        else:
            winner = random.choice(participants)
            result_embed = discord.Embed(
                title="🎉 Sorteio Encerrado",
                description=f"**Prêmio:** {premio}\n\n🏆 Vencedor: {winner.mention} — Parabéns!",
                color=discord.Color.green(),
            )
        result_embed.set_footer(text=f"Promovido por {ctx.author.display_name}")
        await message.reply(embed=result_embed, mention_author=False)

    @commands.command(
        name="resorteio",
        aliases=["reroll", "re_sorteio"],
        help="Escolhe um novo vencedor para o sorteio mais recente do canal.",
    )
    @commands.has_permissions(manage_guild=True)
    async def resorteio(self, ctx: commands.Context, message_id: int | None = None):
        """Re-sorteia um vencedor a partir do ID de uma mensagem de sorteio."""
        if message_id:
            try:
                message = await ctx.channel.fetch_message(message_id)
            except Exception:
                return await ctx.reply("❌ Mensagem não encontrada neste canal.", mention_author=False)
        else:
            return await ctx.reply(
                "Forneça o ID da mensagem de sorteio. Ex: `!resorteio 123456789`",
                mention_author=False,
            )

        reaction = discord.utils.get(message.reactions, emoji=_GIVEAWAY_EMOJI)
        participants = []
        if reaction:
            async for user in reaction.users():
                if not user.bot:
                    participants.append(user)

        if not participants:
            return await ctx.reply("❌ Nenhum participante válido encontrado.", mention_author=False)

        winner = random.choice(participants)
        await ctx.reply(f"🎉 Novo vencedor: {winner.mention} — Parabéns!", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Sorteio(bot))
