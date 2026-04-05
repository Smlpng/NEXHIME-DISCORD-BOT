import re
from datetime import datetime, timezone
import discord
from discord.ext import commands


HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def _clamp(text: str | None, max_len: int) -> str | None:
	if text is None:
		return None
	text = str(text)
	if len(text) <= max_len:
		return text
	# mantém dentro dos limites do Discord
	return text[: max(0, max_len - 1)] + "…"


def _parse_bool(s: str) -> bool | None:
	v = (s or "").strip().lower()
	if v in {"s", "sim", "y", "yes", "1", "true", "t"}:
		return True
	if v in {"n", "nao", "não", "no", "0", "false", "f"}:
		return False
	return None


def _parse_color(raw: str | None) -> discord.Colour | None:
	if raw is None:
		return None
	v = raw.strip().lower()
	if v in {"padrão", "padrao", "default", "skip", "pular", ""}:
		return None
	if v in {"random", "aleatorio", "aleatório"}:
		return discord.Colour.random()
	if HEX_COLOR_RE.fullmatch(v):
		if v.startswith("#"):
			v = v[1:]
		return discord.Colour(int(v, 16))
	# tenta decimal (ex.: 16711680)
	try:
		num = int(v)
		if 0 <= num <= 0xFFFFFF:
			return discord.Colour(num)
	except Exception:
		pass
	return None


