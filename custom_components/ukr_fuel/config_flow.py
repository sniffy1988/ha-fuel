"""Config flow for Ukrainian Fuel Prices."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    DEFAULT_FUELS,
    DEFAULT_OPERATORS,
    DOMAIN,
    FUELS,
    OPERATORS,
)
from .minfin import async_get_operators


def _filter_defaults(defaults: list[str], available: dict[str, str]) -> list[str]:
    """Keep defaults that exist in the available options."""
    filtered = [item for item in defaults if item in available]
    return filtered or list(available)[:5]


def _build_schema(
    operators: dict[str, str],
    default_operators: list[str],
    default_fuels: list[str],
) -> vol.Schema:
    """Build the operators/fuels selection schema."""
    operator_defaults = _filter_defaults(default_operators, operators)
    fuel_defaults = _filter_defaults(default_fuels, FUELS)
    return vol.Schema(
        {
            vol.Required("operators", default=operator_defaults): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": key, "label": label}
                        for key, label in operators.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            ),
            vol.Required("fuels", default=fuel_defaults): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": key, "label": label} for key, label in FUELS.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


class UkrFuelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ukrainian Fuel Prices."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> UkrFuelOptionsFlow:
        """Create the options flow."""
        return UkrFuelOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Ціни на пальне (Харків)",
                data=user_input,
            )

        operators = await async_get_operators(self.hass)
        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(operators, DEFAULT_OPERATORS, DEFAULT_FUELS),
        )


class UkrFuelOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Ukrainian Fuel Prices."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_operators = self.config_entry.options.get(
            "operators",
            self.config_entry.data.get("operators", DEFAULT_OPERATORS),
        )
        current_fuels = self.config_entry.options.get(
            "fuels",
            self.config_entry.data.get("fuels", DEFAULT_FUELS),
        )
        operators = await async_get_operators(self.hass)

        # Keep currently selected custom/unknown slugs visible in the form.
        for slug in current_operators:
            operators.setdefault(slug, OPERATORS.get(slug, slug))

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(operators, current_operators, current_fuels),
        )
