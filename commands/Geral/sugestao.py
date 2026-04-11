from pathlib import Path
from datetime import datetime

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "sugestoes.json"
FORUM_CHANNEL_ID = 1480968259670114466


def _load() -> dict:
    data = load_json_document(DB_PATH, {"channels": {}, "suggestions": [], "next_id": 1})
    if not isinstance(data, dict):
        data = {"channels": {}, "suggestions": [], "next_id": 1}
    data.setdefault("channels", {})
    data.setdefault("suggestions", [])
    data.setdefault("next_id", 1)
    return data


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _format_datetime() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _split_suggestion_text(raw: str) -> tuple[str, str] | None:
    if "|" not in raw:
        return None
    title, description = raw.split("|", 1)
    title = title.strip()
    description = description.strip()
    if not title or not description:
        return None
    return title[:100], description[:4000]


class Sugestao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_forum_channel(self, guild: discord.Guild) -> discord.ForumChannel | None:
        channel = guild.get_channel(FORUM_CHANNEL_ID)
        if channel is None:
            try:
                fetched = await self.bot.fetch_channel(FORUM_CHANNEL_ID)
            except discord.HTTPException:
                return None
            channel = fetched if isinstance(fetched, discord.abc.GuildChannel) else None
        return channel if isinstance(channel, discord.ForumChannel) else None

    def _build_suggestion_embed(self, ctx: commands.Context, suggestion: dict) -> discord.Embed:
        avatar_url = ctx.author.display_avatar.url
        embed = discord.Embed(
            title=suggestion.get("title") or f"Sugestão #{suggestion['id']}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Quem enviou", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
        embed.add_field(name="Da onde enviou", value=ctx.channel.mention, inline=False)
        embed.add_field(name="Foto do user", value=f"[Abrir avatar]({avatar_url})", inline=False)
        embed.add_field(name="Descrição", value=suggestion["description"][:1024], inline=False)
        embed.add_field(name="Data/hora", value=_format_datetime(), inline=False)
        embed.set_thumbnail(url=avatar_url)
        return embed

    @commands.command(name="sugestao", aliases=["suggest"])
    async def sugestao(self, ctx: commands.Context, acao: str | None = None, *args):
        """Recebe sugestoes dos membros e envia para um canal configurado."""
        data = _load()
        action = (acao or "").strip().lower()

        if action == "config":
            if ctx.guild is None:
                return await ctx.reply("Esse ajuste so funciona em servidores.", mention_author=False)
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.reply("Voce precisa de permissao para configurar o canal de sugestoes.", mention_author=False)
            channel = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else None
            if channel is None:
                return await ctx.reply("Use: sugestao config #canal", mention_author=False)
            data["channels"][str(ctx.guild.id)] = channel.id
            _save(data)
            return await ctx.reply(f"Canal de sugestoes configurado para {channel.mention}.", mention_author=False)

        if action == "listar":
            if ctx.guild is None or not ctx.author.guild_permissions.manage_guild:
                return await ctx.reply("Somente moderadores podem listar sugestoes do servidor.", mention_author=False)
            rows = [row for row in data["suggestions"] if row.get("guild_id") == ctx.guild.id][-10:]
            embed = discord.Embed(title="Sugestoes recentes", color=discord.Color.green())
            if not rows:
                embed.description = "Nenhuma sugestao registrada ainda."
            else:
                embed.description = "\n\n".join(
                    f"**#{row['id']} - {row.get('title', 'Sem titulo')}** - <@{row['author_id']}>\n{row.get('description', row.get('content', ''))}"
                    for row in rows
                )
            return await ctx.reply(embed=embed, mention_author=False)

        content = " ".join(([acao] if acao else []) + list(args)).strip()
        if not content:
            return await ctx.reply("Use: sugestao Titulo | Descricao", mention_author=False)

        parsed = _split_suggestion_text(content)
        if parsed is None:
            return await ctx.reply("Formato invalido. Use: sugestao Titulo | Descricao", mention_author=False)

        title, description = parsed

        suggestion = {
            "id": data["next_id"],
            "guild_id": ctx.guild.id if ctx.guild else None,
            "channel_id": ctx.channel.id,
            "author_id": ctx.author.id,
            "title": title,
            "description": description,
            "content": description,
            "forum_thread_id": None,
        }
        data["next_id"] += 1

        if ctx.guild is None:
            data["suggestions"].append(suggestion)
            _save(data)
            return await ctx.reply("Esse comando precisa ser usado em um servidor para criar o post no fórum de sugestões.", mention_author=False)

        forum_channel = await self._get_forum_channel(ctx.guild)
        if forum_channel is None:
            return await ctx.reply("Nao consegui localizar o fórum de sugestões configurado no servidor.", mention_author=False)

        embed = self._build_suggestion_embed(ctx, suggestion)
        thread_name = f"#{suggestion['id']} - {title}"[:100]

        try:
            thread = await forum_channel.create_thread(name=thread_name, embed=embed)
        except discord.Forbidden:
            return await ctx.reply("Nao tenho permissao para criar posts no fórum de sugestões.", mention_author=False)
        except discord.HTTPException as error:
            return await ctx.reply(f"Falha ao criar a sugestão no fórum: {error}", mention_author=False)

        created_thread = getattr(thread, "thread", None)
        if created_thread is not None:
            suggestion["forum_thread_id"] = created_thread.id

        data["suggestions"].append(suggestion)
        _save(data)

        await ctx.reply(f"Sugestao registrada com o ID #{suggestion['id']}.", mention_author=False)


async def setup(bot):
    await bot.add_cog(Sugestao(bot))