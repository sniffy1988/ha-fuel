"""Data update coordinator for Ukrainian Fuel Prices."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import minfin, socar
from .const import DOMAIN, SOCAR_OPERATOR

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)


class UkrFuelCoordinator(DataUpdateCoordinator[dict[str, float | None]]):
    """Coordinator that fetches fuel prices from Minfin and SOCAR."""

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
        """Fetch and parse prices from Minfin and official SOCAR page."""
        data: dict[str, float | None] = {}
        errors: list[str] = []

        minfin_selection = {
            op: fuels
            for op, fuels in self.selection.items()
            if op != SOCAR_OPERATOR
        }
        socar_fuels = self.selection.get(SOCAR_OPERATOR, [])

        if minfin_selection:
            try:
                html = await minfin.async_fetch_minfin_html(self.hass)
                minfin_data = await self.hass.async_add_executor_job(
                    minfin.parse_prices,
                    html,
                    minfin_selection,
                )
                data.update(minfin_data)
            except minfin.MinfinError as err:
                errors.append(str(err))
                for op, fuels in minfin_selection.items():
                    for fuel in fuels:
                        data.setdefault(f"{op}_{fuel}", None)
            except Exception as err:  # noqa: BLE001
                errors.append(f"Помилка парсингу Мінфін: {err}")
                for op, fuels in minfin_selection.items():
                    for fuel in fuels:
                        data.setdefault(f"{op}_{fuel}", None)

        if socar_fuels:
            try:
                html = await socar.async_fetch_socar_html(self.hass)
                socar_data = await self.hass.async_add_executor_job(
                    socar.parse_prices,
                    html,
                    socar_fuels,
                )
                for fuel, price in socar_data.items():
                    data[f"{SOCAR_OPERATOR}_{fuel}"] = price
            except socar.SocarError as err:
                errors.append(str(err))
                for fuel in socar_fuels:
                    data.setdefault(f"{SOCAR_OPERATOR}_{fuel}", None)
            except Exception as err:  # noqa: BLE001
                errors.append(f"Помилка парсингу SOCAR: {err}")
                for fuel in socar_fuels:
                    data.setdefault(f"{SOCAR_OPERATOR}_{fuel}", None)

        priced = sum(value is not None for value in data.values())
        _LOGGER.debug(
            "Price update: %s/%s priced selection=%s errors=%s",
            priced,
            len(data),
            self.selection,
            errors,
        )
        if priced == 0:
            detail = "; ".join(errors) if errors else "немає даних"
            raise UpdateFailed(f"Не знайдено жодної ціни ({detail})")
        return data
