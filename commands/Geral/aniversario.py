import json
import time
from pathlib import Path

import discord
from discord.ext import commands, tasks


DB_PATH = Path("DataBase") / "aniversarios.json"


def _load() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text(
            json.dumps({"birthdays": {}, "channels": {}}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {"birthdays": {}, "channels": {}}
    data.setdefault("birthdays", {})
    data.setdefault("channels", {})
    return data


def _save(data: dict) -> None:
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


def _parse_date(value: str) -> tuple[int, int] | None:
    """Parses a dd/mm string and returns (day, month) or None on error."""
    parts = value.strip().split("/")
    if len(parts) != 2:
        return None
    try:
        day, month = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return day, month


class Aniversario(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._announced: set[str] = set()
        self._last_cleared: str = ""
        self.check_birthdays.start()

    def cog_unload(self):
        self.check_birthdays.cancel()

    @tasks.loop(minutes=30)
    async def check_birthdays(self):
        data = _load()
        now = time.localtime()
        today_key = f"{now.tm_mday:02d}/{now.tm_mon:02d}"
        # Clear cache when the date changes so each birthday fires once per year
        if today_key != self._last_cleared:
            self._announced.clear()
            self._last_cleared = today_key
        for guild_id_str, channel_id in data["channels"].items():
            guild = self.bot.get_guild(int(guild_id_str))
            if guild is None:
                continue
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue
            for user_id_str, birthday in data["birthdays"].items():
                announce_key = f"{guild_id_str}:{user_id_str}:{today_key}"
                if birthday == today_key and announce_key not in self._announced:
                    member = guild.get_member(int(user_id_str))
                    if member is None:
                        continue
                    self._announced.add(announce_key)
                    try:
                        embed = discord.Embed(
                            title="🎂 Feliz Aniversário!",
                            description=f"Hoje é o aniversário de {member.mention}! Parabenize! 🎉",
                            color=discord.Color.gold(),
                        )
                        await channel.send(embed=embed)
                    except Exception:
                        pass

    @check_birthdays.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.group(
        name="aniversario",
        aliases=["birthday", "aniver"],
        invoke_without_command=True,
        help="Sistema de aniversários. Subcomandos: definir, ver, remover, lista, canal.",
    )
    async def aniversario(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎂 Sistema de Aniversários",
            description=(
                f"`{ctx.prefix}aniversario definir <dd/mm>` — Registra seu aniversário.\n"
                f"`{ctx.prefix}aniversario ver [@membro]` — Vê o aniversário de alguém.\n"
                f"`{ctx.prefix}aniversario remover` — Remove seu aniversário.\n"
                f"`{ctx.prefix}aniversario lista` — Lista aniversários do servidor.\n"
                f"`{ctx.prefix}aniversario canal #canal` — Define o canal de parabéns (requer Gerenciar Servidor)."
            ),
            color=discord.Color.gold(),
        )
        await ctx.reply(embed=embed, mention_author=False)

    @aniversario.command(name="definir", aliases=["set", "registrar"])
    async def definir(self, ctx: commands.Context, data_nasc: str):
        """Define o aniversário do usuário no formato dd/mm."""
        parsed = _parse_date(data_nasc)
        if parsed is None:
            return await ctx.reply("❌ Formato inválido. Use `dd/mm`, ex.: `15/08`.", mention_author=False)
        day, month = parsed
        birthday_str = f"{day:02d}/{month:02d}"
        db = _load()
        db["birthdays"][str(ctx.author.id)] = birthday_str
        _save(db)
        await ctx.reply(f"✅ Aniversário registrado para **{birthday_str}**.", mention_author=False)

    @aniversario.command(name="ver", aliases=["show", "check"])
    async def ver(self, ctx: commands.Context, membro: discord.Member | None = None):
        """Exibe o aniversário de um membro."""
        target = membro or ctx.author
        db = _load()
        birthday = db["birthdays"].get(str(target.id))
        if birthday is None:
            return await ctx.reply(
                f"{'Você não tem' if target == ctx.author else f'{target.display_name} não tem'} aniversário registrado.",
                mention_author=False,
            )
        await ctx.reply(
            f"🎂 {'Seu aniversário é' if target == ctx.author else f'Aniversário de {target.display_name} é'} **{birthday}**.",
            mention_author=False,
        )

    @aniversario.command(name="remover", aliases=["delete", "deletar"])
    async def remover(self, ctx: commands.Context):
        """Remove o aniversário do usuário."""
        db = _load()
        if str(ctx.author.id) not in db["birthdays"]:
            return await ctx.reply("Você não tem aniversário registrado.", mention_author=False)
        del db["birthdays"][str(ctx.author.id)]
        _save(db)
        await ctx.reply("✅ Aniversário removido.", mention_author=False)

    @aniversario.command(name="lista", aliases=["list", "todos"])
    async def lista(self, ctx: commands.Context):
        """Lista os aniversários registrados no servidor."""
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona apenas em servidores.", mention_author=False)
        db = _load()
        entries = []
        for uid_str, bday in db["birthdays"].items():
            member = ctx.guild.get_member(int(uid_str))
            if member:
                entries.append((bday, member.display_name))
        entries.sort(key=lambda x: (int(x[0].split("/")[1]), int(x[0].split("/")[0])))
        if not entries:
            return await ctx.reply("Nenhum aniversário registrado neste servidor.", mention_author=False)
        lines = [f"**{bday}** — {name}" for bday, name in entries[:20]]
        embed = discord.Embed(
            title=f"🎂 Aniversários de {ctx.guild.name}",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await ctx.reply(embed=embed, mention_author=False)

    @aniversario.command(name="canal", aliases=["setchannel", "channel"])
    @commands.has_permissions(manage_guild=True)
    async def canal(self, ctx: commands.Context, canal: discord.TextChannel):
        """Define o canal onde os parabéns serão enviados."""
        db = _load()
        db["channels"][str(ctx.guild.id)] = canal.id
        _save(db)
        await ctx.reply(f"✅ Canal de aniversários definido para {canal.mention}.", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Aniversario(bot))