class EmbedSend(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	def _is_supported_target(self, channel: object) -> bool:
		return isinstance(channel, (discord.TextChannel, discord.Thread))

	async def _ask(
		self,
		ctx: commands.Context,
		prompt: str,
		*,
		timeout: float = 120.0,
		allow_skip: bool = True,
		allow_cancel: bool = True,
	) -> discord.Message | None:
		tips = []
		if allow_skip:
			tips.append("`pular`")
		if allow_cancel:
			tips.append("`cancelar`")
		suffix = f" (" + " / ".join(tips) + ")" if tips else ""

		await ctx.reply(prompt + suffix, mention_author=False)

		def check(m: discord.Message) -> bool:
			return (
				m.author.id == ctx.author.id
				and m.channel.id == ctx.channel.id
				and (not m.author.bot)
			)

		try:
			msg: discord.Message = await self.bot.wait_for("message", timeout=timeout, check=check)
			content = (msg.content or "").strip().lower()
			if allow_cancel and content in {"cancel", "cancelar", "parar", "stop"}:
				return None
			if allow_skip and content in {"skip", "pular", "passar", "-"}:
				return discord.Object(id=0)  # sentinela: pulou
			return msg
		except TimeoutError:
			return None

	def _message_to_text_or_attachment_url(self, msg: discord.Message) -> str:
		content = (msg.content or "").strip()
		if content:
			return content
		if msg.attachments:
			return str(msg.attachments[0].url)
		return ""

	def _try_parse_channel(self, ctx: commands.Context, raw: str) -> discord.TextChannel | discord.Thread | None:
		v = (raw or "").strip()
		if v.lower() in {"aqui", "here", "atual", "current"}:
			return ctx.channel if self._is_supported_target(ctx.channel) else None
		if ctx.guild is None:
			return None
		# mention <#id>
		m = re.fullmatch(r"<#(\d+)>", v)
		if m:
			channel_id = int(m.group(1))
			channel = ctx.guild.get_channel(channel_id)
			if channel is None:
				channel = ctx.guild.get_thread(channel_id)
			return channel if self._is_supported_target(channel) else None
		# id puro
		if v.isdigit():
			channel_id = int(v)
			channel = ctx.guild.get_channel(channel_id)
			if channel is None:
				channel = ctx.guild.get_thread(channel_id)
			return channel if self._is_supported_target(channel) else None
		# nome
		channel = discord.utils.get(ctx.guild.text_channels, name=v)
		if channel is not None:
			return channel
		thread = discord.utils.get(ctx.guild.threads, name=v)
		return thread if self._is_supported_target(thread) else None

	def _bot_can_send_embed(self, channel: discord.TextChannel | discord.Thread, me: discord.Member | None) -> tuple[bool, str | None]:
		if me is None:
			return False, "Não consegui identificar as permissões do bot no servidor."

		if isinstance(channel, discord.Thread):
			parent = channel.parent
			if parent is None:
				return False, "Não consegui identificar o canal pai da thread destino."
			perms = parent.permissions_for(me)
			if not perms.view_channel:
				return False, "O bot não consegue ver a thread destino."
			if not perms.send_messages_in_threads:
				return False, "O bot não tem permissão de enviar mensagens em threads no destino."
			if not perms.embed_links:
				return False, "O bot não tem permissão de `Embed Links` na thread destino."
			return True, None

		perms = channel.permissions_for(me)
		if not perms.view_channel:
			return False, "O bot não consegue ver o canal destino."
		if not perms.send_messages:
			return False, "O bot não tem permissão de enviar mensagens no canal destino."
		if not perms.embed_links:
			return False, "O bot não tem permissão de `Embed Links` no canal destino."
		return True, None

	@commands.command(
		name="embed",
		help="Cria e envia um embed totalmente customizável via chat (wizard).",
	)
	@commands.has_permissions(manage_messages=True)
	async def embed(self, ctx: commands.Context):
		if ctx.guild is None:
			return await ctx.reply("Este comando só pode ser usado em servidores.")

		await ctx.reply(
			"Vou te fazer algumas perguntas para montar o embed. "
			"Responda no chat. Você pode anexar imagens nas perguntas de URL.",
			mention_author=False,
		)

		# Canal destino
		dest_msg = await self._ask(
			ctx,
			"Em qual canal devo enviar o embed? (mencione #canal, id, nome ou `aqui`)",
			allow_skip=True,
		)
		if dest_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)

		if isinstance(dest_msg, discord.Object) and dest_msg.id == 0:
			dest_channel = ctx.channel
		else:
			raw = self._message_to_text_or_attachment_url(dest_msg)
			dest_channel = self._try_parse_channel(ctx, raw)
			if dest_channel is None:
				return await ctx.reply(
					"Não consegui encontrar o canal informado. Use uma menção, ID, nome exato ou `aqui`.",
					mention_author=False,
				)

		if not self._is_supported_target(dest_channel):
			return await ctx.reply(
				"O destino informado não é suportado. Use um canal de texto ou uma thread.",
				mention_author=False,
			)

		me = ctx.guild.me
		ok, reason = self._bot_can_send_embed(dest_channel, me)
		if not ok:
			return await ctx.reply(reason or "Sem permissões no canal destino.", mention_author=False)

		# Campos básicos
		title_msg = await self._ask(ctx, "Título do embed?")
		if title_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		title = None if isinstance(title_msg, discord.Object) else _clamp(self._message_to_text_or_attachment_url(title_msg), 256)

		desc_msg = await self._ask(ctx, "Descrição do embed? (pode ter múltiplas linhas)")
		if desc_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		description = None if isinstance(desc_msg, discord.Object) else _clamp(self._message_to_text_or_attachment_url(desc_msg), 4096)

		color_msg = await self._ask(ctx, "Cor? (hex `#ff00ff`, decimal `16711680`, `aleatorio` ou `pular`)")
		if color_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		colour = None
		if not (isinstance(color_msg, discord.Object) and color_msg.id == 0):
			colour = _parse_color(self._message_to_text_or_attachment_url(color_msg))

		url_msg = await self._ask(ctx, "URL do título? (link clicável no título)")
		if url_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		url = None if isinstance(url_msg, discord.Object) else self._message_to_text_or_attachment_url(url_msg)
		if url and not (url.startswith("http://") or url.startswith("https://")):
			url = None

		embed = discord.Embed(
			title=title,
			description=description,
			colour=colour,
			url=url,
		)

		# Autor
		author_name_msg = await self._ask(ctx, "Nome do autor do embed? (aparece acima do título)")
		if author_name_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		author_name = None if isinstance(author_name_msg, discord.Object) else _clamp(self._message_to_text_or_attachment_url(author_name_msg), 256)

		author_icon_msg = await self._ask(ctx, "Ícone do autor (URL ou anexo)?")
		if author_icon_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		author_icon_url = None if isinstance(author_icon_msg, discord.Object) else self._message_to_text_or_attachment_url(author_icon_msg)
		if author_icon_url and not (author_icon_url.startswith("http://") or author_icon_url.startswith("https://")):
			author_icon_url = None

		if author_name:
			if author_icon_url:
				embed.set_author(name=author_name, icon_url=author_icon_url)
			else:
				embed.set_author(name=author_name)

		# Thumb / Image
		thumb_msg = await self._ask(ctx, "Thumbnail (URL ou anexo)?")
		if thumb_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		thumbnail_url = None if isinstance(thumb_msg, discord.Object) else self._message_to_text_or_attachment_url(thumb_msg)
		if thumbnail_url and (thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://")):
			embed.set_thumbnail(url=thumbnail_url)

		image_msg = await self._ask(ctx, "Imagem grande (URL ou anexo)?")
		if image_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		image_url = None if isinstance(image_msg, discord.Object) else self._message_to_text_or_attachment_url(image_msg)
		if image_url and (image_url.startswith("http://") or image_url.startswith("https://")):
			embed.set_image(url=image_url)

		# Footer
		footer_text_msg = await self._ask(ctx, "Texto do rodapé (footer)?")
		if footer_text_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		footer_text = None if isinstance(footer_text_msg, discord.Object) else _clamp(self._message_to_text_or_attachment_url(footer_text_msg), 2048)

		footer_icon_msg = await self._ask(ctx, "Ícone do rodapé (URL ou anexo)?")
		if footer_icon_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		footer_icon_url = None if isinstance(footer_icon_msg, discord.Object) else self._message_to_text_or_attachment_url(footer_icon_msg)
		if footer_icon_url and not (footer_icon_url.startswith("http://") or footer_icon_url.startswith("https://")):
			footer_icon_url = None

		if footer_text:
			if footer_icon_url:
				embed.set_footer(text=footer_text, icon_url=footer_icon_url)
			else:
				embed.set_footer(text=footer_text)

		# Timestamp
		ts_msg = await self._ask(ctx, "Adicionar timestamp (data/hora atual)? (sim/não)", allow_skip=False)
		if ts_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		ts_bool = _parse_bool(self._message_to_text_or_attachment_url(ts_msg))
		if ts_bool is True:
			embed.timestamp = datetime.now(timezone.utc)

		# Campos (fields)
		while len(embed.fields) < 25:
			add_field_msg = await self._ask(ctx, "Adicionar um campo? (sim/não)", allow_skip=False)
			if add_field_msg is None:
				return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
			add_field = _parse_bool(self._message_to_text_or_attachment_url(add_field_msg))
			if add_field is None:
				await ctx.reply("Responda `sim` ou `não`.", mention_author=False)
				continue
			if not add_field:
				break

			field_name_msg = await self._ask(ctx, "Nome do campo?")
			if field_name_msg is None:
				return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
			if isinstance(field_name_msg, discord.Object):
				await ctx.reply("Nome do campo não pode ser pulado.", mention_author=False)
				continue
			field_name = _clamp(self._message_to_text_or_attachment_url(field_name_msg), 256) or "—"

			field_value_msg = await self._ask(ctx, "Valor do campo? (pode ter múltiplas linhas)")
			if field_value_msg is None:
				return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
			if isinstance(field_value_msg, discord.Object):
				await ctx.reply("Valor do campo não pode ser pulado.", mention_author=False)
				continue
			field_value = _clamp(self._message_to_text_or_attachment_url(field_value_msg), 1024) or "—"

			inline_msg = await self._ask(ctx, "Campo inline? (sim/não)", allow_skip=False)
			if inline_msg is None:
				return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
			inline_bool = _parse_bool(self._message_to_text_or_attachment_url(inline_msg))
			if inline_bool is None:
				inline_bool = False

			embed.add_field(name=field_name, value=field_value, inline=inline_bool)

		# Preview + confirmação
		await ctx.reply("Preview do embed (ainda não foi enviado):", embed=embed, mention_author=False)
		confirm_msg = await self._ask(ctx, "Enviar agora? (sim/não)", allow_skip=False)
		if confirm_msg is None:
			return await ctx.reply("Cancelado (timeout/cancelar).", mention_author=False)
		confirm = _parse_bool(self._message_to_text_or_attachment_url(confirm_msg))
		if confirm is not True:
			return await ctx.reply("Ok, não enviei.", mention_author=False)

		try:
			await dest_channel.send(embed=embed)
		except discord.Forbidden:
			return await ctx.reply(
				f"Não consegui enviar o embed em {dest_channel.mention}: falta alguma permissão no canal destino.",
				mention_author=False,
			)
		except discord.HTTPException as e:
			return await ctx.reply(f"Falha ao enviar embed em {dest_channel.mention}: {e}", mention_author=False)

		await ctx.reply(f"Embed enviado em {dest_channel.mention}.", mention_author=False)


async def setup(bot: commands.Bot):
	await bot.add_cog(EmbedSend(bot))

