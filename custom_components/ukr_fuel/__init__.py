"""Ukrainian Fuel Prices integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DEFAULT_FUELS, DEFAULT_OPERATORS, DOMAIN
from .coordinator import UkrFuelCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _as_str_list(value: object, default: list[str]) -> list[str]:
    """Normalize config values to a clean list of strings."""
    if value is None:
        return list(default)
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return list(default)
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _entry_operators(entry: ConfigEntry) -> list[str]:
    """Resolve selected operators from options, then data."""
    return _as_str_list(
        entry.options.get("operators", entry.data.get("operators")),
        DEFAULT_OPERATORS,
    )


def _entry_fuels(entry: ConfigEntry) -> list[str]:
    """Resolve selected fuels from options, then data."""
    return _as_str_list(
        entry.options.get("fuels", entry.data.get("fuels")),
        DEFAULT_FUELS,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ukrainian Fuel Prices from a config entry."""
    coordinator = UkrFuelCoordinator(
        hass,
        _entry_operators(entry),
        _entry_fuels(entry),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
