"""Tests for integration setup and sensors."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ukr_fuel.const import DOMAIN


async def test_setup_creates_sensors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_minfin_html,
) -> None:
    """Setup should create one sensor per operator/fuel pair."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    registry = er.async_get(hass)
    ukrnafta_entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, "fuel_price_ukrnafta_a95"
    )
    okko_entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, "fuel_price_okko_diesel"
    )
    assert ukrnafta_entity_id is not None
    assert okko_entity_id is not None

    ukrnafta = hass.states.get(ukrnafta_entity_id)
    assert ukrnafta is not None
    assert ukrnafta.state not in ("unavailable", "unknown")
    assert float(ukrnafta.state) == 79.9
    assert ukrnafta.attributes["unit_of_measurement"] == "грн/л"
    assert ukrnafta.attributes["operator"] == "ukrnafta"
    assert ukrnafta.attributes["fuel"] == "a95"


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_minfin_html,
) -> None:
    """Config entry should unload cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})
