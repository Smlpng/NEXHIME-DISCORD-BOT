from pathlib import Path

import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "rpg_market.json"
RESOURCE_LABELS = {
    "madeira": ("wood", "Madeira", "ðŸŒ²"),
    "wood": ("wood", "Madeira", "ðŸŒ²"),
    "ferro": ("iron", "Ferro", "â›ï¸"),
    "iron": ("iron", "Ferro", "â›ï¸"),
    "nex": ("nex", "Nex", "ðŸ’°"),
}


def _load() -> dict:
    data = load_json_document(DB_PATH, {"next_id": 1, "offers": []})
    if not isinstance(data, dict):
        data = {"next_id": 1, "offers": []}
    data.setdefault("next_id", 1)
    data.setdefault("offers", [])
    return data


def _save(data: dict) -> None:
    save_json_document(DB_PATH, data)


def _parse_resource(value: str):
    return RESOURCE_LABELS.get((value or "").strip().lower())


class Mercado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _resolve_name(self, user_id: int, guild: discord.Guild | None) -> str:
        if guild is not None:
            member = guild.get_member(user_id)
            if member is not None:
                return member.display_name
        user = self.bot.get_user(user_id)
        if user is not None:
            return user.display_name
        try:
            fetched = await self.bot.fetch_user(user_id)
            return fetched.display_name
        except discord.HTTPException:
            return str(user_id)

    @commands.command(name="mercado", aliases=["market"])
    async def mercado(self, ctx, acao: str | None = None, *args):
        """Mercado assÃ­ncrono de recursos do RPG."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Voce precisa ter um heroi ativo para usar o mercado.")

        action = (acao or "listar").strip().lower()
        data = _load()

        if action in {"listar", "list"}:
            offers = [offer for offer in data["offers"] if offer.get("status") == "open"][:10]
            embed = discord.Embed(title="Mercado do Reino", color=RPG_PRIMARY_COLOR)
            if not offers:
                embed.description = "Nao ha ofertas abertas no momento."
            else:
                lines = []
                for offer in offers:
                    seller = await self._resolve_name(offer["seller_id"], inte.guild)
                    give_key, give_label, give_emoji = _parse_resource(offer["give"])
                    receive_key, receive_label, receive_emoji = _parse_resource(offer["receive"])
                    lines.append(
                        f"**#{offer['id']}** - {seller}\n"
                        f"Oferece {offer['give_amount']} {give_label} {give_emoji} por {offer['receive_amount']} {receive_label} {receive_emoji}"
                    )
                embed.description = "\n\n".join(lines)
            embed.set_footer(text="Use mercado criar, mercado aceitar <id> ou mercado cancelar <id>.")
            return await inte.response.send_message(embed=embed)

        if action == "criar":
            if len(args) < 4:
                return await inte.response.send_message("Uso: mercado criar <recurso_oferecido> <qtd> <recurso_recebido> <qtd>.")
            give_info = _parse_resource(args[0])
            receive_info = _parse_resource(args[2])
            if give_info is None or receive_info is None:
                return await inte.response.send_message("Recursos validos: madeira, ferro e nex.")
            try:
                give_amount = int(args[1])
                receive_amount = int(args[3])
            except ValueError:
                return await inte.response.send_message("As quantidades precisam ser numeros inteiros.")
            if give_amount <= 0 or receive_amount <= 0:
                return await inte.response.send_message("As quantidades precisam ser maiores que zero.")
            if give_info[0] == receive_info[0]:
                return await inte.response.send_message("A oferta precisa trocar recursos diferentes.")

            hero = get_active_hero(inte.user.id)
            if int(hero.get(give_info[0], 0)) < give_amount:
                return await inte.response.send_message("Voce nao tem recursos suficientes para abrir essa oferta.")

            if not update_active_hero_resources(inte.user.id, **{give_info[0]: -give_amount}):
                return await inte.response.send_message("Nao foi possivel reservar os recursos dessa oferta.")

            offer = {
                "id": data["next_id"],
                "seller_id": inte.user.id,
                "give": give_info[0],
                "give_amount": give_amount,
                "receive": receive_info[0],
                "receive_amount": receive_amount,
                "status": "open",
            }
            data["next_id"] += 1
            data["offers"].append(offer)
            _save(data)
            return await inte.response.send_message(f"Oferta #{offer['id']} criada com sucesso no mercado.")

        if action == "cancelar":
            if not args or not str(args[0]).isdigit():
                return await inte.response.send_message("Uso: mercado cancelar <id>.")
            offer_id = int(args[0])
            offer = next((row for row in data["offers"] if row["id"] == offer_id and row.get("status") == "open"), None)
            if offer is None:
                return await inte.response.send_message("Oferta nao encontrada ou ja encerrada.")
            if offer["seller_id"] != inte.user.id:
                return await inte.response.send_message("Somente o autor da oferta pode cancela-la.")
            update_active_hero_resources(inte.user.id, **{offer["give"]: offer["give_amount"]})
            offer["status"] = "cancelled"
            _save(data)
            return await inte.response.send_message(f"Oferta #{offer_id} cancelada e recursos devolvidos.")

        if action == "aceitar":
            if not args or not str(args[0]).isdigit():
                return await inte.response.send_message("Uso: mercado aceitar <id>.")
            offer_id = int(args[0])
            offer = next((row for row in data["offers"] if row["id"] == offer_id and row.get("status") == "open"), None)
            if offer is None:
                return await inte.response.send_message("Oferta nao encontrada ou indisponivel.")
            if offer["seller_id"] == inte.user.id:
                return await inte.response.send_message("Voce nao pode aceitar a propria oferta.")

            buyer = get_active_hero(inte.user.id)
            seller = get_active_hero(offer["seller_id"])
            if buyer is None or seller is None:
                return await inte.response.send_message("Um dos perfis envolvidos nao possui heroi ativo.")
            if int(buyer.get(offer["receive"], 0)) < offer["receive_amount"]:
                return await inte.response.send_message("Voce nao tem recursos suficientes para aceitar essa oferta.")

            if not update_active_hero_resources(inte.user.id, **{offer["receive"]: -offer["receive_amount"], offer["give"]: offer["give_amount"]}):
                return await inte.response.send_message("Nao foi possivel concluir a compra.")
            if not update_active_hero_resources(offer["seller_id"], **{offer["receive"]: offer["receive_amount"]}):
                update_active_hero_resources(inte.user.id, **{offer["receive"]: offer["receive_amount"], offer["give"]: -offer["give_amount"]})
                return await inte.response.send_message("A oferta ficou invalida e foi revertida.")

            offer["status"] = "accepted"
            offer["buyer_id"] = inte.user.id
            _save(data)
            return await inte.response.send_message(f"Oferta #{offer_id} aceita com sucesso.")

        await inte.response.send_message("Uso: mercado listar, mercado criar, mercado aceitar <id> ou mercado cancelar <id>.")


async def setup(bot):
    await bot.add_cog(Mercado(bot))