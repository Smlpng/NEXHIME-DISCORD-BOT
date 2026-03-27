from commands.RPG.utils.database import get_active_zone_id


def get_zone(user_id: int) -> int:
    return get_active_zone_id(user_id)
