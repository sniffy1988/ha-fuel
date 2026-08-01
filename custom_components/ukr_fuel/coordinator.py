"""Data update coordinator for Ukrainian Fuel Prices."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import minfin
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=4)


class UkrFuelCoordinator(DataUpdateCoordinator[dict[str, float | None]]):
    """Coordinator that fetches fuel prices from Minfin."""

    def __init__(
        self,
        hass: HomeAssistant,
        selection: dict[str, list[str]],
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.selection = selection

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch and parse prices from Minfin."""
        try:
            html = await minfin.async_fetch_minfin_html(self.hass)
            data = await self.hass.async_add_executor_job(
                minfin.parse_prices,
                html,
                self.selection,
            )
        except minfin.MinfinError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"Помилка парсингу: {err}") from err

        priced = sum(value is not None for value in data.values())
        _LOGGER.debug(
            "Minfin update: %s/%s prices for selection=%s",
            priced,
            len(data),
            self.selection,
        )
        if priced == 0:
            raise UpdateFailed(
                "Не знайдено жодної ціни для вибраних АЗС/палива на Мінфіні"
            )
        return data
