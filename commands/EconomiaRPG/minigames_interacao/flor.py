import discord
from discord.ext import commands
from pathlib import Path
import time

from mongo import load_json_document, save_json_document

from commands.EconomiaRPG.utils.database import ensure_profile, get_active_hero, update_active_hero_resources

ROOT_DIR = Path(__file__).resolve().parents[3]
FLORES_FILE = ROOT_DIR / "DataBase" / "flor.json"
FLOWER_EMOJIS = {"🌹", "🌸", "🌺", "🌻", "🌷", "💐", "🪻", "🥀"}


def _load_flores() -> dict:
    data = load_json_document(FLORES_FILE, {})
    return data if isinstance(data, dict) else {}


def _save_flores(data: dict):
    save_json_document(FLORES_FILE, data)


class Flor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}
        self.COOLDOWN_TIME = 45

    @commands.command(
        name="bolsa_flores",
        aliases=["bolsa_flor", "minha_bolsa_flores", "flower_bag"],
        help="Mostra a bolsa de flores equipada, capacidade e saldo atual."
    )
    async def bolsa_flores(self, ctx: commands.Context):
        ensure_profile(ctx.author.id)
        profile = get_active_hero(ctx.author.id)
        if profile is None:
            return await ctx.reply("Nao consegui localizar seu perfil de flores.", mention_author=False)

        bag_name = str(profile.get("flower_bag", "Bolsa de flores basica"))
        capacity = int(profile.get("flower_capacity", 100))
        flowers = int(profile.get("flower", 0))

        embed = discord.Embed(
            title="🌹 Sua bolsa de flores",
            color=discord.Color.pink(),
        )
        embed.add_field(name="Bolsa equipada", value=bag_name, inline=False)
        embed.add_field(name="Capacidade", value=f"{capacity} flores", inline=True)
        embed.add_field(name="Disponivel", value=f"{flowers} flores", inline=True)
        embed.set_footer(text=f"Espaco restante: {max(capacity - flowers, 0)} flor(es).")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        flower_emoji = str(payload.emoji)
        if flower_emoji in FLOWER_EMOJIS:
            if payload.user_id == self.bot.user.id:
                return

            channel = self.bot.get_channel(payload.channel_id)
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(payload.channel_id)
                except discord.HTTPException:
                    return

            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.HTTPException:
                return

            target = message.author

            reactor = payload.member
            if not reactor:
                reactor = self.bot.get_user(payload.user_id)
                if not reactor:
                    try:
                        reactor = await self.bot.fetch_user(payload.user_id)
                    except discord.HTTPException:
                        reactor = None

            if reactor and target.id == reactor.id:
                return

            ensure_profile(payload.user_id)
            giver_profile = get_active_hero(payload.user_id)
            if giver_profile is None:
                return

            current_flowers = int(giver_profile.get("flower", 0))
            if current_flowers <= 0:
                try:
                    aviso = await channel.send(
                        f"🚫 {reactor.mention if reactor else f'<@{payload.user_id}>'}, você está sem flores na bolsa."
                    )
                    await aviso.delete(delay=5.0)
                except discord.HTTPException:
                    pass

                try:
                    if reactor and message.guild:
                        await message.remove_reaction(payload.emoji, reactor)
                except discord.HTTPException:
                    pass
                return

            if reactor:
                reactor_id = str(reactor.id)
                current_time = time.time()

                if reactor_id in self.cooldowns:
                    last_time = self.cooldowns[reactor_id]
                    if current_time - last_time < self.COOLDOWN_TIME:
                        remaining_time = int(self.COOLDOWN_TIME - (current_time - last_time))
                        try:
                            aviso = await channel.send(
                                f"⏳ {reactor.mention}, aguarde **{remaining_time} segundos** para entregar outra flor."
                            )
                            await aviso.delete(delay=5.0)
                        except discord.HTTPException:
                            pass

                        try:
                            if message.guild:
                                await message.remove_reaction(payload.emoji, reactor)
                        except discord.HTTPException:
                            pass

                        return

            spent = update_active_hero_resources(payload.user_id, flower=-1)
            if not spent:
                try:
                    aviso = await channel.send(
                        f"🚫 {reactor.mention if reactor else f'<@{payload.user_id}>'}, você está sem flores na bolsa."
                    )
                    await aviso.delete(delay=5.0)
                except discord.HTTPException:
                    pass
                return

            if reactor:
                self.cooldowns[str(reactor.id)] = time.time()
            updated_profile = get_active_hero(payload.user_id)
            remaining_flowers = int(updated_profile.get("flower", 0)) if updated_profile else 0

            flores_data = _load_flores()
            target_id = str(target.id)
            flores_data[target_id] = flores_data.get(target_id, 0) + 1
            _save_flores(flores_data)

            total_flores = flores_data[target_id]
            reactor_mention = reactor.mention if reactor else f"<@{payload.user_id}>"

            embed = discord.Embed(
                title=f"{flower_emoji} Flor entregue!",
                description=f"{reactor_mention} entregou {flower_emoji} para {target.mention}!",
                color=discord.Color.pink()
            )
            embed.set_footer(
                text=(
                    f"Que fofo! {target.display_name} já recebeu {total_flores} flor(es) no total! "
                    f"Restam {remaining_flowers} flores na bolsa de quem enviou."
                )
            )

            await channel.send(embed=embed)

    @commands.command(
        name="flores_rank",
        aliases=["frank", "rank_flores", "flores", "ranking_flores"],
        help="Mostra o ranking global de quem mais recebeu flores"
    )
    async def rank_flores(self, ctx: commands.Context):
        flores_data = _load_flores()

        if not flores_data:
            await ctx.reply("Ninguém recebeu flores ainda! 🌹", mention_author=False)
            return

        sorted_flores = sorted(flores_data.items(), key=lambda item: item[1], reverse=True)
        top_10 = sorted_flores[:10]

        embed = discord.Embed(
            title="🏆 Ranking Global de Flores",
            description="As pessoas que mais receberam flores no bot!",
            color=discord.Color.pink()
        )

        rank_text = ""
        for i, (user_id, count) in enumerate(top_10, 1):
            user = self.bot.get_user(int(user_id))
            user_display = user.name if user else f"<@{user_id}>"

            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            rank_text += f"{medal} **{user_display}** - {count} flor(es)\n"

        embed.add_field(name="Top 10", value=rank_text, inline=False)
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Flor(bot))