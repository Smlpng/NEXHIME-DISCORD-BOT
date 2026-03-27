import re
import io
import aiohttp
import discord
from discord.ext import commands

MAX_BYTES = 256 * 1024
NAME_RE = re.compile(r"^[a-z0-9_]{2,32}$", re.IGNORECASE)
CUSTOM_RE = re.compile(r"^<a?:\w+:(\d+)>$")
ALLOWED_MIME = ("image/png", "image/jpeg", "image/gif")
WEBP_MIME = "image/webp"


def try_convert_to_png(data: bytes, mime: str) -> tuple[bytes, str] | None:
    try:
        from PIL import Image  # Pillow
    except Exception:
        return None
    try:
        im = Image.open(io.BytesIO(data))
        # reduzir para 128x128 mantendo proporção
        im.thumbnail((128, 128))
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        out = buf.getvalue()
        return out, "image/png"
    except Exception:
        return None


def detect_mime(data: bytes, fallback: str = "") -> str:
    """
    Detecta o mime a partir do fallback (content-type) ou pelo cabeçalho da imagem via Pillow.
    """
    mime = (fallback or "").lower().split(";", 1)[0].strip()
    if mime in ("", "application/octet-stream"):
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(data))
            fmt = im.format.lower()
            if fmt == "png":
                return "image/png"
            elif fmt in ("jpeg", "jpg"):
                return "image/jpeg"
            elif fmt == "gif":
                return "image/gif"
        except Exception:
            pass
    return mime


class EmojiManage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _fetch_bytes(self, url: str) -> tuple[bytes, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20, allow_redirects=True) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"http {resp.status}")
                ctype = (resp.headers.get("Content-Type") or "").lower().split(";", 1)[0].strip()
                data = await resp.read()
                mime = detect_mime(data, ctype)
                return data, mime

    def _is_valid_name(self, name: str) -> bool:
        return bool(NAME_RE.fullmatch(name))

    def _bot_can_manage_emojis(self, guild: discord.Guild) -> bool:
        me = guild.me
        if not me:
            return False
        perms = me.guild_permissions
        print("[PERMS BOT]", guild.name, {
            "administrator": perms.administrator,
            "manage_emojis_and_stickers": perms.manage_emojis_and_stickers,
        })
        return perms.manage_emojis_and_stickers or perms.administrator

    def _mime_supported(self, mime: str) -> bool:
        if not mime:
            return False
        mime = mime.lower()
        return (
            mime.startswith("image/png")
            or mime.startswith("image/jpeg")
            or mime.startswith("image/jpg")
            or mime.startswith("image/gif")
        )

    @commands.hybrid_command(
        name="emojiadd",
        description="Cria um emoji a partir de URL, anexo ou emoji customizado existente."
    )
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def emojiadd(self, ctx: commands.Context, nome: str, origem: str | None = None):
        if not ctx.guild:
            return await ctx.reply("Este comando só pode ser usado em servidores.")
        if not self._bot_can_manage_emojis(ctx.guild):
            return await ctx.reply("O bot não possui permissão efetiva de 'Manage Emojis and Stickers' (ou Administrator) neste servidor.")
        if not self._is_valid_name(nome):
            return await ctx.reply("Nome inválido. Use 2–32 caracteres: letras, números e _. Ex.: 'smile_pro'.")

        image: bytes | None = None
        mime: str = ""

        # 1) Clonar de emoji customizado
        if origem and origem.startswith("<") and origem.endswith(">"):
            m = CUSTOM_RE.match(origem)
            if not m:
                return await ctx.reply("Formato de emoji customizado inválido. Use <:nome:id> ou <a:nome:id>.")
            emoji_id = int(m.group(1))
            try:
                e = discord.utils.get(ctx.guild.emojis, id=emoji_id) or await self.bot.fetch_emoji(emoji_id)
                async with aiohttp.ClientSession() as session:
                    async with session.get(str(e.url), timeout=20, allow_redirects=True) as resp:
                        if resp.status != 200:
                            return await ctx.reply("Falha ao baixar a imagem do emoji de origem.")
                        raw_ct = (resp.headers.get("Content-Type") or "").lower()
                        data = await resp.read()
                        image, mime = data, detect_mime(data, raw_ct)
            except discord.Forbidden:
                return await ctx.reply("Sem acesso ao emoji de origem (o bot não participa do servidor de origem).")
            except Exception:
                return await ctx.reply("Não foi possível acessar o emoji de origem (talvez de outro servidor).")

        # 2) URL
        elif origem and (origem.startswith("http://") or origem.startswith("https://")):
            try:
                image, mime = await self._fetch_bytes(origem)
            except Exception as e:
                return await ctx.reply(f"Falha ao baixar a imagem: {e}")

        # 3) Anexo
        elif not origem and ctx.message and ctx.message.attachments:
            att = ctx.message.attachments[0]
            data = await att.read()
            image, mime = data, detect_mime(data, att.content_type)

        else:
            return await ctx.reply("Envie uma URL, um emoji customizado ou anexe uma imagem ao comando.")

        # Conversões e validações
        if image is None:
            return await ctx.reply("Não foi possível obter os bytes da imagem.")
        if len(image) > MAX_BYTES:
            conv = try_convert_to_png(image, mime)
            if conv:
                image, mime = conv
            if len(image) > MAX_BYTES:
                return await ctx.reply("A imagem excede 256 KB após tentativa de redução. Reduza para ~128x128.")

        if not self._mime_supported(mime):
            if WEBP_MIME in mime or "avif" in mime or "webp" in mime:
                conv = try_convert_to_png(image, mime)
                if conv:
                    image, mime = conv
                else:
                    return await ctx.reply("Formato não suportado (WebP/AVIF). Instale Pillow no host ou envie PNG/JPEG/GIF.")
            else:
                return await ctx.reply(f"Formato não suportado: `{mime}`. Use PNG/JPEG ou GIF.")

        # Criar emoji
        try:
            created = await ctx.guild.create_custom_emoji(name=nome, image=image, reason=f"Por {ctx.author}")
        except discord.Forbidden:
            return await ctx.reply("Permissões insuficientes para criar emojis.")
        except discord.HTTPException as e:
            return await ctx.reply(f"Falha ao criar emoji: {e}")

        await ctx.reply(f"Emoji criado: {created} — Nome: {created.name} | ID: {created.id}")


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiManage(bot))
