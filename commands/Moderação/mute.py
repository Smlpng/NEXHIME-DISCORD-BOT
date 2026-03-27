import datetime
import discord
from discord.ext import commands

TIMEOUT_DEFAULT_MIN = 10  # minutos
MUTED_ROLE_NAME = "Muted"  # usado como fallback se timeout falhar

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _hierarchy_ok(self, ctx: commands.Context, target: discord.Member) -> bool:
        return ctx.author.top_role > target.top_role and ctx.guild.me.top_role > target.top_role

    @commands.hybrid_command(name="silenciar", aliases=["mute"], description="Silencia um membro (timeout).")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, membro: discord.Member, minutos: int = TIMEOUT_DEFAULT_MIN, *, motivo: str = None):
        if membro == ctx.author:
            return await ctx.reply("Não é possível silenciar a si mesmo.")
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não é possível moderar alguém com cargo igual/superior.")
        try:
            until = datetime.timedelta(minutes=max(1, minutos))
            await membro.timeout(until, reason=motivo or f"Por {ctx.author}")
            await ctx.reply(f"{membro.mention} silenciado por {minutos} min.")
        except Exception:
            role = discord.utils.get(ctx.guild.roles, name=MUTED_ROLE_NAME)
            if not role:
                role = await ctx.guild.create_role(name=MUTED_ROLE_NAME, reason="Cargo de mute")
                for ch in ctx.guild.channels:
                    try:
                        await ch.set_permissions(role, send_messages=False, add_reactions=False, speak=False)
                    except Exception:
                        pass
            await membro.add_roles(role, reason=motivo or f"Por {ctx.author}")
            await ctx.reply(f"{membro.mention} recebeu cargo {role.name} (fallback).")

    @commands.hybrid_command(name="dessilenciar", aliases=["unmute"], description="Remove o silêncio de um membro.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, membro: discord.Member, *, motivo: str = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Não é possível moderar alguém com cargo igual/superior.")
        try:
            await membro.timeout(None, reason=motivo or f"Por {ctx.author}")
            await ctx.reply(f"{membro.mention} não está mais silenciado.")
        except Exception:
            role = discord.utils.get(ctx.guild.roles, name=MUTED_ROLE_NAME)
            if role and role in membro.roles:
                await membro.remove_roles(role, reason=motivo or f"Por {ctx.author}")
            await ctx.reply(f"{membro.mention} teve o silêncio removido.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))
