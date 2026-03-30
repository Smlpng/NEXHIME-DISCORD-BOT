import json
import os
from pathlib import Path
from threading import RLock


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_FILE = Path(os.getenv("RPG50_DATA_FILE", ROOT_DIR / "DataBase" / "players.json"))
LOCK = RLock()

HERO_FIELDS = [
	"id",
	"user_id",
	"race",
	"tribe",
	"class",
	"level",
	"xp",
	"nex",
	"wood",
	"iron",
	"runes",
	"weapon_id",
	"armor_id",
	"zone_id",
	"active",
]
INVENTORY_FIELDS = ["id", "hero_id", "type", "item_id", "level"]
ADVANCEMENT_FIELDS = ["hero_id", "kills", "upgrades", "nex_spent"]
DEX_FIELDS = ["id", "hero_id", "enemy_id"]

ITEM_TYPE_NAME_BY_ID = {
	1: "weapon",
	2: "armor",
}
ITEM_TYPE_ID_BY_NAME = {name: item_id for item_id, name in ITEM_TYPE_NAME_BY_ID.items()}

ENEMIES = [
	{"id": 1, "name": "Totem do Bando", "zone": 0},
	{"id": 2, "name": "Gosma de Banana", "zone": 2},
	{"id": 3, "name": "Símio de Magma", "zone": 2},
	{"id": 4, "name": "Macaco Ossudo", "zone": 2},
	{"id": 5, "name": "Sagui Saqueador", "zone": 1},
	{"id": 6, "name": "Mico Vigia", "zone": 1},
	{"id": 7, "name": "Larva da Copa", "zone": 1},
	{"id": 8, "name": "Sombra do Galho", "zone": 2},
	{"id": 9, "name": "Rato do Celeiro de Banana", "zone": 2},
	{"id": 10, "name": "Bugio de Presas", "zone": 3},
	{"id": 11, "name": "Gorila Saqueador", "zone": 3},
	{"id": 12, "name": "Urso das Bananeiras", "zone": 3},
	{"id": 13, "name": "Jiboia do Cipó", "zone": 3},
	{"id": 14, "name": "Ancestral Enfaixado", "zone": 4},
	{"id": 15, "name": "Escorpiao da Casca", "zone": 4},
	{"id": 16, "name": "Guardiao de Areia do Cacho", "zone": 4},
	{"id": 17, "name": "Catadores do Sol", "zone": 4},
	{"id": 18, "name": "Sapo do Bananal Podre", "zone": 5},
	{"id": 19, "name": "Rei do Poleiro de Banana", "zone": 1},
	{"id": 20, "name": "Mutante do Pantano Símio", "zone": 5},
	{"id": 21, "name": "Guardiao do Dossel", "zone": 3},
	{"id": 22, "name": "Ancestral das Dunas", "zone": 4},
	{"id": 23, "name": "Soldados de Lama do Bando Caido", "zone": 5},
	{"id": 24, "name": "Xama da Lua Banana", "zone": 5},
]
ENEMIES_BY_ID = {enemy["id"]: enemy for enemy in ENEMIES}


def _default_state() -> dict:
	return {
		"hero": [],
		"inventory": [],
		"advancements": [],
		"dex": [],
		"quest_log": {},
		"bank": {},
		"daily_claims": {},
		"meta": {
			"next_ids": {
				"hero": 1,
				"inventory": 1,
				"dex": 1,
			}
		},
	}


def _table_max_id(rows: list[dict], field_name: str = "id") -> int:
	return max((row[field_name] for row in rows), default=0)


