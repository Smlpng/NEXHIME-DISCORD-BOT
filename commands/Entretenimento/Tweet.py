import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
import textwrap
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "DataBase"
TWEET_REDIRECT_FILE = DB_DIR / "tweet_channels.json"
BACKGROUND = BASE_DIR / "assets" / "templates" / "tweet" / "tweet_bg.png"
MAIN_GUILD_ID = 1454442259536678972
TWEET_CHANNEL_ID = 1488553040553185310


def load_tweet_redirects() -> dict[str, dict]:
    try:
        with TWEET_REDIRECT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    redirects: dict[str, dict] = {}
    for guild_id, payload in data.items():
        guild_key = str(guild_id)
        if isinstance(payload, int):
            redirects[guild_key] = {"channel_id": int(payload), "external": "none"}
            continue
        if isinstance(payload, str) and payload.isdigit():
            redirects[guild_key] = {"channel_id": int(payload), "external": "none"}
            continue
        if isinstance(payload, dict):
            raw_channel_id = payload.get("channel_id", payload.get("id"))
            try:
                channel_id = int(raw_channel_id)
            except (TypeError, ValueError):
                continue
            external = str(payload.get("external", payload.get("mode", "none")) or "none").lower()
            if external not in {"none", "main", "all"}:
                external = "none"
            redirects[guild_key] = {"channel_id": channel_id, "external": external}
            continue

    return redirects


def save_tweet_redirects(data: dict[str, dict]) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with TWEET_REDIRECT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


