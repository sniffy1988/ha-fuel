from datetime import timedelta
import logging
import re
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
MINFIN_URL = "https://index.minfin.com.ua/ua/markets/fuel/tm/"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    selected_operators = entry.data.get("operators", ["ukrnafta", "socar"])
    selected_fuels = entry.data.get("fuels", ["a95", "diesel"])

    async def async_update_data():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data = {}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(MINFIN_URL, timeout=15) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Помилка HTTP від Мінфіну: {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.select_one("#tm-table table")
                    if not table:
                        raise UpdateFailed("Не вдалося знайти таблицю цін")
                    
                    def parse_price(text):
                        try:
                            cleaned = text.replace(u'\xa0', u' ').strip().replace(" ", "").replace(",", ".")
                            match = re.search(r'\d+\.\d+|\d+', cleaned)
                            if match:
                                return float(match.group())
                        except Exception:
                            pass
                        return None

                    rows = table.select("tr")
                    for row in rows:
                        link = row.select_one("td a")
                        cells = row.select("td")
                        if not cells or len(cells) < 6:
                            continue
                        
                        # Визначаємо ідентифікатор оператора з посилання (наприклад, /ua/markets/fuel/tm/ukrnafta/ -> ukrnafta)
                        op_slug = ""
                        if link and link.get("href"):
                            match_slug = re.search(r'/tm/([^/]+)/', link.get("href"))
                            if match_slug:
                                op_slug = match_slug.group(1).lower()
                        
                        if not op_slug:
                            continue

                        # Якщо оператор обраний користувачем для моніторингу
                        if op_slug in selected_operators:
                            # Мапінг колонок таблиці Мінфіну:
                            # [2] А-95+, [3] А-95, [4] А-92, [5] ДП, [6] Газ
                            row_fuel_map = {
                                "a95_plus": parse_price(cells[2].get_text()) if len(cells) > 2 else None,
                                "a95": parse_price(cells[3].get_text()) if len(cells) > 3 else None,
                                "a92": parse_price(cells[4].get_text()) if len(cells) > 4 else None,
                                "diesel": parse_price(cells[5].get_text()) if len(cells) > 5 else None,
                                "gas": parse_price(cells[6].get_text()) if len(cells) > 6 else None,
                            }

                            for fuel_key in selected_fuels:
                                data[f"{op_slug}_{fuel_key}"] = row_fuel_map.get(fuel_key)

            except Exception as err:
                raise UpdateFailed(f"Помилка парсингу: {err}")

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    fuel_meta = {
        "a95_plus": ("А-95+", "mdi:gas-station"),
        "a95": ("А-95", "mdi:gas-station"),
        "a92": ("А-92", "mdi:gas-station"),
        "diesel": ("ДП", "mdi:fuel"),
        "gas": ("Газ", "mdi:propane-tank"),
    }

    sensors = []
    for op in selected_operators:
        # Робимо красиву назву бренду з великої літери
        op_formatted_name = op.replace("_", " ").title()
        for fuel in selected_fuels:
            if fuel in fuel_meta:
                f_name, f_icon = fuel_meta[fuel]
                sensors.append(
                    FuelSensor(
                        coordinator, 
                        f"{op_formatted_name} {f_name}", 
                        f"{op}_{fuel}", 
                        f_icon
                    )
                )

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
        return self.coordinator.last_update_success and self._key in self.coordinator.data and self.coordinator.data.get(self._key) is not None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )