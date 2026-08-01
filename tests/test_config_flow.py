"""Tests for config and options flows."""

from __future__ import annotations

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ukr_fuel.const import DOMAIN


async def test_user_flow_creates_per_operator_selection(
    hass: HomeAssistant, mock_minfin_html
) -> None:
    """Test operator step followed by per-operator fuel steps."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"operators": ["ukrnafta", "socar"]},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "fuels"
    assert result["description_placeholders"]["operator"] == "UKRNAFTA"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"fuels": ["a92", "a95"]},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "fuels"
    assert result["description_placeholders"]["operator"] == "SOCAR"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"fuels": ["a95", "diesel"]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Ціни на пальне (Харків)"
    assert result["data"] == {
        "selection": {
            "ukrnafta": ["a92", "a95"],
            "socar": ["a95", "diesel"],
        }
    }


async def test_user_flow_aborts_if_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_minfin_html
) -> None:
    """Only one config entry should be allowed."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow_updates_selection(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_minfin_html
) -> None:
    """Options flow should persist per-operator fuel selection."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"operators": ["brent_oil"]},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "fuels"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"fuels": ["gas"]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {
        "selection": {
            "brent_oil": ["gas"],
        }
    }
