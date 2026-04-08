from commands.EconomiaRPG.utils.database import _normalize_state


def test_normalize_state_converts_gold_to_nex_and_preserves_bank() -> None:
    state = {
        "hero": [{"id": 1, "user_id": 99, "gold": 120, "bank": "35", "active": 1, "class": "mage", "level": 1, "xp": 0, "wood": 0, "iron": 0, "runes": 0, "weapon_id": None, "armor_id": None, "zone_id": 0}],
        "inventory": [],
        "advancements": [],
        "dex": [],
        "quest_log": {},
        "daily_claims": {},
        "meta": {"next_ids": {}},
    }

    normalized = _normalize_state(state)
    hero = normalized["hero"][0]

    assert hero["nex"] == 120
    assert "gold" not in hero
    assert hero["bank"] == 35
    assert normalized["meta"]["next_ids"]["hero"] == 2