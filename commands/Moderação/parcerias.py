import re

from discord.ext import commands


RULES = [
	{
		"channel_id": "1481067975456067674",
		"keywords": ["parceria", "parcerias", "Parceria", "Parcerias"],
		"response": "📌 <@&1484553936970059897>, novo pedido de parceria, verifique se o usuario tem os requisitos.",
	},
]


class Parcerias(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.rules = self._normalize_rules(RULES)

	def _normalize_rules(self, raw_rules: list[dict]) -> list[dict]:
		normalized_rules = []

		for rule in raw_rules:
			if not isinstance(rule, dict):
				continue

			channel_id = rule.get("channel_id")
			keywords = rule.get("keywords", rule.get("keyword"))
			response = rule.get("response")

			if isinstance(keywords, str):
				keywords = [keywords]

			if not channel_id or not keywords or not response:
				continue

			normalized_keywords = []

			for keyword in keywords:
				if not keyword:
					continue

				normalized_keywords.append(str(keyword).strip().lower())

			if not normalized_keywords:
				continue

			normalized_rules.append(
				{
					"channel_id": str(channel_id),
					"keywords": normalized_keywords,
					"response": str(response),
				}
			)

		return normalized_rules

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot or not message.guild:
			return

		content = message.content.lower()
		channel_id = str(message.channel.id)

		for rule in self.rules:
			if rule["channel_id"] != channel_id:
				continue

			for keyword in rule["keywords"]:
				pattern = rf"\b{re.escape(keyword)}\b"

				if re.search(pattern, content):
					await message.reply(rule["response"], mention_author=False)
					return


async def setup(bot: commands.Bot):
	await bot.add_cog(Parcerias(bot))