def _normalize_state(state: dict | None) -> dict:
	normalized = _default_state()
	if state:
		normalized.update({key: value for key, value in state.items() if key in normalized})
		meta = state.get("meta", {}) if isinstance(state, dict) else {}
		if not isinstance(normalized.get("bank"), dict):
			normalized["bank"] = {}
		if not isinstance(normalized.get("daily_claims"), dict):
			normalized["daily_claims"] = {}
		if not isinstance(normalized.get("quest_log"), dict):
			normalized["quest_log"] = {}
		normalized["meta"] = normalized.get("meta", {})
		normalized["meta"]["next_ids"] = normalized["meta"].get("next_ids", {})
		normalized["meta"]["next_ids"].update(meta.get("next_ids", {}))

	for hero in normalized["hero"]:
		if "nex" not in hero and "gold" in hero:
			hero["nex"] = hero.pop("gold")
		else:
			hero.setdefault("nex", 0)
		hero.pop("gold", None)
		hero.setdefault("race", None)
		hero.setdefault("tribe", None)

	for advancement in normalized["advancements"]:
		if "nex_spent" not in advancement and "gold_spent" in advancement:
			advancement["nex_spent"] = advancement.pop("gold_spent")
		else:
			advancement.setdefault("nex_spent", 0)
		advancement.pop("gold_spent", None)

	for hero_id, quest_data in list(normalized["quest_log"].items()):
		if not isinstance(quest_data, dict):
			normalized["quest_log"][hero_id] = {"active": {}, "completed": []}
			continue
		quest_data.setdefault("active", {})
		quest_data.setdefault("completed", [])
		for active_data in quest_data["active"].values():
			snapshot = active_data.get("snapshot")
			if not isinstance(snapshot, dict):
				continue
			if "nex_spent" not in snapshot and "gold_spent" in snapshot:
				snapshot["nex_spent"] = snapshot.pop("gold_spent")
			snapshot.pop("gold_spent", None)

	normalized["meta"]["next_ids"]["hero"] = max(
		normalized["meta"]["next_ids"].get("hero", 1),
		_table_max_id(normalized["hero"]) + 1,
	)
	normalized["meta"]["next_ids"]["inventory"] = max(
		normalized["meta"]["next_ids"].get("inventory", 1),
		_table_max_id(normalized["inventory"]) + 1,
	)
	normalized["meta"]["next_ids"]["dex"] = max(
		normalized["meta"]["next_ids"].get("dex", 1),
		_table_max_id(normalized["dex"]) + 1,
	)
	return normalized


def _write_state_unlocked(state: dict) -> None:
	DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
	temp_file = DATA_FILE.with_suffix(".tmp")
	temp_file.write_text(json.dumps(_normalize_state(state), indent=2), encoding="utf-8")
	temp_file.replace(DATA_FILE)


def _read_state_unlocked() -> dict:
	if not DATA_FILE.exists():
		state = _default_state()
		_write_state_unlocked(state)
		return state

	try:
		state = json.loads(DATA_FILE.read_text(encoding="utf-8"))
	except (json.JSONDecodeError, OSError):
		state = _default_state()
		_write_state_unlocked(state)
		return state

	return _normalize_state(state)


def _load_state() -> dict:
	with LOCK:
		return _read_state_unlocked()


def _save_state(state: dict) -> None:
	with LOCK:
		_write_state_unlocked(state)


def _next_id(state: dict, key: str) -> int:
	next_id = state["meta"]["next_ids"][key]
	state["meta"]["next_ids"][key] += 1
	return next_id


def _get_active_hero_row(state: dict, user_id: int) -> dict | None:
	for hero in state["hero"]:
		if hero["user_id"] == user_id and hero["active"] == 1:
			return hero
	return None


def _get_hero_row_by_id(state: dict, hero_id: int) -> dict | None:
	for hero in state["hero"]:
		if hero["id"] == hero_id:
			return hero
	return None


def _get_advancement_row(state: dict, hero_id: int) -> dict | None:
	for advancement in state["advancements"]:
		if advancement["hero_id"] == hero_id:
			return advancement
	return None


def _get_inventory_rows(state: dict, hero_id: int) -> list[dict]:
	return [item for item in state["inventory"] if item["hero_id"] == hero_id]


