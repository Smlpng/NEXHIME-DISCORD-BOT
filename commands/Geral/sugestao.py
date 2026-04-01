import json
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "sugestoes.json"


def _load() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"channels": {}, "suggestions": [], "next_id": 1}, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {"channels": {}, "suggestions": [], "next_id": 1}
    data.setdefault("channels", {})
    data.setdefault("suggestions", [])
    data.setdefault("next_id", 1)
    return data


def _save(data: dict) -> None:
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


class Sugestao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
                    f"**#{row['id']}** - <@{row['author_id']}>\n{row['content']}"
                    for row in rows
                )
            return await ctx.reply(embed=embed, mention_author=False)

        content = " ".join(([acao] if acao else []) + list(args)).strip()
        if not content:
            return await ctx.reply("Use: sugestao <mensagem> ou sugestao config #canal", mention_author=False)

        suggestion = {
            "id": data["next_id"],
            "guild_id": ctx.guild.id if ctx.guild else None,
            "channel_id": ctx.channel.id,
            "author_id": ctx.author.id,
            "content": content,
        }
        data["next_id"] += 1
        data["suggestions"].append(suggestion)
        _save(data)

        if ctx.guild is not None:
            target_channel_id = data["channels"].get(str(ctx.guild.id))
            if target_channel_id:
                target_channel = ctx.guild.get_channel(int(target_channel_id))
                if target_channel is not None:
                    embed = discord.Embed(title=f"Nova sugestao #{suggestion['id']}", description=content, color=discord.Color.green())
                    embed.add_field(name="Autor", value=f"{ctx.author} ({ctx.author.id})", inline=False)
                    embed.add_field(name="Origem", value=ctx.channel.mention, inline=False)
                    try:
                        await target_channel.send(embed=embed)
                    except Exception:
                        pass

        await ctx.reply(f"Sugestao registrada com o ID #{suggestion['id']}.", mention_author=False)


async def setup(bot):
    await bot.add_cog(Sugestao(bot))