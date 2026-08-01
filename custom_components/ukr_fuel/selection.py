"""Helpers for per-operator fuel selection."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

from .const import DEFAULT_FUELS, DEFAULT_OPERATORS, FUELS


def _as_str_list(value: object, default: list[str] | None = None) -> list[str]:
    """Normalize config values to a clean list of strings."""
    if value is None:
        return list(default or [])
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return list(default or [])
    return [str(item).strip().lower() for item in value if str(item).strip()]


def normalize_selection(raw: object) -> dict[str, list[str]]:
    """Normalize a selection mapping to operator -> fuels."""
    if not isinstance(raw, dict):
        return {}

    selection: dict[str, list[str]] = {}
    for operator, fuels in raw.items():
        op = str(operator).strip().lower()
        fuel_list = [fuel for fuel in _as_str_list(fuels) if fuel in FUELS]
        if op and fuel_list:
            selection[op] = fuel_list
    return selection


def default_selection() -> dict[str, list[str]]:
    """Return the default operator/fuel mapping."""
    return {operator: list(DEFAULT_FUELS) for operator in DEFAULT_OPERATORS}


def resolve_selection(entry: ConfigEntry) -> dict[str, list[str]]:
    """Resolve selection from options/data, including legacy cartesian config."""
    for source in (entry.options, entry.data):
        if "selection" in source:
            selection = normalize_selection(source.get("selection"))
            if selection:
                return selection

    operators = _as_str_list(
        entry.options.get("operators", entry.data.get("operators")),
        DEFAULT_OPERATORS,
    )
    fuels = _as_str_list(
        entry.options.get("fuels", entry.data.get("fuels")),
        DEFAULT_FUELS,
    )
    fuels = [fuel for fuel in fuels if fuel in FUELS]
    if not operators or not fuels:
        return default_selection()
    return {operator: list(fuels) for operator in operators}


def selection_pairs(selection: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Flatten selection into (operator, fuel) pairs."""
    return [
        (operator, fuel)
        for operator, fuels in selection.items()
        for fuel in fuels
        if fuel in FUELS
    ]
