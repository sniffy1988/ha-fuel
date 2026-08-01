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
        selected_operators: list[str],
        selected_fuels: list[str],
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.selected_operators = selected_operators
        self.selected_fuels = selected_fuels

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch and parse prices from Minfin."""
        try:
            html = await minfin.async_fetch_minfin_html(self.hass)
            return await self.hass.async_add_executor_job(
                minfin.parse_prices,
                html,
                self.selected_operators,
                self.selected_fuels,
            )
        except minfin.MinfinError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"Помилка парсингу: {err}") from err
