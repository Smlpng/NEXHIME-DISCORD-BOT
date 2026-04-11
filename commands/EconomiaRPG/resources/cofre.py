import time
from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "vaults.json"
LOCK_SECONDS = 6 * 60 * 60
BONUS_RATE = 0.15


def _load() -> dict:
    data = load_json_document(DB_PATH, {})
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


class Cofre(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="cofre", invoke_without_command=True, help="Deposita nex em um cofre temporario com bonus.")
    async def cofre(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        data = _load().get(str(inte.user.id))
        if not data:
            return await inte.response.send_message("Voce nao tem nenhum valor guardado no cofre.")
        ready_at = int(data["ready_at"])
        amount = int(data["amount"])
        await inte.response.send_message(f"Seu cofre atual guarda {amount} nex e libera <t:{ready_at}:R>.")

    @cofre.command(name="depositar")
    async def cofre_depositar(self, ctx: commands.Context, amount: int):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        hero = get_active_hero(inte.user.id)
        if hero is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para usar o cofre.")
        if amount <= 0:
            return await inte.response.send_message("Informe um valor positivo.")
        if _load().get(str(inte.user.id)):
            return await inte.response.send_message("Voce ja possui um deposito ativo no cofre. Saque antes de abrir outro.")
        if int(hero.get("nex", 0)) < amount:
            return await inte.response.send_message("Voce nao tem nex suficiente na carteira.")
        if not update_active_hero_resources(inte.user.id, nex=-amount):
            return await inte.response.send_message("Nao foi possivel mover esse valor para o cofre.")

        db = _load()
        db[str(inte.user.id)] = {
            "amount": amount,
            "created_at": int(time.time()),
            "ready_at": int(time.time()) + LOCK_SECONDS,
        }
        _save(db)
        await inte.response.send_message(f"{amount} nex foram guardados no cofre por 6 horas.")

    @cofre.command(name="sacar")
    async def cofre_sacar(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        db = _load()
        entry = db.get(str(inte.user.id))
        if not entry:
            return await inte.response.send_message("Voce nao tem deposito ativo no cofre.")
        if int(entry["ready_at"]) > int(time.time()):
            return await inte.response.send_message(f"Seu cofre ainda esta fechado. Libera <t:{int(entry['ready_at'])}:R>.")

        amount = int(entry["amount"])
        final_amount = int(round(amount * (1 + BONUS_RATE)))
        update_active_hero_resources(inte.user.id, nex=final_amount)
        db.pop(str(inte.user.id), None)
        _save(db)
        hero = get_active_hero(inte.user.id)
        embed = discord.Embed(title="Cofre aberto", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Valor guardado", value=str(amount), inline=True)
        embed.add_field(name="Valor final", value=str(final_amount), inline=True)
        embed.add_field(name="Carteira", value=f"{hero['nex']} nex", inline=True)
        await inte.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Cofre(bot))