def _get_inventory_row(state: dict, hero_id: int, item_id: int, item_type_id: int) -> dict | None:
	matches = [
		item for item in state["inventory"]
		if item["hero_id"] == hero_id and item["item_id"] == item_id and item["type"] == item_type_id
	]
	if not matches:
		return None
	return max(matches, key=lambda row: (row.get("level", 0), row.get("id", 0)))


def _apply_resource_delta(hero: dict, nex: int = 0, wood: int = 0, iron: int = 0, runes: int = 0) -> bool:
	updated_values = {
		"nex": hero["nex"] + nex,
		"wood": hero["wood"] + wood,
		"iron": hero["iron"] + iron,
		"runes": hero["runes"] + runes,
	}
	if any(value < 0 for value in updated_values.values()):
		return False
	hero.update(updated_values)
	return True


def _get_equipped_level(state: dict, hero: dict, item_type_id: int, item_id: int | None):
	if item_id is None:
		return None
	item = _get_inventory_row(state, hero["id"], item_id, item_type_id)
	return None if item is None else item["level"]


def _build_clean_hero_row(state: dict, hero: dict) -> dict:
	return {
		"id": hero["id"],
		"user_id": hero["user_id"],
		"active": hero["active"],
		"race": hero.get("race"),
		"tribe": hero.get("tribe"),
		"class": hero["class"],
		"level": hero["level"],
		"xp": hero["xp"],
		"nex": hero["nex"],
		"wood": hero["wood"],
		"iron": hero["iron"],
		"runes": hero["runes"],
		"weapon_id": hero["weapon_id"],
		"weapon_level": _get_equipped_level(state, hero, 1, hero["weapon_id"]),
		"armor_id": hero["armor_id"],
		"armor_level": _get_equipped_level(state, hero, 2, hero["armor_id"]),
		"zone_id": hero["zone_id"],
	}


def _build_clean_inventory_rows(state: dict, hero_id: int | None = None) -> list[dict]:
	rows = []
	for item in state["inventory"]:
		if hero_id is not None and item["hero_id"] != hero_id:
			continue
		rows.append(
			{
				"hero_id": item["hero_id"],
				"type": ITEM_TYPE_NAME_BY_ID[item["type"]],
				"item_id": item["item_id"],
				"level": item["level"],
			}
		)
	return rows


def _build_hero(user_id: int, class_id: int | None, active: int, hero_id: int) -> dict:
	return {
		"id": hero_id,
		"user_id": user_id,
		"race": None,
		"tribe": None,
		"class": class_id,
		"level": 1,
		"xp": 0,
		"nex": 0,
		"wood": 0,
		"iron": 0,
		"runes": 0,
		"weapon_id": None,
		"armor_id": None,
		"zone_id": 1,
		"active": active,
	}


def _build_advancement(hero_id: int) -> dict:
	return {
		"hero_id": hero_id,
		"kills": 0,
		"upgrades": 0,
		"nex_spent": 0,
	}


def reset_data() -> dict:
	state = _default_state()
	_save_state(state)
	return state


def get_active_hero(user_id: int) -> dict | None:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	return None if hero is None else dict(hero)


def ensure_profile(user_id: int) -> None:
	with LOCK:
		state = _read_state_unlocked()
		state.setdefault("bank", {})
		updated = False
		if str(user_id) not in state["bank"]:
			state["bank"][str(user_id)] = 0
			updated = True
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			hero_id = _next_id(state, "hero")
			hero = _build_hero(user_id, None, 1, hero_id)
			state["hero"].append(hero)
			state["advancements"].append(_build_advancement(hero_id))
			updated = True
		if updated:
			_write_state_unlocked(state)


def get_active_hero_id(user_id: int) -> int | None:
	hero = get_active_hero(user_id)
	return None if hero is None else hero["id"]


def has_active_hero(user_id: int) -> bool:
	return get_active_hero_id(user_id) is not None


def list_user_heroes(user_id: int) -> list[dict]:
	state = _load_state()
	return [dict(hero) for hero in state["hero"] if hero["user_id"] == user_id]


