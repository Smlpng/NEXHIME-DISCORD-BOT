import discord
from discord.ext import commands

# IDs para limitar a ação ao servidor correto
GUILD_ID = 1454442259536678972  # ID do seu servidor
WELCOME_CHANNEL_ID = 1454463760185163910  # Coloque o ID do canal de texto aqui
WELCOME_ROLE_ID = 0  # Coloque o ID do cargo para marcar junto da mensagem
OWNER_IDS = [
				773954862223851560,
				1411896473632641077
			]
  # Coloque seu ID de usuário aqui

class WelcomeNovo(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def build_welcome_content(self, member: discord.Member) -> str:
		mentions = [member.mention]
		role = member.guild.get_role(WELCOME_ROLE_ID)
		if role is not None:
			mentions.append(role.mention)
		return " ".join(mentions)

	def build_welcome_embed(self, member: discord.Member) -> discord.Embed:
		embed = discord.Embed(
			title="🐒🌿 Bem-vindo ao nosso servidor! 🌿",
			description=(
				"E aí, macaco! 🐵 Aqui é o seu novo cantinho na selva digital 🌴\n"
				"Divirta-se, faça amizades e explore tudo com a gente!\n\n"
				"🍌 Pegue sua banana, relaxe e aproveite o servidor,\n"
				"mas antes veja as <#1454463743466668092> e <#1456859390706716867>\n"
				"E esteja pronto pra se divertir!"
			),
			color=discord.Color.green(),
		)
		embed.set_thumbnail(url=member.display_avatar.url)
		embed.set_footer(text=f"Novo membro: {member.display_name}")
		return embed

	@commands.Cog.listener()
	async def on_member_join(self, member):
		# Verifica se o membro entrou no servidor correto
		if member.guild.id != GUILD_ID:
			return
		# Envia mensagem de boas-vindas no canal
		channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
		if channel:
			await channel.send(
				content=self.build_welcome_content(member),
				embed=self.build_welcome_embed(member),
			)
		# Envia DM para o dono
		for owner_id in OWNER_IDS:
			owner = self.bot.get_user(owner_id)
			if owner:
				await owner.send(f"Novo membro entrou: {member} ({member.mention})")

	@commands.command(
		name="testar_boas_vindas",
		help="Testa a mensagem de boas-vindas no canal atual.",
	)
	@commands.has_permissions(manage_guild=True)
	async def testar_boas_vindas(self, ctx: commands.Context, membro: discord.Member | None = None):
		if ctx.guild is None:
			return await ctx.reply("Este comando só pode ser usado em servidores.")

		if ctx.guild.id != GUILD_ID:
			return await ctx.reply("Este comando só está disponível no servidor configurado.")

		target = membro or ctx.author
		await ctx.send(
			content=self.build_welcome_content(target),
			embed=self.build_welcome_embed(target),
		)
		await ctx.reply("Mensagem de boas-vindas enviada para teste.", mention_author=False)

async def setup(bot):
	await bot.add_cog(WelcomeNovo(bot))
