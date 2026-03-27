from commands.RPG.utils.database import ensure_profile, has_active_hero, has_selected_class

async def hero_created(inte):
    ensure_profile(inte.user.id)
    if not has_active_hero(inte.user.id) or not has_selected_class(inte.user.id):
        await inte.response.send_message(
            "Seu perfil ja existe, mas voce ainda nao escolheu uma classe. Use !menu para abrir seu perfil e escolher quando quiser."
        )
        return False
    else:
        return True


async def economy_profile_created(inte):
    ensure_profile(inte.user.id)
    return True
