"""Minfin HTML fetch and parse helpers."""

from __future__ import annotations

import asyncio
import logging
import re

from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import MINFIN_URL, OPERATORS

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Referer": "https://index.minfin.com.ua/ua/markets/fuel/",
}


class MinfinError(Exception):
    """Raised when Minfin data cannot be fetched or parsed."""


def parse_price(text: str) -> float | None:
    """Parse a Minfin price cell into a float."""
    try:
        cleaned = text.replace("\xa0", " ").strip().replace(" ", "").replace(",", ".")
        match = re.search(r"\d+\.\d+|\d+", cleaned)
        if match:
            return float(match.group())
    except (TypeError, ValueError):
        pass
    return None


def parse_operators(html: str) -> dict[str, str]:
    """Parse operator slug -> label mapping from Minfin HTML."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#tm-table table")
    if not table:
        raise MinfinError("Не вдалося знайти таблицю цін")

    operators: dict[str, str] = {}
    for row in table.select("tr"):
        link = row.select_one("td a")
        if not link or not link.get("href"):
            continue
        match_slug = re.search(r"/tm/([^/]+)/", link.get("href", ""))
        if not match_slug:
            continue
        slug = match_slug.group(1).lower()
        label = link.get_text(strip=True) or OPERATORS.get(slug, slug)
        operators[slug] = label
    if not operators:
        raise MinfinError("Не вдалося знайти операторів у таблиці")
    return operators


def parse_prices(
    html: str, selection: dict[str, list[str]]
) -> dict[str, float | None]:
    """Parse Minfin HTML into operator_fuel -> price mapping."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#tm-table table")
    if not table:
        raise MinfinError("Не вдалося знайти таблицю цін")

    normalized = {
        op.lower(): [fuel.lower() for fuel in fuels]
        for op, fuels in selection.items()
    }
    # Always expose every requested sensor key, even when Minfin has no value.
    data: dict[str, float | None] = {
        f"{op}_{fuel}": None
        for op, fuels in normalized.items()
        for fuel in fuels
    }

    for row in table.select("tr"):
        link = row.select_one("td a")
        cells = row.select("td")
        if not cells or len(cells) < 6:
            continue

        op_slug = ""
        if link and link.get("href"):
            match_slug = re.search(r"/tm/([^/]+)/", link.get("href", ""))
            if match_slug:
                op_slug = match_slug.group(1).lower()

        if not op_slug or op_slug not in normalized:
            continue

        # Cells: [0] name, [1] spacer, [2] A-95+, [3] A-95, [4] A-92, [5] ДП, [6] Газ
        row_fuel_map = {
            "a95_plus": parse_price(cells[2].get_text()) if len(cells) > 2 else None,
            "a95": parse_price(cells[3].get_text()) if len(cells) > 3 else None,
            "a92": parse_price(cells[4].get_text()) if len(cells) > 4 else None,
            "diesel": parse_price(cells[5].get_text()) if len(cells) > 5 else None,
            "gas": parse_price(cells[6].get_text()) if len(cells) > 6 else None,
        }

        for fuel_key in normalized[op_slug]:
            data[f"{op_slug}_{fuel_key}"] = row_fuel_map.get(fuel_key)

    return data


async def async_fetch_minfin_html(hass: HomeAssistant) -> str:
    """Fetch Minfin fuel table HTML."""
    session = async_get_clientsession(hass)
    try:
        async with asyncio.timeout(15):
            async with session.get(
                MINFIN_URL,
                headers=REQUEST_HEADERS,
            ) as response:
                if response.status != 200:
                    raise MinfinError(f"Помилка HTTP від Мінфіну: {response.status}")
                return await response.text()
    except MinfinError:
        raise
    except Exception as err:
        raise MinfinError(f"Помилка запиту до Мінфіну: {err}") from err


async def async_get_operators(hass: HomeAssistant) -> dict[str, str]:
    """Fetch live operators from Minfin, falling back to the static list."""
    try:
        html = await async_fetch_minfin_html(hass)
        operators = await hass.async_add_executor_job(parse_operators, html)
        return operators
    except MinfinError as err:
        _LOGGER.warning("Using static operator list: %s", err)
        return dict(OPERATORS)
