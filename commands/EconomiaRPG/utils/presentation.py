import discord

from commands.EconomiaRPG.items.armors import armor_dict
from commands.EconomiaRPG.items.weapons import weapon_dict
from commands.EconomiaRPG.zones.zones.embeds import zones_data


RPG_PRIMARY_COLOR = discord.Color.from_rgb(155, 89, 182)

ITEM_TYPE_LABELS = {
    1: "Arma",
    2: "Armadura",
}

ITEM_TYPE_EMOJIS = {
    1: "âš”ï¸",
    2: "ðŸ›¡ï¸",
}

RARITY_LABELS = {
    1: "Comum",
    2: "Incomum",
    3: "Raro",
    4: "Ã‰pico",
    5: "LendÃ¡rio",
}


def resolve_zone_name(zone_id: int | None) -> str:
    if isinstance(zone_id, int) and 0 <= zone_id < len(zones_data):
        zone_name = zones_data[zone_id].get("name")
        if zone_name:
            return zone_name
    return "NÃ£o definida"


def build_progress_bar(current: int, total: int, size: int = 10) -> str:
    if total <= 0:
        total = 1
    progress = min(max(current / total, 0), 1)
    filled = round(size * progress)
    return "â–ˆ" * filled + "â–‘" * (size - filled)


def add_spacer(embed: discord.Embed) -> None:
    embed.add_field(name="\u200b", value="\u200b", inline=False)


def get_item_catalog(item_type_id: int) -> dict | None:
    if item_type_id == 1:
        return weapon_dict
    if item_type_id == 2:
        return armor_dict
    return None


def build_item_instance(item_type_id: int, item_id: int, level: int = 1):
    catalog = get_item_catalog(item_type_id)
    if catalog is None or item_id not in catalog:
        return None
    return catalog[item_id](level=level)


def get_item_type_label(item_type_id: int) -> str:
    return ITEM_TYPE_LABELS.get(item_type_id, "Item")


def get_item_type_emoji(item_type_id: int) -> str:
    return ITEM_TYPE_EMOJIS.get(item_type_id, "ðŸŽ’")


def get_rarity_label(rarity: int | None) -> str:
    return RARITY_LABELS.get(rarity, "Desconhecida")


def format_item_summary(item_row: dict, equipped_item_id: int | None = None) -> str:
    item = build_item_instance(item_row["type"], item_row["item_id"], level=item_row.get("level", 1))
    if item is None:
        return "Item invÃ¡lido ou removido do catÃ¡logo."

    equipped_suffix = " | Equipado" if equipped_item_id == item_row["item_id"] else ""
    special_text = item.attack_description if item.attack_description and item.attack_description != "None" else "Sem habilidade especial"
    return (
        f"{get_item_type_emoji(item_row['type'])} **{item.name}**{equipped_suffix}\n"
        f"NÃ­vel {item_row['level']} | {get_rarity_label(getattr(item, 'rarity', None))}\n"
        f"BÃ´nus: {item.boosts}\n"
        f"Especial: {special_text}"
    )


def build_inventory_embed(display_name: str, inventory_rows: list[dict], hero_data: dict | None = None) -> discord.Embed:
    embed = discord.Embed(title=f"InventÃ¡rio de {display_name}", color=RPG_PRIMARY_COLOR)

    if not inventory_rows:
        embed.description = "Seu inventÃ¡rio estÃ¡ vazio no momento. Passe na loja, lute ou melhore itens na forja para comeÃ§ar a montar seu arsenal."
        return embed

    grouped_rows = {1: [], 2: [], 0: []}
    for row in inventory_rows:
        grouped_rows.setdefault(row.get("type", 0), []).append(row)

    for item_type_id in (1, 2, 0):
        rows = grouped_rows.get(item_type_id) or []
        if not rows:
            continue
        equipped_item_id = None
        if hero_data is not None:
            if item_type_id == 1:
                equipped_item_id = hero_data.get("weapon_id")
            elif item_type_id == 2:
                equipped_item_id = hero_data.get("armor_id")

        lines = [format_item_summary(row, equipped_item_id=equipped_item_id) for row in rows]
        embed.add_field(
            name=f"{get_item_type_emoji(item_type_id)} {get_item_type_label(item_type_id)}{'s' if item_type_id in (1, 2) else ''}",
            value="\n\n".join(lines)[:1024],
            inline=False,
        )

    return embed