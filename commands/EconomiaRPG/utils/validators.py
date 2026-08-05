from __future__ import annotations

from dataclasses import dataclass

from commands.EconomiaRPG.utils.database import get_active_hero


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str | None = None


def format_nex(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def validate_positive_amount(amount: int, *, field_name: str = "quantidade", minimum: int = 1) -> ValidationResult:
    if amount < minimum:
        if minimum == 1:
            return ValidationResult(False, f"Informe uma {field_name} positiva.")
        return ValidationResult(False, f"Informe uma {field_name} maior ou igual a {minimum}.")
    return ValidationResult(True)


def validate_amount_range(amount: int, *, field_name: str, minimum: int, maximum: int) -> ValidationResult:
    if amount < minimum or amount > maximum:
        return ValidationResult(False, f"{field_name.capitalize()} deve ficar entre {minimum} e {maximum}.")
    return ValidationResult(True)


def validate_wallet_balance(user_id: int, amount: int, *, context: str = "essa operacao") -> ValidationResult:
    hero = get_active_hero(user_id)
    if hero is None:
        return ValidationResult(False, "Nao consegui localizar seu heroi ativo.")

    wallet = int(hero.get("nex", 0))
    if wallet < amount:
        return ValidationResult(
            False,
            f"Voce nao tem nex suficiente para {context}. Carteira atual: {format_nex(wallet)} nex.",
        )
    return ValidationResult(True)


def validate_bet_amount(
    user_id: int,
    amount: int,
    *,
    minimum: int = 1,
    maximum: int | None = None,
    context: str = "essa aposta",
) -> ValidationResult:
    positive_check = validate_positive_amount(amount, field_name="aposta", minimum=minimum)
    if not positive_check.ok:
        return positive_check

    if maximum is not None and amount > maximum:
        return ValidationResult(False, f"A aposta maxima permitida para {context} e de {format_nex(maximum)} nex.")

    return validate_wallet_balance(user_id, amount, context=context)