class Tweet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_redirect_channels = load_tweet_redirects()

    async def _safe_send_file(
        self,
        channel: discord.abc.Messageable | None,
        image_bytes: bytes,
        *,
        filename: str = "tweet.png",
        content: str | None = None,
    ) -> bool:
        if channel is None or not hasattr(channel, "send"):
            return False
        try:
            kwargs = {"file": discord.File(BytesIO(image_bytes), filename=filename)}
            if content:
                kwargs["content"] = content
            await channel.send(**kwargs)
            return True
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            return False

    async def _get_avatar_image(self, user: discord.abc.User) -> Image.Image | None:
        """Retorna avatar do usuário como PIL Image (RGBA) ou None."""
        try:
            avatar_bytes = await user.display_avatar.read()
            return Image.open(BytesIO(avatar_bytes)).convert("RGBA")
        except Exception:
            pass

        # Fallback para ambientes onde Asset.read() falhe
        try:
            avatar_url = user.display_avatar.url
            response = requests.get(avatar_url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception:
            return None

    @staticmethod
    def _sanitize_channel_name(name: str) -> str:
        name = (name or "").strip().lower()
        if not name:
            return "tweet-redirecionamento"

        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
        name = name.replace(" ", "-")
        cleaned = []
        last_dash = False
        for ch in name:
            if ch in allowed:
                if ch == "-":
                    if last_dash:
                        continue
                    last_dash = True
                else:
                    last_dash = False
                cleaned.append(ch)
            elif ch in {"/", "\\", ".", ",", ":", ";", "|", "'", '"', "`"}:
                continue
            else:
                # substitui caracteres não suportados por hífen para manter legível
                if not last_dash:
                    cleaned.append("-")
                    last_dash = True

        final = "".join(cleaned).strip("-")
        if not final:
            final = "tweet-redirecionamento"
        return final[:90]

    async def get_target_channel(self) -> discord.abc.Messageable | None:
        channel = self.bot.get_channel(TWEET_CHANNEL_ID)
        if channel is not None:
            return channel

        try:
            fetched_channel = await self.bot.fetch_channel(TWEET_CHANNEL_ID)
        except discord.HTTPException:
            return None

        return fetched_channel if hasattr(fetched_channel, "send") else None

    async def get_guild_redirect_channel(self, guild_id: int) -> discord.abc.Messageable | None:
        payload = self.guild_redirect_channels.get(str(guild_id))
        if not isinstance(payload, dict):
            return None

        channel_id = payload.get("channel_id")
        if channel_id is None:
            return None
        try:
            channel_id = int(channel_id)
        except (TypeError, ValueError):
            return None

        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            return channel

        try:
            fetched_channel = await self.bot.fetch_channel(channel_id)
        except discord.HTTPException:
            return None

        return fetched_channel if hasattr(fetched_channel, "send") else None

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name="tweet_redirect", help="Define o canal para onde o tweet também será enviado neste servidor")
    async def tweet_redirect(self, ctx, canal: discord.TextChannel):
        guild_key = str(ctx.guild.id)
        current = self.guild_redirect_channels.get(guild_key)
        external = "none"
        if isinstance(current, dict):
            external = str(current.get("external", "none") or "none").lower()
            if external not in {"none", "main", "all"}:
                external = "none"
        self.guild_redirect_channels[guild_key] = {"channel_id": canal.id, "external": external}
        save_tweet_redirects(self.guild_redirect_channels)
        await ctx.send(f"Canal de redirecionamento do tweet definido para {canal.mention}.")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(
        name="configurar_tweet",
        aliases=["setup_tweet"],
        help="Cria um canal de redirecionamento para o tweet e salva o ID no banco.",
    )
    async def configurar_tweet(self, ctx: commands.Context):
        if ctx.guild is None:
            return await ctx.send("Esse comando só pode ser usado dentro de um servidor.")

        current_payload = self.guild_redirect_channels.get(str(ctx.guild.id))
        current_channel = None
        if isinstance(current_payload, dict) and current_payload.get("channel_id"):
            try:
                current_channel = ctx.guild.get_channel(int(current_payload["channel_id"]))
            except (TypeError, ValueError):
                current_channel = None

        embed = discord.Embed(
            title="Configurar redirecionamento de Tweet",
            description=(
                "Vou criar um chat específico neste servidor para o redirecionamento dos tweets.\n\n"
                "Depois disso, o bot vai **guardar o ID** do chat criado no banco, então o redirecionamento vai continuar funcionando "
                "mesmo após reiniciar."
            ),
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Nome do canal",
            value=(
                "Se você quiser, responda **agora** com o nome do canal (ex: `tweet-redirecionamento`).\n"
                "Se não quiser, responda `padrao` (ou `padrão`) para usar o nome padrão.\n"
                "Tempo: 30 segundos."
            ),
            inline=False,
        )
        if current_channel is not None:
            embed.add_field(
                name="Já configurado",
                value=f"Canal atual: {current_channel.mention}\nSe continuar, vou criar um novo canal e substituir a configuração.",
                inline=False,
            )

        await ctx.send(embed=embed)

        def check(message: discord.Message) -> bool:
            return (
                message.author.id == ctx.author.id
                and message.channel.id == ctx.channel.id
                and message.guild is not None
                and message.guild.id == ctx.guild.id
            )

        channel_name = "tweet-redirecionamento"
        try:
            reply: discord.Message = await self.bot.wait_for("message", check=check, timeout=30)
            raw = (reply.content or "").strip()
            if raw and raw.lower() not in {"padrao", "padrão", "nao", "não"}:
                channel_name = raw
        except Exception:
            pass

        external_mode = "none"
        embed2 = discord.Embed(
            title="Redirecionamento externo",
            description=(
                "Agora escolha se este servidor também vai receber tweets criados em **outros servidores**.\n\n"
                "Responda com `1`, `2` ou `3`:\n"
                "`1` = Outros servidores (todos)\n"
                "`2` = Só do servidor principal\n"
                "`3` = Nenhum (somente deste servidor)"
            ),
            color=discord.Color.blurple(),
        )
        embed2.set_footer(text="Tempo: 30 segundos")
        await ctx.send(embed=embed2)

        try:
            reply2: discord.Message = await self.bot.wait_for("message", check=check, timeout=30)
            raw2 = (reply2.content or "").strip().lower()
            if raw2 in {"1", "todos", "all", "outros", "global"}:
                external_mode = "all"
            elif raw2 in {"2", "principal", "main"}:
                external_mode = "main"
            elif raw2 in {"3", "nenhum", "none", "nao", "não"}:
                external_mode = "none"
        except Exception:
            pass

        channel_name = self._sanitize_channel_name(channel_name)

        try:
            created = await ctx.guild.create_text_channel(
                name=channel_name,
                reason=f"Configuração de tweet por {ctx.author} ({ctx.author.id})",
                category=getattr(ctx.channel, "category", None),
            )
        except discord.Forbidden:
            return await ctx.send("Não tenho permissão para criar canais neste servidor.")
        except discord.HTTPException:
            return await ctx.send("Falhei ao criar o canal (erro do Discord). Tente novamente.")

        self.guild_redirect_channels[str(ctx.guild.id)] = {"channel_id": created.id, "external": external_mode}
        save_tweet_redirects(self.guild_redirect_channels)
        mode_label = {"none": "Nenhum", "main": "Só do principal", "all": "Outros servidores (todos)"}.get(external_mode, "Nenhum")
        await ctx.send(
            f"Canal de redirecionamento configurado: {created.mention} (ID salvo). "
            f"Redirecionamento externo: **{mode_label}**."
        )

    @commands.command(help="Cria um tweet falso")
    async def tweet(self, ctx, *, texto: str):
        # Context (prefix commands) não tem defer; mantenha compatibilidade com possíveis interações.
        if getattr(ctx, "interaction", None):
            try:
                await ctx.interaction.response.defer(thinking=True)
            except Exception:
                pass

        target_channel = await self.get_target_channel()
        if target_channel is None:
            await ctx.send(
                "Aviso: não consegui acessar o canal global configurado para tweet (TWEET_CHANNEL_ID). "
                "Vou enviar o tweet apenas aqui e nos redirecionamentos configurados."
            )

        # carregar fundo
        try:
            img = Image.open(BACKGROUND).convert("RGBA")
        except Exception:
            await ctx.send(
                "Não consegui abrir o template do tweet. Verifique o arquivo em assets/templates/tweet/tweet_bg.png."
            )
            return
        draw = ImageDraw.Draw(img)

        width, height = img.size

        # baixar avatar (resiliente)
        avatar = await self._get_avatar_image(ctx.author)
        if avatar is not None:
            avatar = avatar.resize((60, 60))

            mask = Image.new("L", (60, 60), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 60, 60), fill=255)

            img.paste(avatar, (34, 24), mask)

        # fontes
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 20)
            font_user = ImageFont.truetype("arial.ttf", 18)
            font_text = ImageFont.truetype("arial.ttf", 20)
            font_stats = ImageFont.truetype("arial.ttf", 20)
        except:
            font_name = ImageFont.load_default()
            font_user = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_stats = ImageFont.load_default()

        # nome
        draw.text((107, 37), ctx.author.display_name, font=font_name, fill=(255, 255, 255))

        # username
        draw.text((107, 57), f"@{ctx.author.name}", font=font_user, fill=(140, 140, 140))

        # texto do tweet
        lines = textwrap.wrap(texto, width=42)

        y = 106
        for line in lines:
            draw.text((40, y), line, font=font_text, fill=(255, 255, 255))
            y += 45

        # -------------------------
        # gerar estatísticas
        # -------------------------

        members = ctx.guild.member_count if ctx.guild else 100

        comentarios = random.randint(0, int(members * 0.1))
        reposts = random.randint(0, int(members * 0.2))
        likes = random.randint(0, int(members * 0.6))

        # posição dos números (ajuste conforme seu template)
        stats_y = 245

        draw.text((66, stats_y), str(comentarios), font=font_stats, fill=(120, 120, 120))
        draw.text((140, stats_y), str(reposts), font=font_stats, fill=(120, 120, 120))
        draw.text((216, stats_y), str(likes), font=font_stats, fill=(120, 120, 120))

        # salvar
        buffer = BytesIO()
        img.save(buffer, "PNG")
        buffer.seek(0)

        image_bytes = buffer.getvalue()

        def origin_line_for(destination: discord.abc.Messageable | None) -> str | None:
            """Retorna uma linha curta com a origem do tweet para anexar na mensagem.

            Observação: menções de canal só funcionam dentro do mesmo servidor.
            """
            if ctx.guild is None:
                return None

            channel_id = getattr(ctx.channel, "id", None)
            if channel_id:
                # Mostra sempre no formato <#ID> como solicitado.
                # Observação: fora do servidor de origem, a menção não vira link clicável,
                # mas ainda preserva o ID do canal.
                channel_label = f"<#{channel_id}>"
            else:
                channel_label = f"#{getattr(ctx.channel, 'name', 'canal')}"

            guild_name = getattr(ctx.guild, "name", "Servidor")
            return f"Postado em: <#{channel_id}>"

        send_direct_to_target = bool(
            target_channel is not None
            and ctx.guild
            and ctx.guild.id == MAIN_GUILD_ID
            and getattr(ctx.channel, "id", None) != getattr(target_channel, "id", None)
        )

        if not send_direct_to_target:
            await self._safe_send_file(ctx.channel, image_bytes)

        if target_channel is not None:
            if getattr(target_channel, "id", None) == getattr(ctx.channel, "id", None) and not send_direct_to_target:
                pass
            else:
                await self._safe_send_file(target_channel, image_bytes, content=origin_line_for(target_channel))

        if ctx.guild is None:
            return

        origin_guild_id = ctx.guild.id

        async def send_to_channel_id(channel_id: int):
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except discord.HTTPException:
                    return
            if channel is None or not hasattr(channel, "send"):
                return
            await self._safe_send_file(channel, image_bytes, content=origin_line_for(channel))

        ctx_channel_id = getattr(ctx.channel, "id", None)
        target_channel_id = getattr(target_channel, "id", None) if target_channel is not None else None

        # 1) Redirecionamento do próprio servidor (sempre, se configurado)
        origin_payload = self.guild_redirect_channels.get(str(origin_guild_id))
        if isinstance(origin_payload, dict) and origin_payload.get("channel_id"):
            try:
                local_redirect_id = int(origin_payload["channel_id"])
            except (TypeError, ValueError):
                local_redirect_id = None

            if local_redirect_id and local_redirect_id not in {ctx_channel_id, target_channel_id}:
                await send_to_channel_id(local_redirect_id)

        # 2) Redirecionamento externo: outros servidores que optaram por receber
        for guild_key, payload in self.guild_redirect_channels.items():
            try:
                dest_guild_id = int(guild_key)
            except (TypeError, ValueError):
                continue
            if dest_guild_id == origin_guild_id:
                continue
            if not isinstance(payload, dict):
                continue

            external_mode = str(payload.get("external", "none") or "none").lower()
            if external_mode == "none":
                continue
            if external_mode == "main" and origin_guild_id != MAIN_GUILD_ID:
                continue

            channel_id = payload.get("channel_id")
            try:
                channel_id = int(channel_id)
            except (TypeError, ValueError):
                continue

            if channel_id in {ctx_channel_id, target_channel_id}:
                continue
            await send_to_channel_id(channel_id)


async def setup(bot):
    await bot.add_cog(Tweet(bot))