def has_any_hero(user_id: int) -> bool:
	return len(list_user_heroes(user_id)) > 0


def has_selected_class(user_id: int) -> bool:
	hero = get_active_hero(user_id)
	return hero is not None and hero["class"] is not None


def list_user_hero_classes(user_id: int) -> list[int]:
	return sorted({hero["class"] for hero in list_user_heroes(user_id) if hero["class"] is not None})


def create_hero(user_id: int, class_id: int, active: bool) -> dict:
	with LOCK:
		state = _read_state_unlocked()
		for hero in state["hero"]:
			if hero["user_id"] == user_id:
				return dict(hero)
		hero_id = _next_id(state, "hero")
		hero = _build_hero(user_id, class_id, 1 if active else 0, hero_id)
		state["hero"].append(hero)
		state["advancements"].append(_build_advancement(hero_id))
		_write_state_unlocked(state)
		return dict(hero)


def set_active_hero_class(user_id: int, class_id: int) -> dict | None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return None
		hero["class"] = int(class_id)
		_write_state_unlocked(state)
		return dict(hero)


def clear_active_hero_class(user_id: int) -> dict | None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return None
		hero["class"] = None
		_write_state_unlocked(state)
		return dict(hero)


def set_active_hero_race(user_id: int, race_name: str) -> dict | None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return None
		hero["race"] = race_name
		_write_state_unlocked(state)
		return dict(hero)


def set_active_hero_tribe(user_id: int, tribe_name: str) -> dict | None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return None
		hero["tribe"] = tribe_name
		_write_state_unlocked(state)
		return dict(hero)


def set_active_hero(user_id: int, hero_id: int) -> None:
	with LOCK:
		state = _read_state_unlocked()
		for hero in state["hero"]:
			if hero["user_id"] == user_id:
				hero["active"] = 1 if hero["id"] == int(hero_id) else 0
		_write_state_unlocked(state)


def get_active_zone_id(user_id: int) -> int | None:
	hero = get_active_hero(user_id)
	return None if hero is None else hero["zone_id"]


def set_active_zone_id(user_id: int, zone_id: int) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is not None:
			hero["zone_id"] = zone_id
			_write_state_unlocked(state)


def get_hero_resources_by_id(hero_id: int) -> dict | None:
	state = _load_state()
	hero = _get_hero_row_by_id(state, hero_id)
	if hero is None:
		return None
	return {key: hero[key] for key in ("nex", "wood", "iron", "runes")}


def get_active_hero_clean(user_id: int) -> dict | None:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	return None if hero is None else _build_clean_hero_row(state, hero)


def get_active_hero_level_and_xp(user_id: int) -> dict | None:
	hero = get_active_hero(user_id)
	if hero is None:
		return None
	return {"level": hero["level"], "xp": hero["xp"]}


def list_active_inventory(user_id: int, item_type_id: int | None = None) -> list[dict]:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return []
	rows = sorted(_get_inventory_rows(state, hero["id"]), key=lambda item: item["level"], reverse=True)
	if item_type_id is not None:
		rows = [item for item in rows if item["type"] == item_type_id]
	return [dict(item) for item in rows]


def active_hero_has_item(user_id: int, item_id: int, item_type_name: str) -> bool:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return False
	item_type_id = ITEM_TYPE_ID_BY_NAME[item_type_name]
	return _get_inventory_row(state, hero["id"], item_id, item_type_id) is not None


def add_item_to_active_hero(user_id: int, item_type_name: str, item_id: int) -> dict | None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return None
		item = {
			"id": _next_id(state, "inventory"),
			"hero_id": hero["id"],
			"type": ITEM_TYPE_ID_BY_NAME[item_type_name],
			"item_id": item_id,
			"level": 1,
		}
		state["inventory"].append(item)
		_write_state_unlocked(state)
		return dict(item)


