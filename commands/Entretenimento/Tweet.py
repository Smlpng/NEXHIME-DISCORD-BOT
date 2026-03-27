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
TWEET_CHANNEL_ID = 1484012616819937391


def load_tweet_redirects() -> dict[str, int]:
    try:
        with TWEET_REDIRECT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    redirects: dict[str, int] = {}
    for guild_id, channel_id in data.items():
        try:
            redirects[str(guild_id)] = int(channel_id)
        except (TypeError, ValueError):
            continue

    return redirects


def save_tweet_redirects(data: dict[str, int]) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with TWEET_REDIRECT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


class Tweet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_redirect_channels = load_tweet_redirects()

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
        channel_id = self.guild_redirect_channels.get(str(guild_id))
        if channel_id is None:
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
    @commands.hybrid_command(name="tweet_redirect", description="Define o canal para onde o tweet também será enviado neste servidor")
    async def tweet_redirect(self, ctx, canal: discord.TextChannel):
        self.guild_redirect_channels[str(ctx.guild.id)] = canal.id
        save_tweet_redirects(self.guild_redirect_channels)
        await ctx.send(f"Canal de redirecionamento do tweet definido para {canal.mention}.")

    @commands.hybrid_command(description="Cria um tweet falso")
    async def tweet(self, ctx, *, texto: str):
        if getattr(ctx, "interaction", None):
            await ctx.defer()

        target_channel = await self.get_target_channel()
        if target_channel is None:
            await ctx.send(
                "Não consegui encontrar o canal configurado para o tweet na cog. "
                "Verifique a constante TWEET_CHANNEL_ID."
            )
            return

        # carregar fundo
        img = Image.open(BACKGROUND).convert("RGBA")
        draw = ImageDraw.Draw(img)

        width, height = img.size

        # baixar avatar
        avatar_url = ctx.author.display_avatar.url
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")

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

        send_direct_to_target = bool(
            ctx.guild
            and ctx.guild.id == MAIN_GUILD_ID
            and getattr(ctx.channel, "id", None) != getattr(target_channel, "id", None)
        )

        if not send_direct_to_target:
            current_channel_file = discord.File(BytesIO(image_bytes), filename="tweet.png")
            await ctx.send(file=current_channel_file)

        if getattr(target_channel, "id", None) == getattr(ctx.channel, "id", None) and not send_direct_to_target:
            pass
        else:
            target_channel_file = discord.File(BytesIO(image_bytes), filename="tweet.png")
            await target_channel.send(file=target_channel_file)

        if ctx.guild is None:
            return

        redirect_channel = await self.get_guild_redirect_channel(ctx.guild.id)
        if redirect_channel is None:
            return

        redirect_channel_id = getattr(redirect_channel, "id", None)
        if redirect_channel_id in {getattr(ctx.channel, "id", None), getattr(target_channel, "id", None)}:
            return

        redirect_file = discord.File(BytesIO(image_bytes), filename="tweet.png")
        await redirect_channel.send(file=redirect_file)


async def setup(bot):
    await bot.add_cog(Tweet(bot))