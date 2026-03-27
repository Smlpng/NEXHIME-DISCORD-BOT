import json
from pathlib import Path

import discord
from discord import app_commands, Embed
from discord.ui import View
from discord.ext import commands

from commands.RPG.utils.database import get_active_hero, update_active_hero_resources
from commands.RPG.utils.progress import add_gold_spent
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.command_adapter import CommandContextAdapter


LOJA_FILE = Path("DataBase") / "loja.json"


def _load_loja() -> dict:
    """Carrega a loja do JSON.

    Estrutura esperada:
    {
      "segmento": {
        "Nome do item": {"Preço": 0, "Descrição": "", ...campos extras}
      }
    }
    """
    try:
        with LOJA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _iter_items(loja: dict):
    for segmento, items in loja.items():
        if not isinstance(items, dict):
            continue
        for item_name, payload in items.items():
            if not isinstance(payload, dict):
                continue
            yield str(segmento), str(item_name), payload


def _normalize_key(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _choices_from_loja(loja: dict) -> list[app_commands.Choice[str]]:
    choices: list[app_commands.Choice[str]] = []
    for segmento, item_name, _payload in _iter_items(loja):
        # value precisa ser curto e estável; usamos "segmento|item"
        value = f"{_normalize_key(segmento)}|{_normalize_key(item_name)}"
        label = item_name
        # limite do Discord: 100 choices por comando
        if len(choices) >= 100:
            break
        choices.append(app_commands.Choice(name=label, value=value))
    return choices


def _find_item(loja: dict, item_key: str) -> tuple[str, str, dict] | None:
    """Resolve o item pelo value gerado em _choices_from_loja."""
    if "|" not in item_key:
        return None
    seg_key, name_key = item_key.split("|", 1)
    for segmento, item_name, payload in _iter_items(loja):
        if _normalize_key(segmento) == seg_key and _normalize_key(item_name) == name_key:
            return segmento, item_name, payload
    return None

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='loja', aliases=["shop"])
    async def shop(self, ctx):
        """Abre a loja."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        loja = _load_loja()
        embed = Embed(title="Loja", description="Itens disponíveis:", color=0x3498DB)

        if not loja:
            embed.add_field(
                name="Loja vazia",
                value=(
                    "Não encontrei itens em `DataBase/loja.json`.\n"
                    "Edite o arquivo seguindo a estrutura esperada e tente novamente."
                ),
                inline=False,
            )
        else:
            # Mostra por segmento sem quebrar se houver campos extras
            for segmento, item_name, payload in _iter_items(loja):
                preco = payload.get("Preço", payload.get("preco", 0))
                desc = payload.get("Descrição", payload.get("descricao", ""))
                line = f"🪙 **{preco}** → **{item_name}**"
                if desc:
                    line += f"\n_{desc}_"
                embed.add_field(name=str(segmento), value=line, inline=False)

            embed.add_field(
                name="Como comprar",
                value="Use `/comprar <item> <quantidade>` (ou `comprar` via prefixo).",
                inline=False,
            )
        
        view = View()
        await inte.response.send_message(embed=embed, view=view)
        
        
    @commands.hybrid_command(name="comprar", aliases=["buy"], description="Compra um item da loja.")
    async def buy(self, ctx, item: str, amount: int):
        """Compra recursos na loja."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce precisa criar um heroi antes de comprar recursos para o inventario dele.")
        
        if amount <= 0:
            await inte.response.send_message(f"A quantidade {amount} nao e suportada. O minimo e 1.")
            return
        
        
        loja = _load_loja()
        resolved = _find_item(loja, item)
        if not resolved:
            await inte.response.send_message("Item inválido ou não encontrado na loja.")
            return

        _segmento, item_name, payload = resolved
        unit_price = payload.get("Preço", payload.get("preco", None))
        if unit_price is None:
            await inte.response.send_message("Este item não possui o campo 'Preço' no loja.json.")
            return
        try:
            unit_price = int(unit_price)
        except (TypeError, ValueError):
            await inte.response.send_message("O campo 'Preço' deste item está inválido no loja.json.")
            return

        data = get_active_hero(inte.user.id)
        user_gold = data["gold"]

        price = unit_price * amount
        if price > user_gold:
            await inte.response.send_message("Voce nao tem ouro suficiente.")
            return

        # Mantém compatibilidade: se o JSON tiver um campo de recurso, use-o.
        # Caso não tenha, tenta mapear pelo nome do item (madeira/ferro etc.).
        resource_key = payload.get("resource") or payload.get("Recurso")
        if isinstance(resource_key, str) and resource_key.strip():
            kwargs = {resource_key.strip(): amount, "gold": -price}
            update_active_hero_resources(inte.user.id, **kwargs)
        else:
            name_norm = _normalize_key(item_name)
            if "madeira" in name_norm or name_norm == "wood":
                update_active_hero_resources(inte.user.id, gold=-price, wood=amount)
            elif "ferro" in name_norm or name_norm == "iron":
                update_active_hero_resources(inte.user.id, gold=-price, iron=amount)
            else:
                await inte.response.send_message(
                    "Este item não possui mapeamento de recurso. Adicione `resource` no loja.json (ex: 'wood', 'iron', etc.)."
                )
                return
        
        add_gold_spent(inte.user.id, price)
        
        await inte.response.send_message(f"{amount} de {item_name} foi comprado com sucesso.")


    @buy.autocomplete("item")
    async def buy_item_autocomplete(self, interaction: discord.Interaction, current: str):
        # Autocomplete (para slash): filtra por texto e limita a 25.
        loja = _load_loja()
        all_choices = _choices_from_loja(loja)
        if not current:
            return all_choices[:25]
        cur = _normalize_key(current)
        filtered = [c for c in all_choices if cur in _normalize_key(c.name)]
        return filtered[:25]
        

async def setup(bot):
    await bot.add_cog(Shop(bot))
