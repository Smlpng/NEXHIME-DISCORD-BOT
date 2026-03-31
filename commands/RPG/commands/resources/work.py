import random
import time

from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import get_active_hero, update_active_hero_resources
from commands.RPG.utils.hero_check import economy_profile_created


class Work(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.work_cooldowns: dict[int, float] = {}
		self.slut_cooldowns: dict[int, float] = {}

	@staticmethod
	def _format_cooldown(seconds_left: int) -> str:
		minutes, seconds = divmod(max(seconds_left, 0), 60)
		if minutes and seconds:
			return f"{minutes}m {seconds}s"
		if minutes:
			return f"{minutes}m"
		return f"{seconds}s"

	async def _run_job_command(
		self,
		ctx,
		*,
		cooldowns: dict[int, float],
		cooldown_seconds: int,
		min_nex: int,
		max_nex: int,
		outcomes: list[str],
	):
		inte = CommandContextAdapter(ctx)
		await economy_profile_created(inte)

		hero = get_active_hero(inte.user.id)
		if hero is None:
			return await inte.response.send_message(
				"Seu perfil economico foi criado, mas voce ainda precisa ter um heroi para ganhar nex."
			)

		now = time.time()
		available_at = cooldowns.get(inte.user.id, 0)
		if available_at > now:
			remaining = self._format_cooldown(int(available_at - now))
			return await inte.response.send_message(
				f"Voce precisa esperar {remaining} para usar esse comando novamente.",
				ephemeral=True,
			)

		earned_nex = random.randint(min_nex, max_nex)
		update_active_hero_resources(inte.user.id, nex=earned_nex)
		cooldowns[inte.user.id] = now + cooldown_seconds

		message = random.choice(outcomes).format(user=inte.user.mention, nex=earned_nex)
		await inte.response.send_message(message)

	@commands.command(name="trabalhar", aliases=["work"])
	async def trabalhar(self, ctx):
		"""Trabalha para ganhar um pouco de nex."""
		outcomes = [
			"{user} passou o dia carregando caixas no mercado e recebeu {nex} nex.",
			"{user} ajudou a reforcar uma ponte do vilarejo e ganhou {nex} nex.",
			"{user} fez um bico escoltando mercadores e voltou com {nex} nex.",
			"{user} cortou lenha para a taverna e embolsou {nex} nex.",
		]
		await self._run_job_command(
			ctx,
			cooldowns=self.work_cooldowns,
			cooldown_seconds=300,
			min_nex=45,
			max_nex=110,
			outcomes=outcomes,
		)

	@commands.command(name="glubglub", aliases=["slut"])
	async def slut(self, ctx):
		"""Usa carisma e ousadia para conseguir nex rapido."""
		outcomes = [
			"{user} saiu distribuindo charme pela cidade e conseguiu {nex} nex em gorjetas.",
			"{user} entrou no salao mais caro do reino, fez contatos e voltou com {nex} nex.",
			"{user} apostou no carisma, roubou a cena na festa e faturou {nex} nex.",
			"{user} improvisou um numero provocante na taverna e ganhou {nex} nex.",
		]
		await self._run_job_command(
			ctx,
			cooldowns=self.slut_cooldowns,
			cooldown_seconds=480,
			min_nex=90,
			max_nex=180,
			outcomes=outcomes,
		)


async def setup(bot):
	await bot.add_cog(Work(bot))
