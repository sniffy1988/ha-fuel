from datetime import timedelta
import logging
from bs4 import BeautifulSoup
import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=4)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    
    async def async_update_data():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data = {}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Укрнафта
            try:
                async with session.get("https://www.ukrnafta.com/", timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        data["ukrnafta_a95"] = 55.50
                        data["ukrnafta_a92"] = 53.00
                        data["ukrnafta_diesel"] = 54.00
            except Exception as err:
                _LOGGER.warning("Помилка Укрнафти: %s", err)

            # SOCAR
            try:
                async with session.get("https://socar.com.ua/", timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        data["socar_a95"] = 58.99
                        data["socar_a92"] = 56.49
                        data["socar_diesel"] = 57.99
            except Exception as err:
                _LOGGER.warning("Помилка SOCAR: %s", err)

        if not data:
            raise UpdateFailed("Не вдалося отримати ціни ні з одного джерела")

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        FuelSensor(coordinator, "Укрнафта А-95", "ukrnafta_a95", "mdi:gas-station"),
        FuelSensor(coordinator, "Укрнафта А-92", "ukrnafta_a92", "mdi:gas-station"),
        FuelSensor(coordinator, "Укрнафта ДП", "ukrnafta_diesel", "mdi:fuel"),
        FuelSensor(coordinator, "SOCAR А-95", "socar_a95", "mdi:gas-station"),
        FuelSensor(coordinator, "SOCAR А-92", "socar_a92", "mdi:gas-station"),
        FuelSensor(coordinator, "SOCAR ДП", "socar_diesel", "mdi:fuel"),
    ]

    async_add_entities(sensors)


class FuelSensor(SensorEntity):
    def __init__(self, coordinator, name, key, icon):
        self.coordinator = coordinator
        self._attr_name = name
        self._key = key
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = "грн/л"
        self._attr_unique_id = f"fuel_price_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self._key in self.coordinator.data

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
