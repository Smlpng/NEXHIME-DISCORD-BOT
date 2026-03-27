import json
import asyncio
import discord
from discord.ext import commands
from pathlib import Path
from datetime import datetime, timezone

# Tempo de espera: 2 horas em segundos
BUMP_DELAY = 2 * 60 * 60

DB_PATH = Path(__file__).resolve().parents[2] / "DataBase" / "bump_reminder.json"


# ──────────────────────────────────────────────
# Helpers de persistência
# ──────────────────────────────────────────────

def _load() -> dict:
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save(data: dict) -> None:
    tmp = str(DB_PATH) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    Path(tmp).replace(DB_PATH)


# ──────────────────────────────────────────────
# Cog
# ──────────────────────────────────────────────

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # guild_id (str) → asyncio.Task
        self.pending: dict[str, asyncio.Task] = {}

    # Restaura timers salvos quando o bot fica pronto
    @commands.Cog.listener()
    async def on_ready(self):
        await self._restore_pending()

    async def _restore_pending(self):
        data = _load()
        now = datetime.now(timezone.utc).timestamp()
        to_remove = []

        for guild_id, entry in data.items():
            remaining = entry["remind_at"] - now

            if remaining <= 0:
                task = asyncio.create_task(
                    self._send_reminder(guild_id, entry["channel_id"], entry["user_id"], 0)
                )
                to_remove.append(guild_id)
            else:
                task = asyncio.create_task(
                    self._send_reminder(guild_id, entry["channel_id"], entry["user_id"], remaining)
                )

            self.pending[guild_id] = task

        for gid in to_remove:
            data.pop(gid, None)

        _save(data)

    async def _send_reminder(self, guild_id: str, channel_id: int, user_id: int, delay: float):
        if delay > 0:
            await asyncio.sleep(delay)

        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            await channel.send(
                f"<@{user_id}> ⏰ Já se passaram 2 horas! "
                f"Está na hora de fazer o `/bump` de novo!"
            )

        data = _load()
        data.pop(guild_id, None)
        _save(data)
        self.pending.pop(guild_id, None)

    # ──────────────────────────────────────────────
    # Comando híbrido: !bump_reminder / /bump_reminder
    # ──────────────────────────────────────────────

    @commands.hybrid_command(
        name="bump_reminder",
        description="Inicia um lembrete de 2 horas para fazer o /bump novamente."
    )
    async def bump_reminder(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)

        # Cancela timer anterior (se existir)
        if guild_id in self.pending:
            self.pending[guild_id].cancel()

        remind_at = datetime.now(timezone.utc).timestamp() + BUMP_DELAY
        data = _load()
        data[guild_id] = {
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "remind_at": remind_at
        }
        _save(data)

        task = asyncio.create_task(
            self._send_reminder(guild_id, ctx.channel.id, ctx.author.id, BUMP_DELAY)
        )
        self.pending[guild_id] = task

        await ctx.reply(
            f"✅ Lembrete registrado! Vou te avisar em **2 horas** para fazer o `/bump` de novo. 🔔",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(BumpReminder(bot))
