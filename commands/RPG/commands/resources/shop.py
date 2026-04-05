import json
from pathlib import Path

import discord
from discord import Embed
from discord.ui import Button, View
from discord.ext import commands

from commands.RPG.utils.database import (
    active_hero_has_title,
    get_active_hero,
    grant_active_hero_title,
    set_active_hero_tomato_bag,
    update_active_hero_resources,
)
from commands.RPG.utils.progress import add_nex_spent
from commands.RPG.utils.hero_check import economy_profile_created
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR


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


def _is_titles_segment(segmento: str) -> bool:
    key = _normalize_key(segmento)
    return key in {"titulos", "títulos"}

def _find_item(loja: dict, item_key: str) -> tuple[str, str, dict] | None:
    """Resolve o item pelo nome (prefixo) ou pela chave antiga "segmento|item"."""
    raw = (item_key or "").strip()
    if not raw:
        return None

    if "|" in raw:
        seg_key, name_key = raw.split("|", 1)
        for segmento, item_name, payload in _iter_items(loja):
            if _normalize_key(segmento) == _normalize_key(seg_key) and _normalize_key(item_name) == _normalize_key(name_key):
                return segmento, item_name, payload
        return None

    name_key = _normalize_key(raw)
    matches: list[tuple[str, str, dict]] = []
    for segmento, item_name, payload in _iter_items(loja):
        if _normalize_key(item_name) == name_key:
            matches.append((segmento, item_name, payload))

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return matches[0]
    return None


def _build_shop_embed(loja: dict, *, only_segment: str | None = None) -> Embed:
    embed = Embed(title="Loja", description="Itens disponíveis:", color=RPG_PRIMARY_COLOR)
    if not loja:
        embed.add_field(
            name="Loja vazia",
            value=(
                "Não encontrei itens em `DataBase/loja.json`.\n"
                "Edite o arquivo seguindo a estrutura esperada e tente novamente."
            ),
            inline=False,
        )
        return embed

    grouped_lines: dict[str, list[str]] = {}
    for segmento, item_name, payload in _iter_items(loja):
        if only_segment is not None and _normalize_key(segmento) != _normalize_key(only_segment):
            continue
        preco = payload.get("Preço", payload.get("preco", 0))
        desc = payload.get("Descrição", payload.get("descricao", ""))
        line = f"**{item_name}**: **{preco}** 🪙"
        if desc:
            line += f"\n_{desc}_"
        grouped_lines.setdefault(str(segmento), []).append(line)

    if not grouped_lines:
        if only_segment is not None:
            embed.add_field(
                name="Seção vazia",
                value=f"Não encontrei itens na seção **{only_segment}**.",
                inline=False,
            )
        else:
            embed.add_field(
                name="Loja vazia",
                value="Não encontrei itens válidos no arquivo da loja.",
                inline=False,
            )
        return embed

    for segmento, lines in grouped_lines.items():
        embed.add_field(name=segmento, value="\n\n".join(lines)[:1024], inline=False)

    embed.add_field(
        name="Como comprar",
        value=(
            "Use `comprar <item> <quantidade>`.\n"
            "Para **Títulos**, use `comprar <título>` (quantidade sempre 1)."
        ),
        inline=False,
    )
    if only_segment is not None:
        embed.set_footer(text=f"Mostrando seção: {only_segment}")
    return embed


def _build_shop_home_embed(loja: dict) -> Embed:
    embed = Embed(
        title="Loja",
        description="Escolha uma seção nos botões abaixo para ver os itens.",
        color=RPG_PRIMARY_COLOR,
    )
    if not loja:
        embed.add_field(
            name="Loja vazia",
            value=(
                "Não encontrei itens em `DataBase/loja.json`.\n"
                "Edite o arquivo seguindo a estrutura esperada e tente novamente."
            ),
            inline=False,
        )
        return embed

    sections: list[str] = []
    for segmento, items in loja.items():
        if not isinstance(items, dict):
            continue
        item_count = sum(1 for _, payload in items.items() if isinstance(payload, dict))
        sections.append(f"• **{segmento}** ({item_count})")

    if sections:
        embed.add_field(name="Seções", value="\n".join(sections)[:1024], inline=False)

    embed.add_field(
        name="Como comprar",
        value=(
            "Depois de abrir a seção, use `comprar <item> <quantidade>`.\n"
            "Para **Títulos**, use `comprar <título>` (quantidade sempre 1)."
        ),
        inline=False,
    )
    return embed


