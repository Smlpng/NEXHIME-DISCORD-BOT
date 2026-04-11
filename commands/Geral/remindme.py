import asyncio
import time
from pathlib import Path

import discord
from discord.ext import commands, tasks

from mongo import load_json_document, save_json_document


DB_PATH = Path("DataBase") / "reminders.json"


def _load() -> list[dict]:
    data = load_json_document(DB_PATH, [])
    return data if isinstance(data, list) else []


def _save(data: list[dict]) -> None:
    save_json_document(DB_PATH, data)

class RemindMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @commands.command(
        name="remindme",
        aliases=["lembrete", "lembrar", "remind"],
        help="Envia um lembrete após um tempo (ex: 10m, 2h, 1d)."
    )
    async def remindme(self, ctx: commands.Context, time: str, *, message: str):
        """Envia uma mensagem de lembrete após o tempo especificado na DM."""
        try:
            time_seconds = self.convert_time_to_seconds(time)
            if time_seconds is None:
                await ctx.reply("Formato de tempo inválido. Use algo como '5m', '1h', '2d'.", mention_author=False)
                return

            reminders = _load()
            reminder_id = max((entry.get("id", 0) for entry in reminders), default=0) + 1
            reminders.append(
                {
                    "id": reminder_id,
                    "user_id": ctx.author.id,
                    "channel_id": ctx.channel.id,
                    "message": message,
                    "created_at": int(time.time()),
                    "due_at": int(time.time()) + time_seconds,
                }
            )
            _save(reminders)
            await ctx.reply(f"Lembrete #{reminder_id} configurado para `{time}`.", mention_author=False)

        except Exception as e:
            await ctx.send(f"Erro ao configurar o lembrete: {e}")

    @commands.command(name="lembretes", aliases=["reminders"], help="Lista seus lembretes ativos.")
    async def lembretes(self, ctx: commands.Context):
        reminders = [entry for entry in _load() if entry.get("user_id") == ctx.author.id]
        if not reminders:
            return await ctx.reply("Voce nao possui lembretes ativos.", mention_author=False)
        description = "\n".join(
            f"**#{entry['id']}** - <t:{entry['due_at']}:R>\n{entry['message']}"
            for entry in reminders[:20]
        )
        embed = discord.Embed(title=f"Lembretes de {ctx.author}", description=description, color=discord.Color.blurple())
        await ctx.reply(embed=embed, mention_author=False)

    def convert_time_to_seconds(self, time_str: str):
        """Converte o tempo no formato 'Xd', 'Xh', 'Xm', 'Xs' para segundos."""
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = time_str[-1]
        if unit not in time_units:
            return None
        try:
            value = int(time_str[:-1])
            return value * time_units[unit]
        except ValueError:
            return None

    @tasks.loop(seconds=20)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        now_ts = int(time.time())
        reminders = _load()
        remaining = []
        for entry in reminders:
            if int(entry.get("due_at", 0)) > now_ts:
                remaining.append(entry)
                continue
            user = self.bot.get_user(int(entry.get("user_id", 0)))
            if user is None:
                try:
                    user = await self.bot.fetch_user(int(entry.get("user_id", 0)))
                except discord.HTTPException:
                    continue
            try:
                await user.send(f"Lembrete: {entry.get('message', '')}")
            except discord.HTTPException:
                continue
        if remaining != reminders:
            _save(remaining)

async def setup(bot):
    await bot.add_cog(RemindMe(bot))
