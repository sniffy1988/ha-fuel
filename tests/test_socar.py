"""Unit tests for SOCAR HTML parsing."""

from __future__ import annotations

from custom_components.ukr_fuel.const import SOCAR_FUELS
from custom_components.ukr_fuel.socar import parse_price, parse_prices, title_to_fuel

SOCAR_HTML = """
<html><body>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">NANO 100</h2>
  <p class="two-image-and-content__price">*Ціна: 95.4 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">DIESEL NANO Extro</h2>
  <p class="two-image-and-content__price">*Ціна: 97.9 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">NANO ДП</h2>
  <p class="two-image-and-content__price">*Ціна: 94.9 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">NANO 95</h2>
  <p class="two-image-and-content__price">*Ціна: 88.4 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">Бензин А-95</h2>
  <p class="two-image-and-content__price">*Ціна: 85.4 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">LPG</h2>
  <p class="two-image-and-content__price">*Ціна: 43.9 грн/л</p>
</div>
<div class="two-image-and-content">
  <h2 class="two-image-and-content__title">AdBlue</h2>
  <p class="two-image-and-content__price">*Ціна: 49 грн/л</p>
</div>
</body></html>
"""


def test_parse_price() -> None:
    """SOCAR price lines should parse as floats."""
    assert parse_price("*Ціна: 85.4 грн/л") == 85.4
    assert parse_price("*Ціна: 49 грн/л") == 49.0


def test_title_to_fuel_mapping() -> None:
    """Every product title from socar.ua/fuel should map to a fuel key."""
    assert title_to_fuel("NANO 100") == "nano_100"
    assert title_to_fuel("DIESEL NANO Extro") == "diesel_plus"
    assert title_to_fuel("NANO ДП") == "nano_diesel"
    assert title_to_fuel("NANO 95") == "nano_95"
    assert title_to_fuel("Бензин А-95") == "a95"
    assert title_to_fuel("LPG") == "gas"
    assert title_to_fuel("AdBlue") == "adblue"


def test_parse_prices_all_socar_fuels() -> None:
    """All SOCAR fuels should resolve from page blocks."""
    data = parse_prices(SOCAR_HTML, SOCAR_FUELS)
    assert data == {
        "nano_100": 95.4,
        "diesel_plus": 97.9,
        "nano_diesel": 94.9,
        "nano_95": 88.4,
        "a95": 85.4,
        "gas": 43.9,
        "adblue": 49.0,
    }


def test_parse_prices_legacy_aliases() -> None:
    """Legacy diesel / A-95+ keys still resolve for older configs."""
    data = parse_prices(SOCAR_HTML, ["diesel", "a95_plus", "gas"])
    assert data["diesel"] == 94.9
    assert data["a95_plus"] == 88.4
    assert data["gas"] == 43.9