class _SectionButton(Button):
    def __init__(self, *, label: str, owner_user_id: int, loja: dict):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self._segment_label = label
        self._owner_user_id = owner_user_id
        self._loja = loja

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self._owner_user_id:
            await interaction.response.send_message(
                "Apenas quem abriu esta loja pode trocar de seção.",
                ephemeral=True,
            )
            return
        embed = _build_shop_embed(self._loja, only_segment=self._segment_label)
        await interaction.response.edit_message(embed=embed, view=self.view)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='loja', aliases=["shop"])
    async def shop(self, ctx):
        """Abre a loja."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)

        loja = _load_loja()
        embed = _build_shop_home_embed(loja)

        view = View(timeout=180)
        # 1 botão por seção (máx. 25 botões por mensagem no Discord)
        for segmento in list(loja.keys())[:25]:
            if not isinstance(segmento, str):
                segmento = str(segmento)
            view.add_item(_SectionButton(label=segmento, owner_user_id=inte.user.id, loja=loja))

        await inte.response.send_message(embed=embed, view=view)
        
        
    @commands.command(name="comprar", aliases=["buy"], help="Compra um item da loja.")
    async def buy(self, ctx, *, args: str):
        """Compra recursos na loja."""
        inte = CommandContextAdapter(ctx)
        await economy_profile_created(inte)
        if get_active_hero(inte.user.id) is None:
            return await inte.response.send_message("Seu perfil economico foi criado, mas voce precisa criar um heroi antes de comprar recursos para o inventario dele.")

        raw = (args or "").strip()
        if not raw:
            return await inte.response.send_message("Uso: comprar <item> <quantidade>.")

        parts = raw.split()
        amount = 1
        if parts and parts[-1].isdigit():
            amount = int(parts[-1])
            parts = parts[:-1]

        item = " ".join(parts).strip()
        if not item:
            return await inte.response.send_message("Informe o item. Ex: comprar Madeira 2")

        if amount <= 0:
            await inte.response.send_message(f"A quantidade {amount} nao e suportada. O minimo e 1.")
            return

        loja = _load_loja()
        resolved = _find_item(loja, item)
        if not resolved:
            await inte.response.send_message("Item inválido ou não encontrado na loja.")
            return

        segmento, item_name, payload = resolved
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
        user_nex = data["nex"]

        is_title = _is_titles_segment(segmento) or _normalize_key(str(payload.get("type", ""))) == "title"
        if is_title and amount != 1:
            await inte.response.send_message("Para comprar títulos, a quantidade deve ser 1. Ex: `comprar O pensador`")
            return

        price = unit_price * amount
        if price > user_nex:
            await inte.response.send_message(f"Voce nao tem nex suficiente. Saldo atual: {user_nex} nex.")
            return

        if is_title:
            if active_hero_has_title(inte.user.id, item_name):
                await inte.response.send_message("Você já possui esse título. Use `titulo usar <nome>` para equipar.")
                return

            paid = update_active_hero_resources(inte.user.id, nex=-price)
            if not paid:
                await inte.response.send_message("Saldo insuficiente.")
                return

            granted = grant_active_hero_title(inte.user.id, item_name, set_active=True)
            if not granted:
                update_active_hero_resources(inte.user.id, nex=price)
                await inte.response.send_message("Falha ao registrar o título. Sua compra foi estornada.")
                return

            add_nex_spent(inte.user.id, price)
            updated_data = get_active_hero(inte.user.id)
            await inte.response.send_message(
                f"Compra concluída: título **{item_name}** por **{price}** nex. "
                f"Carteira atual: {updated_data['nex']} nex."
            )
            return

        if _normalize_key(str(payload.get("resource", payload.get("Recurso", "")))) == "tomato":
            if "capacity" in payload:
                try:
                    new_capacity = int(payload.get("capacity"))
                except (TypeError, ValueError):
                    await inte.response.send_message("A capacidade desta bolsa está inválida no loja.json.")
                    return

                current_tomatoes = int(data.get("tomato", 0))
                if current_tomatoes > new_capacity:
                    await inte.response.send_message(
                        f"Voce esta com {current_tomatoes} tomates e a nova bolsa suporta apenas {new_capacity}. Use tomates antes de trocar de bolsa."
                    )
                    return

                paid = update_active_hero_resources(inte.user.id, nex=-price)
                if not paid:
                    await inte.response.send_message("Saldo insuficiente.")
                    return

                equipped = set_active_hero_tomato_bag(inte.user.id, item_name, new_capacity)
                if not equipped:
                    update_active_hero_resources(inte.user.id, nex=price)
                    await inte.response.send_message("Falha ao equipar a nova bolsa. Sua compra foi estornada.")
                    return

                add_nex_spent(inte.user.id, price)
                updated_data = get_active_hero(inte.user.id)
                await inte.response.send_message(
                    f"Compra concluida: **{item_name}** equipada por **{price}** nex. "
                    f"Bolsa atual: {updated_data['tomato_bag']} ({updated_data['tomato_capacity']} tomates). "
                    f"Saldo de tomates: {updated_data['tomato']}. Carteira atual: {updated_data['nex']} nex."
                )
                return

            if "quantity" in payload:
                try:
                    tomato_amount = int(payload.get("quantity")) * amount
                except (TypeError, ValueError):
                    await inte.response.send_message("A quantidade de tomates deste item está inválida no loja.json.")
                    return

                updated = update_active_hero_resources(inte.user.id, nex=-price, tomato=tomato_amount)
                if not updated:
                    current_tomatoes = int(data.get("tomato", 0))
                    current_capacity = int(data.get("tomato_capacity", current_tomatoes))
                    if current_tomatoes + tomato_amount > current_capacity:
                        await inte.response.send_message(
                            f"Sua bolsa comporta ate {current_capacity} tomates e voce esta com {current_tomatoes}."
                        )
                    else:
                        await inte.response.send_message("A compra foi bloqueada para evitar saldo negativo ou recurso inválido.")
                    return

                add_nex_spent(inte.user.id, price)
                updated_data = get_active_hero(inte.user.id)
                await inte.response.send_message(
                    f"Compra concluida: {amount}x {item_name} por {price} nex. "
                    f"Carteira atual: {updated_data['nex']} nex. "
                    f"Tomates: {updated_data['tomato']}/{updated_data['tomato_capacity']}."
                )
                return

        # Mantém compatibilidade: se o JSON tiver um campo de recurso, use-o.
        # Caso não tenha, tenta mapear pelo nome do item (madeira/ferro etc.).
        resource_key = payload.get("resource") or payload.get("Recurso")
        transaction_ok = False
        resource_label = None
        if isinstance(resource_key, str) and resource_key.strip():
            resource_label = resource_key.strip()
            kwargs = {resource_label: amount, "nex": -price}
            transaction_ok = update_active_hero_resources(inte.user.id, **kwargs)
        else:
            name_norm = _normalize_key(item_name)
            if "madeira" in name_norm or name_norm == "wood":
                resource_label = "wood"
                transaction_ok = update_active_hero_resources(inte.user.id, nex=-price, wood=amount)
            elif "ferro" in name_norm or name_norm == "iron":
                resource_label = "iron"
                transaction_ok = update_active_hero_resources(inte.user.id, nex=-price, iron=amount)
            else:
                await inte.response.send_message(
                    "Este item não possui mapeamento de recurso. Adicione `resource` no loja.json (ex: 'wood', 'iron', etc.)."
                )
                return

        if not transaction_ok:
            await inte.response.send_message("A compra foi bloqueada para evitar saldo negativo ou recurso inválido.")
            return
        
        add_nex_spent(inte.user.id, price)
        updated_data = get_active_hero(inte.user.id)
        resource_balance = updated_data.get(resource_label, "--") if isinstance(updated_data, dict) else "--"
        
        await inte.response.send_message(
            f"Compra concluída: {amount}x {item_name} por {price} nex. "
            f"Carteira atual: {updated_data['nex']} nex. Saldo de {resource_label}: {resource_balance}."
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
