import json
from pathlib import Path

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import get_active_hero, update_active_hero_resources
from commands.EconomiaRPG.utils.hero_check import economy_profile_created
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


DB_PATH = Path("DataBase") / "rpg_bounties.json"


def _load() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"next_id": 1, "bounties": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {"next_id": 1, "bounties": []}
    data.setdefault("next_id", 1)
    data.setdefault("bounties", [])
    return data


def _save(data: dict) -> None:
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


class Recompensa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="recompensa", aliases=["bounty"])
    async def recompensa(self, ctx, acao: str | None = None, *args):
        """Sistema simples de recompensas entre jogadores."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Voce precisa de um heroi ativo para usar recompensas.")

        action = (acao or "listar").strip().lower()
        data = _load()

        if action in {"listar", "list"}:
            open_bounties = [row for row in data["bounties"] if row.get("status") == "open"][:10]
            embed = discord.Embed(title="Quadro de Recompensas", color=RPG_PRIMARY_COLOR)
            if not open_bounties:
                embed.description = "Nao ha recompensas abertas no momento."
            else:
                lines = []
                for row in open_bounties:
                    lines.append(
                        f"**#{row['id']}** - Alvo: <@{row['target_id']}>\n"
                        f"Valor: {row['amount']} nex\n"
                        f"Motivo: {row.get('reason') or 'Sem motivo informado'}"
                    )
                embed.description = "\n\n".join(lines)
            embed.set_footer(text="Use recompensa criar @alvo <valor> [motivo], recompensa cancelar <id> ou recompensa concluir <id> @vencedor.")
            return await inte.response.send_message(embed=embed)

        if action == "criar":
            if len(args) < 2 or not ctx.message.mentions:
                return await inte.response.send_message("Uso: recompensa criar @alvo <valor> [motivo].")
            alvo = ctx.message.mentions[0]
            amount_token = next((token for token in args if str(token).isdigit()), None)
            if amount_token is None:
                return await inte.response.send_message("Informe um valor numerico para a recompensa.")
            valor = int(amount_token)
            motivo_tokens = list(args)
            mention_tokens = {alvo.mention, f"<@{alvo.id}>", f"<@!{alvo.id}>"}
            motivo = " ".join(
                token for token in motivo_tokens
                if token not in mention_tokens and token != amount_token
            ).strip() or None
            if alvo.bot or alvo.id == inte.user.id:
                return await inte.response.send_message("Escolha um alvo valido para a recompensa.")
            if valor <= 0:
                return await inte.response.send_message("Informe um valor positivo para a recompensa.")
            if not update_active_hero_resources(inte.user.id, nex=-valor):
                return await inte.response.send_message("Voce nao tem nex suficiente na carteira para abrir essa recompensa.")

            bounty = {
                "id": data["next_id"],
                "author_id": inte.user.id,
                "target_id": alvo.id,
                "amount": valor,
                "reason": motivo,
                "status": "open",
            }
            data["next_id"] += 1
            data["bounties"].append(bounty)
            _save(data)
            return await inte.response.send_message(f"Recompensa #{bounty['id']} criada contra {alvo.mention} por {valor} nex.")

        if action == "cancelar":
            if not args or not str(args[0]).isdigit():
                return await inte.response.send_message("Uso: recompensa cancelar <id>.")
            identifier = int(args[0])
            bounty = next((row for row in data["bounties"] if row["id"] == identifier and row.get("status") == "open"), None)
            if bounty is None:
                return await inte.response.send_message("Recompensa nao encontrada.")
            if bounty["author_id"] != inte.user.id:
                return await inte.response.send_message("Somente o criador pode cancelar essa recompensa.")
            update_active_hero_resources(inte.user.id, nex=bounty["amount"])
            bounty["status"] = "cancelled"
            _save(data)
            return await inte.response.send_message(f"Recompensa #{identifier} cancelada e valor devolvido.")

        if action == "concluir":
            if len(args) < 2 or not str(args[0]).isdigit() or not ctx.message.mentions:
                return await inte.response.send_message("Uso: recompensa concluir <id> @vencedor")
            bounty_id = int(args[0])
            vencedor = ctx.message.mentions[0]
            bounty = next((row for row in data["bounties"] if row["id"] == bounty_id and row.get("status") == "open"), None)
            if bounty is None:
                return await inte.response.send_message("Recompensa nao encontrada.")
            if bounty["author_id"] != inte.user.id and not ctx.author.guild_permissions.manage_guild:
                return await inte.response.send_message("Somente o criador da recompensa ou a staff podem conclui-la.")
            if get_active_hero(vencedor.id) is None:
                return await inte.response.send_message("O vencedor precisa ter um heroi ativo para receber a recompensa.")
            update_active_hero_resources(vencedor.id, nex=bounty["amount"])
            bounty["status"] = "claimed"
            bounty["winner_id"] = vencedor.id
            _save(data)
            return await inte.response.send_message(
                f"Recompensa #{bounty_id} concluida. {vencedor.mention} recebeu {bounty['amount']} nex."
            )

        await inte.response.send_message("Uso: recompensa listar, recompensa criar @alvo <valor> [motivo], recompensa cancelar <id> ou recompensa concluir <id> @vencedor.")


async def setup(bot):
    await bot.add_cog(Recompensa(bot))