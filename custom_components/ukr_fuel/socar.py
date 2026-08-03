"""SOCAR official fuel-price helpers."""

from __future__ import annotations

import asyncio
import logging
import re

from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import SOCAR_URL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Referer": "https://socar.ua/",
}

# All products from https://socar.ua/fuel (most specific patterns first).
_TITLE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"diesel\s*nano\s*extro", re.I), "diesel_plus"),
    (re.compile(r"nano\s*дп|nano\s*dp", re.I), "nano_diesel"),
    (re.compile(r"nano\s*100", re.I), "nano_100"),
    (re.compile(r"nano\s*95", re.I), "nano_95"),
    (re.compile(r"ad\s*blue|adblue", re.I), "adblue"),
    (re.compile(r"бензин\s*а[-\s]?95|а[-\s]?95\b", re.I), "a95"),
    (re.compile(r"\blpg\b", re.I), "gas"),
]


class SocarError(Exception):
    """Raised when SOCAR data cannot be fetched or parsed."""


def parse_price(text: str) -> float | None:
    """Parse a SOCAR price line into a float."""
    try:
        cleaned = text.replace("\xa0", " ").strip().replace(" ", "").replace(",", ".")
        match = re.search(r"\d+\.\d+|\d+", cleaned)
        if match:
            return float(match.group())
    except (TypeError, ValueError):
        pass
    return None


def title_to_fuel(title: str) -> str | None:
    """Map a SOCAR product title to a fuel key."""
    cleaned = " ".join(title.split())
    for pattern, fuel in _TITLE_RULES:
        if pattern.search(cleaned):
            return fuel
    return None


def parse_prices(html: str, selected_fuels: list[str]) -> dict[str, float | None]:
    """Parse SOCAR fuel page into fuel_key -> price."""
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.select(".two-image-and-content")
    if not blocks:
        raise SocarError("Не вдалося знайти блоки цін на сторінці SOCAR")

    fuels = [fuel.lower() for fuel in selected_fuels]
    data: dict[str, float | None] = {fuel: None for fuel in fuels}
    found_any = False

    for block in blocks:
        title_el = block.select_one(".two-image-and-content__title, h2, h3")
        price_el = block.select_one(".two-image-and-content__price")
        if not title_el or not price_el:
            continue

        title = title_el.get_text(" ", strip=True)
        fuel_key = title_to_fuel(title)
        price = parse_price(price_el.get_text(" ", strip=True))
        if fuel_key is None or price is None:
            continue

        found_any = True
        if fuel_key in data and data[fuel_key] is None:
            data[fuel_key] = price

    if not found_any:
        raise SocarError("Не вдалося розпарсити ціни SOCAR")

    return data


async def async_fetch_socar_html(hass: HomeAssistant) -> str:
    """Fetch SOCAR fuel page HTML."""
    session = async_get_clientsession(hass)
    try:
        async with asyncio.timeout(15):
            async with session.get(
                SOCAR_URL,
                headers=REQUEST_HEADERS,
            ) as response:
                if response.status != 200:
                    raise SocarError(f"Помилка HTTP від SOCAR: {response.status}")
                return await response.text()
    except SocarError:
        raise
    except Exception as err:
        raise SocarError(f"Помилка запиту до SOCAR: {err}") from err
