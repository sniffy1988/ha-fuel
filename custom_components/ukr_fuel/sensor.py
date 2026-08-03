"""Sensor platform for Ukrainian Fuel Prices."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FUELS, MINFIN_URL, OPERATORS, SOCAR_OPERATOR, SOCAR_URL
from .coordinator import UkrFuelCoordinator
from .selection import selection_pairs

FUEL_ICONS = {
    "a95_plus": "mdi:gas-station",
    "a95": "mdi:gas-station",
    "a92": "mdi:gas-station",
    "diesel": "mdi:fuel",
    "diesel_plus": "mdi:fuel",
    "nano_100": "mdi:gas-station",
    "nano_95": "mdi:gas-station",
    "nano_diesel": "mdi:fuel",
    "gas": "mdi:propane-tank",
    "adblue": "mdi:water",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ukrainian Fuel Prices sensors from a config entry."""
    coordinator: UkrFuelCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        FuelSensor(
            coordinator=coordinator,
            operator=operator,
            operator_name=OPERATORS.get(operator, operator.replace("_", " ").title()),
            fuel=fuel,
            fuel_name=FUELS[fuel],
            icon=FUEL_ICONS.get(fuel, "mdi:gas-station"),
        )
        for operator, fuel in selection_pairs(coordinator.selection)
    ]

    async_add_entities(sensors)


class FuelSensor(CoordinatorEntity[UkrFuelCoordinator], SensorEntity):
    """Representation of a fuel price sensor."""

    _attr_native_unit_of_measurement = "грн/л"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: UkrFuelCoordinator,
        operator: str,
        operator_name: str,
        fuel: str,
        fuel_name: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._operator = operator
        self._fuel = fuel
        self._key = f"{operator}_{fuel}"
        self._attr_name = f"{operator_name} {fuel_name}"
        self._attr_icon = icon
        self._attr_unique_id = f"fuel_price_{self._key}"
        if operator == SOCAR_OPERATOR:
            self._attr_attribution = "Дані: SOCAR Energy Ukraine"
            self._source = SOCAR_URL
        else:
            self._attr_attribution = "Дані: Мінфін (Харківська обл.)"
            self._source = MINFIN_URL

    @property
    def native_value(self) -> float | None:
        """Return the current fuel price, or None if missing."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return diagnostic attributes."""
        return {
            "operator": self._operator,
            "fuel": self._fuel,
            "source": self._source,
        }
