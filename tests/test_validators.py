from commands.EconomiaRPG.utils import database
from commands.EconomiaRPG.utils.validators import (
    format_nex,
    validate_amount_range,
    validate_bet_amount,
    validate_positive_amount,
    validate_wallet_balance,
)


def _make_profile(user_id: int, nex: int) -> None:
    database.ensure_profile(user_id)
    state = database._load_state()
    hero = database._get_active_hero_row(state, user_id)
    hero["class"] = "guerreiro"
    hero["nex"] = nex
    database._save_state(state)


def test_format_nex_uses_thousands_separator() -> None:
    assert format_nex(1234567) == "1.234.567"


def test_validate_positive_amount_rejects_zero() -> None:
    result = validate_positive_amount(0)
    assert not result.ok
    assert result.message == "Informe uma quantidade positiva."


def test_validate_amount_range_rejects_outside_interval() -> None:
    result = validate_amount_range(9, field_name="minas", minimum=1, maximum=8)
    assert not result.ok
    assert result.message == "Minas deve ficar entre 1 e 8."


def test_validate_wallet_balance_uses_hero_wallet(players_data_file) -> None:
    _make_profile(42, 150)
    result = validate_wallet_balance(42, 200, context="essa transferencia")
    assert not result.ok
    assert result.message == "Voce nao tem nex suficiente para essa transferencia. Carteira atual: 150 nex."


def test_validate_bet_amount_accepts_valid_balance(players_data_file) -> None:
    _make_profile(84, 900)
    result = validate_bet_amount(84, 250, context="esse jogo")
    assert result.ok