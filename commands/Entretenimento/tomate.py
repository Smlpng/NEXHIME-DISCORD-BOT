import discord
from discord.ext import commands
import json
from pathlib import Path
import time

from commands.RPG.utils.database import ensure_profile, get_active_hero, update_active_hero_resources

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "DataBase"
TOMATADAS_FILE = DB_DIR / "tomate.json"

def _load_tomatadas() -> dict:
    try:
        with TOMATADAS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_tomatadas(data: dict):
    DB_DIR.mkdir(parents=True, exist_ok=True)
    tmp = TOMATADAS_FILE.with_name(TOMATADAS_FILE.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(TOMATADAS_FILE)

class Tomate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dicionário para armazenar o tempo do último tomate de cada usuário (ID do usuário -> timestamp)
        self.cooldowns = {}
        self.COOLDOWN_TIME = 45  # 45 segundos

    @commands.command(
        name="bolsa_tomates",
        aliases=["bolsa_tomate", "minha_bolsa_tomates", "tomate_bag"],
        help="Mostra a bolsa de tomates equipada, capacidade e saldo atual."
    )
    async def bolsa_tomates(self, ctx: commands.Context):
        ensure_profile(ctx.author.id)
        profile = get_active_hero(ctx.author.id)
        if profile is None:
            return await ctx.reply("Nao consegui localizar seu perfil de tomates.", mention_author=False)

        bag_name = str(profile.get("tomato_bag", "Bolsa basica"))
        capacity = int(profile.get("tomato_capacity", 100))
        tomatoes = int(profile.get("tomato", 0))

        embed = discord.Embed(
            title="🍅 Sua bolsa de tomates",
            color=discord.Color.red(),
        )
        embed.add_field(name="Bolsa equipada", value=bag_name, inline=False)
        embed.add_field(name="Capacidade", value=f"{capacity} tomates", inline=True)
        embed.add_field(name="Disponivel", value=f"{tomatoes} tomates", inline=True)
        embed.set_footer(text=f"Espaco restante: {max(capacity - tomatoes, 0)} tomate(s).")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Verifica se o emoji reagido é um tomate
        if str(payload.emoji) == "🍅" or payload.emoji.name == "🍅":
            # Ignora reações do próprio bot
            if payload.user_id == self.bot.user.id:
                return
            
            # Obtém o canal onde a reação ocorreu
            channel = self.bot.get_channel(payload.channel_id)
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(payload.channel_id)
                except discord.HTTPException:
                    return

            # Obtém a mensagem que recebeu a reação
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.HTTPException:
                return
            
            # O alvo do tomate é o autor da mensagem
            target = message.author
            
            # Obtém quem atirou o tomate
            reactor = payload.member
            if not reactor:
                reactor = self.bot.get_user(payload.user_id)
                if not reactor:
                    try:
                        reactor = await self.bot.fetch_user(payload.user_id)
                    except discord.HTTPException:
                        reactor = None
            
            # Verifica se o alvo é a própria pessoa (auto-tomatada)
            if reactor and target.id == reactor.id:
                return # Ignora se a pessoa tentar jogar tomate nela mesma

            ensure_profile(payload.user_id)
            thrower_profile = get_active_hero(payload.user_id)
            if thrower_profile is None:
                return

            current_tomatoes = int(thrower_profile.get("tomato", 0))
            if current_tomatoes <= 0:
                try:
                    aviso = await channel.send(
                        f"🚫 {reactor.mention if reactor else f'<@{payload.user_id}>'}, você está sem tomates na bolsa."
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
            
            # Verifica o cooldown do atirador
            if reactor:
                reactor_id = str(reactor.id)
                current_time = time.time()
                
                if reactor_id in self.cooldowns:
                    last_time = self.cooldowns[reactor_id]
                    if current_time - last_time < self.COOLDOWN_TIME:
                        # Em cooldown
                        remaining_time = int(self.COOLDOWN_TIME - (current_time - last_time))
                        # Mandar mensagem temporária avisando do cooldown
                        try:
                            aviso = await channel.send(f"⏳ {reactor.mention}, você está sem tomates! Aguarde **{remaining_time} segundos** para arremessar outro.")
                            # Deleta a mensagem após 5 segundos para não poluir
                            await aviso.delete(delay=5.0)
                        except discord.HTTPException:
                            pass
                        
                        # Remove a reação do usuário para ele não achar que o tomate foi computado
                        try:
                            if message.guild: # Só consegue remover reações no servidor, não na DM
                                await message.remove_reaction(payload.emoji, reactor)
                        except discord.HTTPException:
                            pass
                            
                        return

            spent = update_active_hero_resources(payload.user_id, tomato=-1)
            if not spent:
                try:
                    aviso = await channel.send(
                        f"🚫 {reactor.mention if reactor else f'<@{payload.user_id}>'}, você está sem tomates na bolsa."
                    )
                    await aviso.delete(delay=5.0)
                except discord.HTTPException:
                    pass
                return

            if reactor:
                self.cooldowns[str(reactor.id)] = time.time()
            updated_profile = get_active_hero(payload.user_id)
            remaining_tomatoes = int(updated_profile.get("tomato", 0)) if updated_profile else 0

            # Atualiza e salva o contador de tomatadas
            tomatadas_data = _load_tomatadas()
            target_id = str(target.id)
            tomatadas_data[target_id] = tomatadas_data.get(target_id, 0) + 1
            _save_tomatadas(tomatadas_data)
            
            total_tomatadas = tomatadas_data[target_id]
            
            
            reactor_mention = reactor.mention if reactor else f"<@{payload.user_id}>"
            
            # Cria a embed de aviso
            embed = discord.Embed(
                title="🍅 Tomatada!",
                description=f"{reactor_mention} arremessou um tomate em {target.mention}!",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Coitado(a)! Já levou {total_tomatadas} tomatada(s) no total! Restam {remaining_tomatoes} tomates na bolsa de quem jogou.")
            
            # Envia a embed no mesmo canal
            await channel.send(embed=embed)

    @commands.command(name="tomatadas_rank", aliases=["trank", "rank_tomates", "tomatadas", "tomates"], help="Mostra o ranking global de quem mais levou tomatadas")
    async def rank_tomatadas(self, ctx: commands.Context):
        tomatadas_data = _load_tomatadas()
        
        if not tomatadas_data:
            await ctx.reply("Ninguém levou tomatadas ainda! 🍅")
            return
            
        # Ordena o dicionário pelo número de tomatadas em ordem decrescente
        sorted_tomatadas = sorted(tomatadas_data.items(), key=lambda item: item[1], reverse=True)
        
        # Pega o top 10
        top_10 = sorted_tomatadas[:10]
        
        embed = discord.Embed(
            title="🏆 Ranking Global de Tomatadas",
            description="Os maiores alvos de tomates do bot!",
            color=discord.Color.red()
        )
        
        # Constrói o texto do ranking
        rank_text = ""
        for i, (user_id, count) in enumerate(top_10, 1):
            # Tenta pegar o nome de usuário se ele estiver no cache do bot
            user = self.bot.get_user(int(user_id))
            user_display = user.name if user else f"<@{user_id}>"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            rank_text += f"{medal} **{user_display}** - {count} tomatada(s)\n"
            
        embed.add_field(name="Top 10", value=rank_text, inline=False)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tomate(bot))
