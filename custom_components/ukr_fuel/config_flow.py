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
    SOCAR_FUELS,
    SOCAR_OPERATOR,
)
from .minfin import async_get_operators
from .selection import default_selection, normalize_selection, resolve_selection


def _filter_defaults(defaults: list[str], available: dict[str, str]) -> list[str]:
    """Keep defaults that exist in the available options."""
    filtered = [item for item in defaults if item in available]
    return filtered or list(available)[:5]


def _fuel_choices_for_operator(operator: str) -> dict[str, str]:
    """Return fuel options tailored to the operator."""
    if operator == SOCAR_OPERATOR:
        # SOCAR page products first, then remaining shared labels.
        ordered = list(SOCAR_FUELS) + [
            key for key in FUELS if key not in SOCAR_FUELS
        ]
        return {key: FUELS[key] for key in ordered if key in FUELS}
    return dict(FUELS)


def _operators_schema(
    operators: dict[str, str], default_operators: list[str]
) -> vol.Schema:
    """Build operator multi-select schema."""
    return vol.Schema(
        {
            vol.Required(
                "operators",
                default=_filter_defaults(default_operators, operators),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": key, "label": label}
                        for key, label in operators.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            )
        }
    )


def _fuels_schema(
    default_fuels: list[str], fuel_choices: dict[str, str]
) -> vol.Schema:
    """Build fuel multi-select schema for one operator."""
    return vol.Schema(
        {
            vol.Required(
                "fuels",
                default=_filter_defaults(default_fuels, fuel_choices),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": key, "label": label}
                        for key, label in fuel_choices.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        }
    )


class _SelectionFlowMixin:
    """Shared multi-step operator then per-operator fuels selection."""

    _operator_labels: dict[str, str]
    _selected_operators: list[str]
    _selection: dict[str, list[str]]
    _fuel_index: int
    _current_defaults: dict[str, list[str]]

    def _init_selection_state(self) -> None:
        """Ensure flow state attributes exist."""
        if not hasattr(self, "_operator_labels"):
            self._operator_labels = {}
        if not hasattr(self, "_selected_operators"):
            self._selected_operators = []
        if not hasattr(self, "_selection"):
            self._selection = {}
        if not hasattr(self, "_fuel_index"):
            self._fuel_index = 0
        if not hasattr(self, "_current_defaults"):
            self._current_defaults = {}

    async def _async_start_fuel_steps(
        self, operators: list[str]
    ) -> config_entries.ConfigFlowResult:
        """Begin per-operator fuel selection."""
        self._init_selection_state()
        self._selected_operators = [op.strip().lower() for op in operators if op]
        self._selection = {}
        self._fuel_index = 0
        if not self._selected_operators:
            return self.async_abort(reason="no_operators")
        return await self.async_step_fuels()

    async def async_step_fuels(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Select fuels for the current operator."""
        self._init_selection_state()
        if self._fuel_index >= len(self._selected_operators):
            return await self._async_finish_selection()

        current = self._selected_operators[self._fuel_index]
        if user_input is not None:
            fuels = [
                fuel
                for fuel in user_input.get("fuels", [])
                if fuel in FUELS
            ]
            if fuels:
                self._selection[current] = fuels
            self._fuel_index += 1
            if self._fuel_index < len(self._selected_operators):
                return await self.async_step_fuels()
            return await self._async_finish_selection()

        defaults = self._current_defaults.get(current)
        if defaults is None:
            defaults = (
                list(SOCAR_FUELS) if current == SOCAR_OPERATOR else list(DEFAULT_FUELS)
            )
        fuel_choices = _fuel_choices_for_operator(current)
        label = self._operator_labels.get(
            current, OPERATORS.get(current, current.replace("_", " ").title())
        )
        return self.async_show_form(
            step_id="fuels",
            data_schema=_fuels_schema(defaults, fuel_choices),
            description_placeholders={
                "operator": label,
                "step_number": str(self._fuel_index + 1),
                "step_count": str(len(self._selected_operators)),
            },
        )

    async def _async_finish_selection(self) -> config_entries.ConfigFlowResult:
        """Persist the completed selection."""
        selection = normalize_selection(self._selection)
        if not selection:
            selection = default_selection()
        return await self._async_store_selection(selection)

    async def _async_store_selection(
        self, selection: dict[str, list[str]]
    ) -> config_entries.ConfigFlowResult:
        """Implemented by config/options flow subclasses."""
        raise NotImplementedError


class UkrFuelConfigFlow(_SelectionFlowMixin, config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ukrainian Fuel Prices."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> UkrFuelOptionsFlow:
        """Create the options flow."""
        return UkrFuelOptionsFlow()

    async def _async_store_selection(
        self, selection: dict[str, list[str]]
    ) -> config_entries.ConfigFlowResult:
        """Create the config entry."""
        return self.async_create_entry(
            title="Ціни на пальне (Харків)",
            data={"selection": selection},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial operator selection step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        self._init_selection_state()

        if user_input is not None:
            return await self._async_start_fuel_steps(user_input["operators"])

        self._operator_labels = await async_get_operators(self.hass)
        self._current_defaults = default_selection()
        return self.async_show_form(
            step_id="user",
            data_schema=_operators_schema(self._operator_labels, DEFAULT_OPERATORS),
        )


class UkrFuelOptionsFlow(_SelectionFlowMixin, config_entries.OptionsFlow):
    """Handle options for Ukrainian Fuel Prices."""

    async def _async_store_selection(
        self, selection: dict[str, list[str]]
    ) -> config_entries.ConfigFlowResult:
        """Save options."""
        return self.async_create_entry(title="", data={"selection": selection})

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Select operators to reconfigure."""
        self._init_selection_state()
        self._current_defaults = resolve_selection(self.config_entry)

        if user_input is not None:
            return await self._async_start_fuel_steps(user_input["operators"])

        self._operator_labels = await async_get_operators(self.hass)
        for slug in self._current_defaults:
            self._operator_labels.setdefault(
                slug, OPERATORS.get(slug, slug.replace("_", " ").title())
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_operators_schema(
                self._operator_labels, list(self._current_defaults)
            ),
        )