def list_active_clean_inventory(user_id: int, item_type_name: str | None = None, item_id: int | None = None) -> list[dict]:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return []
	rows = _build_clean_inventory_rows(state, hero["id"])
	if item_type_name is not None:
		rows = [row for row in rows if row["type"] == item_type_name]
	if item_id is not None:
		rows = [row for row in rows if row["item_id"] == item_id]
	return rows


def equip_item(user_id: int, item_type_name: str, item_id: int) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return
		field_name = "weapon_id" if item_type_name == "weapon" else "armor_id"
		hero[field_name] = int(item_id)
		_write_state_unlocked(state)


def spend_hero_resources(hero_id: int, nex: int = 0, wood: int = 0, iron: int = 0, runes: int = 0) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_hero_row_by_id(state, hero_id)
		if hero is None:
			return
		if _apply_resource_delta(hero, nex=-nex, wood=-wood, iron=-iron, runes=-runes):
			_write_state_unlocked(state)


def update_active_hero_resources(user_id: int, nex: int = 0, wood: int = 0, iron: int = 0, runes: int = 0) -> bool:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return False
		if not _apply_resource_delta(hero, nex=nex, wood=wood, iron=iron, runes=runes):
			return False
		_write_state_unlocked(state)
		return True


def get_bank_balance(user_id: int) -> int:
	state = _load_state()
	return int(state.get("bank", {}).get(str(user_id), 0))


def deposit_nex_to_bank(user_id: int, amount: int) -> bool:
	if amount <= 0:
		return False
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None or not _apply_resource_delta(hero, nex=-amount):
			return False
		state.setdefault("bank", {})
		state["bank"][str(user_id)] = int(state["bank"].get(str(user_id), 0)) + amount
		_write_state_unlocked(state)
		return True


def withdraw_nex_from_bank(user_id: int, amount: int) -> bool:
	if amount <= 0:
		return False
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		balance = int(state.get("bank", {}).get(str(user_id), 0))
		if hero is None or balance < amount or not _apply_resource_delta(hero, nex=amount):
			return False
		state["bank"][str(user_id)] = balance - amount
		_write_state_unlocked(state)
		return True


def transfer_bank_nex(sender_user_id: int, target_user_id: int, amount: int) -> bool:
	if amount <= 0 or sender_user_id == target_user_id:
		return False
	with LOCK:
		state = _read_state_unlocked()
		bank_state = state.setdefault("bank", {})
		sender_balance = int(bank_state.get(str(sender_user_id), 0))
		if sender_balance < amount:
			return False
		bank_state[str(sender_user_id)] = sender_balance - amount
		bank_state[str(target_user_id)] = int(bank_state.get(str(target_user_id), 0)) + amount
		_write_state_unlocked(state)
		return True


def claim_daily_nex(user_id: int, amount: int, cooldown_seconds: int, now_ts: float) -> tuple[bool, int]:
	if amount <= 0 or cooldown_seconds <= 0:
		return False, 0
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return False, 0
		daily_claims = state.setdefault("daily_claims", {})
		last_claim = float(daily_claims.get(str(user_id), 0))
		available_at = last_claim + cooldown_seconds
		if available_at > now_ts:
			return False, int(available_at - now_ts)
		if not _apply_resource_delta(hero, nex=amount):
			return False, 0
		daily_claims[str(user_id)] = now_ts
		_write_state_unlocked(state)
		return True, 0


def get_daily_remaining_seconds(user_id: int, cooldown_seconds: int, now_ts: float) -> int:
	state = _load_state()
	last_claim = float(state.get("daily_claims", {}).get(str(user_id), 0))
	available_at = last_claim + cooldown_seconds
	if available_at <= now_ts:
		return 0
	return int(available_at - now_ts)


