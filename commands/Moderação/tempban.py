import asyncio
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


class TempBan(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _hierarchy_ok(self, ctx: commands.Context, target: discord.Member) -> bool:
        return ctx.author.top_role > target.top_role and ctx.guild.me.top_role > target.top_role

    @commands.command(
        name="tempban",
        aliases=["bantemp", "bantemporal"],
        help="Bane temporariamente um membro. Ex: !tempban @membro 1h Spam",
    )
    @commands.has_permissions(ban_members=True)
    async def tempban(
        self,
        ctx: commands.Context,
        membro: discord.Member,
        duracao: str,
        *,
        motivo: str = "Sem motivo informado",
    ):
        """Bane um membro por um período de tempo e depois o desbane automaticamente."""
        seconds = _parse_duration(duracao)
        if seconds is None:
            return await ctx.reply(
                "❌ Duração inválida. Use algo como `10m`, `2h`, `1d`.",
                mention_author=False,
            )

        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply(
                "❌ Não é possível moderar alguém com cargo igual ou superior ao seu.",
                mention_author=False,
            )

        unban_ts = int(discord.utils.utcnow().timestamp()) + seconds
        full_reason = f"Tempban por {ctx.author} | {motivo} | Desbanir em <t:{unban_ts}:f>"

        try:
            await membro.send(
                f"Você foi banido temporariamente de **{ctx.guild.name}** por `{duracao}`.\n"
                f"Motivo: {motivo}\n"
                f"Você poderá retornar em <t:{unban_ts}:R>."
            )
        except Exception:
            pass

        await ctx.guild.ban(membro, reason=full_reason, delete_message_days=0)

        embed = discord.Embed(
            title="🔨 Ban Temporário",
            color=discord.Color.red(),
        )
        embed.add_field(name="Membro", value=str(membro), inline=True)
        embed.add_field(name="Duração", value=duracao, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Desbanir em", value=f"<t:{unban_ts}:R>", inline=False)
        embed.set_footer(text=f"Moderado por {ctx.author.display_name}")
        await ctx.reply(embed=embed, mention_author=False)

        # Store data needed for unban before sleeping
        guild_id = ctx.guild.id
        user_id = membro.id

        await asyncio.sleep(seconds)

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return
        try:
            user = await self.bot.fetch_user(user_id)
            await guild.unban(user, reason=f"Tempban expirado. Banido por {ctx.author}.")
            try:
                channel = ctx.channel
                await channel.send(
                    embed=discord.Embed(
                        title="✅ Ban Temporário Expirado",
                        description=f"**{user}** foi desbanido automaticamente.",
                        color=discord.Color.green(),
                    )
                )
            except Exception:
                pass
        except discord.NotFound:
            pass
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(TempBan(bot))
