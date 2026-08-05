import json
import asyncio
import discord
from discord.ext import commands
from pathlib import Path
from datetime import datetime, timezone

# Tempo de espera: 2 horas em segundos
BUMP_DELAY = 2 * 60 * 61

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

        for guild_id, entry in data.items():
            if guild_id in self.pending and not self.pending[guild_id].done():
                continue

            remaining = entry["remind_at"] - now

            task = asyncio.create_task(
                self._reminder_loop(
                    guild_id,
                    entry["channel_id"],
                    entry["user_id"],
                    max(remaining, 0),
                )
            )

            self.pending[guild_id] = task

    def _store_reminder(self, guild_id: str, channel_id: int, user_id: int, remind_at: float) -> None:
        data = _load()
        data[guild_id] = {
            "user_id": user_id,
            "channel_id": channel_id,
            "remind_at": remind_at,
        }
        _save(data)

    def _clear_reminder(self, guild_id: str) -> None:
        data = _load()
        data.pop(guild_id, None)
        _save(data)

    def _cancel_pending(self, guild_id: str, clear_data: bool = False) -> bool:
        task = self.pending.pop(guild_id, None)
        if task is not None:
            task.cancel()

        if clear_data:
            self._clear_reminder(guild_id)

        return task is not None

    async def _reminder_loop(self, guild_id: str, channel_id: int, user_id: int, delay: float):
        try:
            next_delay = delay

            while True:
                if next_delay > 0:
                    await asyncio.sleep(next_delay)

                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    await channel.send(
                        f"<@{user_id}> ⏰ Já se passaram 2 horas! "
                        f"Está na hora de fazer o `/bump` de novo! Se você não deseja mais receber este lembrete, use `n!stop_bump`."
                    )

                next_delay = BUMP_DELAY
                remind_at = datetime.now(timezone.utc).timestamp() + next_delay
                self._store_reminder(guild_id, channel_id, user_id, remind_at)
        except asyncio.CancelledError:
            raise
        finally:
            task = self.pending.get(guild_id)
            if task is asyncio.current_task():
                self.pending.pop(guild_id, None)

    # ──────────────────────────────────────────────
    # Comando híbrido: !bump_reminder / /bump_reminder
    # ──────────────────────────────────────────────

    @commands.command(
        name="bump_reminder",
        help="Inicia um lembrete recorrente de 2 horas para fazer o /bump novamente."
    )
    async def bump_reminder(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Este comando funciona apenas em servidores.")
            return

        guild_id = str(ctx.guild.id)

        # Cancela timer anterior (se existir)
        self._cancel_pending(guild_id, clear_data=False)

        remind_at = datetime.now(timezone.utc).timestamp() + BUMP_DELAY
        self._store_reminder(guild_id, ctx.channel.id, ctx.author.id, remind_at)

        task = asyncio.create_task(
            self._reminder_loop(guild_id, ctx.channel.id, ctx.author.id, BUMP_DELAY)
        )
        self.pending[guild_id] = task

        await ctx.reply(
            "✅ Lembrete registrado! Vou continuar te avisando a cada **2 horas** até você usar `n!stop_bump`."
        )

    @commands.command(
        name="stop_bump",
        help="Encerra o lembrete recorrente do /bump neste servidor."
    )
    async def stop_bump(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Este comando funciona apenas em servidores.")
            return

        guild_id = str(ctx.guild.id)
        stopped = self._cancel_pending(guild_id, clear_data=True)

        if not stopped and guild_id not in _load():
            await ctx.reply("Não há nenhum lembrete de bump ativo neste servidor.")
            return

        await ctx.reply("🛑 Lembrete de bump encerrado. Não vou mais enviar avisos até um novo `n!bump_reminder`.")


async def setup(bot: commands.Bot):
    await bot.add_cog(BumpReminder(bot))