def list_economy_leaderboard(limit: int = 10) -> list[dict]:
	state = _load_state()
	bank_state = state.get("bank", {})
	rows = []
	for hero in state["hero"]:
		if hero.get("active") != 1:
			continue
		bank_balance = int(bank_state.get(str(hero["user_id"]), 0))
		rows.append(
			{
				"user_id": hero["user_id"],
				"level": hero["level"],
				"nex": hero["nex"],
				"bank": bank_balance,
				"total": hero["nex"] + bank_balance,
			}
		)
	rows.sort(key=lambda row: (row["total"], row["nex"], row["level"]), reverse=True)
	return rows[:max(limit, 1)]


def deposit_gold_to_bank(user_id: int, amount: int) -> bool:
	return deposit_nex_to_bank(user_id, amount)


def withdraw_gold_from_bank(user_id: int, amount: int) -> bool:
	return withdraw_nex_from_bank(user_id, amount)


def transfer_bank_gold(sender_user_id: int, target_user_id: int, amount: int) -> bool:
	return transfer_bank_nex(sender_user_id, target_user_id, amount)


def apply_loot_to_active_hero(
	user_id: int,
	level_delta: int,
	xp: int,
	nex: int,
	wood: int,
	iron: int,
	runes: int,
) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return
		hero["level"] += level_delta
		hero["xp"] = xp
		_apply_resource_delta(hero, nex=nex, wood=wood, iron=iron, runes=runes)
		_write_state_unlocked(state)


def get_advancements(user_id: int) -> dict | None:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return None
	advancement = _get_advancement_row(state, hero["id"])
	return None if advancement is None else dict(advancement)


def get_active_quest_log(user_id: int) -> dict | None:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return None
	quest_log = state.setdefault("quest_log", {}).setdefault(str(hero["id"]), {"active": {}, "completed": []})
	quest_log.setdefault("active", {})
	quest_log.setdefault("completed", [])
	return {
		"active": dict(quest_log["active"]),
		"completed": list(quest_log["completed"]),
	}


def save_active_quest_log(user_id: int, quest_log: dict) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return
		state.setdefault("quest_log", {})[str(hero["id"])] = {
			"active": dict(quest_log.get("active", {})),
			"completed": list(quest_log.get("completed", [])),
		}
		_write_state_unlocked(state)


def increment_advancement(user_id: int, field_name: str, amount: int = 1) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return
		advancement = _get_advancement_row(state, hero["id"])
		if advancement is None:
			return
		advancement[field_name] += amount
		_write_state_unlocked(state)


def increment_inventory_item_level(hero_id: int, item_id: int, item_type_name: str) -> None:
	with LOCK:
		state = _read_state_unlocked()
		item = _get_inventory_row(state, hero_id, item_id, ITEM_TYPE_ID_BY_NAME[item_type_name])
		if item is not None:
			item["level"] += 1
			_write_state_unlocked(state)


def count_enemies_in_zone(zone_id: int) -> int:
	return sum(1 for enemy in ENEMIES if enemy["zone"] == zone_id)


def list_seen_enemies_by_zone(user_id: int, zone_id: int) -> list[dict]:
	state = _load_state()
	hero = _get_active_hero_row(state, user_id)
	if hero is None:
		return []
	rows = []
	for dex_entry in state["dex"]:
		if dex_entry["hero_id"] != hero["id"]:
			continue
		enemy = ENEMIES_BY_ID.get(dex_entry["enemy_id"])
		if enemy is None or enemy["zone"] != zone_id:
			continue
		row = {key: dex_entry[key] for key in DEX_FIELDS}
		row.update(enemy)
		rows.append(row)
	return rows


def record_enemy_seen(user_id: int, enemy_id: int) -> None:
	with LOCK:
		state = _read_state_unlocked()
		hero = _get_active_hero_row(state, user_id)
		if hero is None:
			return
		already_seen = any(
			entry["hero_id"] == hero["id"] and entry["enemy_id"] == enemy_id
			for entry in state["dex"]
		)
		if already_seen:
			return
		state["dex"].append({
			"id": _next_id(state, "dex"),
			"hero_id": hero["id"],
			"enemy_id": enemy_id,
		})
		_write_state_unlocked(state)
