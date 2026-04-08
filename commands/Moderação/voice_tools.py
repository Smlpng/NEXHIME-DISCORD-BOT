import discord
from discord.ext import commands


class VoiceTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _hierarchy_ok(ctx: commands.Context, target: discord.Member) -> bool:
        if target == ctx.author or target.bot or target == ctx.guild.owner:
            return False
        return ctx.author.top_role > target.top_role and ctx.guild.me.top_role > target.top_role

    @commands.command(name="voicekick", aliases=["vkick"], help="Remove um membro do canal de voz atual.")
    @commands.has_permissions(move_members=True)
    async def voicekick(self, ctx: commands.Context, membro: discord.Member, *, motivo: str | None = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Nao e possivel moderar este membro na call.")
        if membro.voice is None or membro.voice.channel is None:
            return await ctx.reply("Esse membro nao esta em um canal de voz.")
        try:
            await membro.move_to(None, reason=motivo or f"Voice kick por {ctx.author}")
        except discord.Forbidden:
            return await ctx.reply("Faltam permissoes para remover este membro da call.")
        except discord.HTTPException as exc:
            return await ctx.reply(f"Nao foi possivel remover da call: {exc}")
        await ctx.reply(f"{membro.mention} foi removido do canal de voz.")

    @commands.command(name="voicemute", aliases=["vmute"], help="Silencia um membro no canal de voz.")
    @commands.has_permissions(mute_members=True)
    async def voicemute(self, ctx: commands.Context, membro: discord.Member, *, motivo: str | None = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Nao e possivel moderar este membro na call.")
        if membro.voice is None or membro.voice.channel is None:
            return await ctx.reply("Esse membro nao esta em um canal de voz.")
        try:
            await membro.edit(mute=True, reason=motivo or f"Voice mute por {ctx.author}")
        except discord.Forbidden:
            return await ctx.reply("Faltam permissoes para silenciar este membro.")
        except discord.HTTPException as exc:
            return await ctx.reply(f"Nao foi possivel silenciar na call: {exc}")
        await ctx.reply(f"{membro.mention} foi silenciado no canal de voz.")

    @commands.command(name="voiceunmute", aliases=["vunmute"], help="Remove o silencio de voz de um membro.")
    @commands.has_permissions(mute_members=True)
    async def voiceunmute(self, ctx: commands.Context, membro: discord.Member, *, motivo: str | None = None):
        if not self._hierarchy_ok(ctx, membro):
            return await ctx.reply("Nao e possivel moderar este membro na call.")
        try:
            await membro.edit(mute=False, reason=motivo or f"Voice unmute por {ctx.author}")
        except discord.Forbidden:
            return await ctx.reply("Faltam permissoes para remover o silencio deste membro.")
        except discord.HTTPException as exc:
            return await ctx.reply(f"Nao foi possivel remover o silencio na call: {exc}")
        await ctx.reply(f"{membro.mention} nao esta mais silenciado no canal de voz.")


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceTools(bot))