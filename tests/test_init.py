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
    mock_socar_html,
) -> None:
    """Setup should create sensors for legacy cartesian config."""
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


async def test_setup_respects_per_operator_selection(
    hass: HomeAssistant,
    mock_minfin_html,
    mock_socar_html,
) -> None:
    """Only selected fuels per operator should create sensors."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Ціни на пальне (Харків)",
        data={
            "selection": {
                "ukrnafta": ["a92"],
                "socar": ["a95"],
            }
        },
        version=2,
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, "fuel_price_ukrnafta_a92")
        is not None
    )
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, "fuel_price_socar_a95")
        is not None
    )
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, "fuel_price_socar_a92") is None
    )
    assert (
        registry.async_get_entity_id("sensor", DOMAIN, "fuel_price_ukrnafta_a95")
        is None
    )


async def test_setup_socar_uses_official_prices(
    hass: HomeAssistant,
    mock_minfin_html,
    mock_socar_html,
) -> None:
    """SOCAR sensors should use socar.ua prices including ДП+."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Ціни на пальне (Харків)",
        data={
            "selection": {
                "socar": ["a95", "diesel", "diesel_plus", "gas"],
            }
        },
        version=2,
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    a95_id = registry.async_get_entity_id("sensor", DOMAIN, "fuel_price_socar_a95")
    diesel_plus_id = registry.async_get_entity_id(
        "sensor", DOMAIN, "fuel_price_socar_diesel_plus"
    )
    assert a95_id is not None
    assert diesel_plus_id is not None
    assert float(hass.states.get(a95_id).state) == 85.4
    assert float(hass.states.get(diesel_plus_id).state) == 97.9
    assert hass.states.get(a95_id).attributes["source"] == "https://socar.ua/fuel"


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_minfin_html,
    mock_socar_html,
) -> None:
    """Config entry should unload cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})
