import time
from pathlib import Path

import discord
from discord.ext import commands, tasks

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "agenda.json"
TIME_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _load() -> dict:
    data = load_json_document(DB_PATH, {"next_id": 1, "events": []})
    if not isinstance(data, dict):
        data = {"next_id": 1, "events": []}
    data.setdefault("next_id", 1)
    data.setdefault("events", [])
    return data


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _parse_time(value: str) -> int | None:
    if not value:
        return None
    unit = value[-1].lower()
    if unit not in TIME_UNITS:
        return None
    try:
        amount = int(value[:-1])
    except ValueError:
        return None
    return amount * TIME_UNITS[unit] if amount > 0 else None


class Agenda(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_events.start()

    def cog_unload(self):
        self.check_events.cancel()

    @tasks.loop(seconds=30)
    async def check_events(self):
        data = _load()
        now = int(time.time())
        changed = False
        for event in data["events"]:
            if event.get("sent") or event.get("due_at", 0) > now:
                continue
            channel = self.bot.get_channel(event["channel_id"])
            if channel is None:
                continue
            try:
                embed = discord.Embed(title="Evento da agenda", description=event["title"], color=discord.Color.gold())
                embed.add_field(name="Criado por", value=f"<@{event['author_id']}>", inline=False)
                await channel.send(embed=embed)
                event["sent"] = True
                changed = True
            except Exception:
                continue
        if changed:
            _save(data)

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

    @commands.command(name="agenda", aliases=["agendaevento"])
    async def agenda(self, ctx: commands.Context, acao: str | None = None, argumento: str | None = None, *, titulo: str | None = None):
        """Cria, lista e remove eventos simples agendados no servidor."""
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona apenas em servidores.", mention_author=False)

        action = (acao or "listar").strip().lower()
        data = _load()

        if action in {"listar", "list"}:
            events = [row for row in data["events"] if row["guild_id"] == ctx.guild.id and not row.get("sent")]
            events.sort(key=lambda row: row.get("due_at", 0))
            embed = discord.Embed(title=f"Agenda de {ctx.guild.name}", color=discord.Color.blue())
            if not events:
                embed.description = "Nenhum evento pendente no momento."
            else:
                embed.description = "\n\n".join(
                    f"**#{event['id']}** - {event['title']}\nCanal: <#{event['channel_id']}>\nQuando: <t:{event['due_at']}:F>"
                    for event in events[:10]
                )
            return await ctx.reply(embed=embed, mention_author=False)

        if action == "criar":
            seconds = _parse_time(argumento or "")
            if seconds is None or not titulo:
                return await ctx.reply("Uso: agenda criar <tempo> <titulo>. Ex.: agenda criar 2h Raid semanal", mention_author=False)
            event = {
                "id": data["next_id"],
                "guild_id": ctx.guild.id,
                "channel_id": ctx.channel.id,
                "author_id": ctx.author.id,
                "title": titulo,
                "due_at": int(time.time()) + seconds,
                "sent": False,
            }
            data["next_id"] += 1
            data["events"].append(event)
            _save(data)
            return await ctx.reply(f"Evento #{event['id']} criado para <t:{event['due_at']}:F>.", mention_author=False)

        if action in {"remover", "delete", "cancelar"}:
            if not (argumento or "").isdigit():
                return await ctx.reply("Uso: agenda remover <id>.", mention_author=False)
            event_id = int(argumento)
            before = len(data["events"])
            data["events"] = [
                event for event in data["events"]
                if not (event["id"] == event_id and event["guild_id"] == ctx.guild.id and (event["author_id"] == ctx.author.id or ctx.author.guild_permissions.manage_guild))
            ]
            if len(data["events"]) == before:
                return await ctx.reply("Evento nao encontrado ou sem permissao para remover.", mention_author=False)
            _save(data)
            return await ctx.reply(f"Evento #{event_id} removido da agenda.", mention_author=False)

        await ctx.reply("Uso: agenda listar, agenda criar <tempo> <titulo> ou agenda remover <id>.", mention_author=False)


async def setup(bot):
    await bot.add_cog(Agenda(bot))