import discord
from discord.ext import commands

ID_GUILD = 1454442259536678972


class Invite(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	async def _send_feedback(self, ctx: commands.Context, message: str):
		if ctx.interaction:
			if ctx.interaction.response.is_done():
				await ctx.followup.send(message, ephemeral=True)
			else:
				await ctx.interaction.response.send_message(message, ephemeral=True)
			return

		await ctx.reply(message, mention_author=False)

	def _get_invite_channel(self, guild: discord.Guild) -> discord.abc.GuildChannel | None:
		preferred_channels = [guild.system_channel, guild.rules_channel, guild.public_updates_channel]

		for channel in preferred_channels:
			if channel is None:
				continue

			permissions = channel.permissions_for(guild.me)
			if permissions.view_channel and permissions.create_instant_invite:
				return channel

		for channel in guild.text_channels:
			permissions = channel.permissions_for(guild.me)
			if permissions.view_channel and permissions.create_instant_invite:
				return channel

		return None

	@commands.hybrid_command(name="invite", aliases=["convite", "inv"], description="Envia no seu privado o convite deste servidor.")
	async def invite(self, ctx: commands.Context):
		if not ID_GUILD:
			await self._send_feedback(ctx, "❌ Configure o `ID_GUILD` no início do arquivo antes de usar este comando.")
			return

		guild = self.bot.get_guild(ID_GUILD)
		if guild is None:
			await self._send_feedback(ctx, "❌ Não encontrei o servidor configurado no `ID_GUILD`.")
			return

		invite_channel = self._get_invite_channel(guild)
		if invite_channel is None:
			await self._send_feedback(ctx, "❌ Não encontrei um canal em que eu possa criar convites no servidor configurado.")
			return

		try:
			invite = await invite_channel.create_invite(
				max_age=3600,
				max_uses=0,
				unique=True,
				reason=f"Convite solicitado por {ctx.author}"
			)
		except discord.Forbidden:
			await self._send_feedback(ctx, "❌ Eu não tenho permissão para criar convites no servidor configurado.")
			return
		except discord.HTTPException:
			await self._send_feedback(ctx, "❌ Não consegui gerar o convite agora. Tente novamente em instantes.")
			return

		embed = discord.Embed(
			title="Convite do servidor",
			description=f"Aqui está o convite para **{guild.name}**:\n{invite.url}\n\n⏳ Este convite expira em 1 hora.",
			color=discord.Color.green()
		)

		try:
			await ctx.author.send(embed=embed)
		except discord.Forbidden:
			await self._send_feedback(ctx, "❌ Não consegui te enviar DM. Verifique se suas mensagens privadas estão ativadas.")
			return

		await self._send_feedback(ctx, "✅ Te enviei o convite na DM.")


async def setup(bot: commands.Bot):
	await bot.add_cog(Invite(bot))
