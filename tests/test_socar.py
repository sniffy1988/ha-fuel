"""Unit tests for SOCAR HTML parsing."""

from __future__ import annotations

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
    """Titles should map to stable fuel keys."""
    assert title_to_fuel("DIESEL NANO Extro") == "diesel_plus"
    assert title_to_fuel("NANO ДП") == "diesel"
    assert title_to_fuel("NANO 95") == "a95_plus"
    assert title_to_fuel("Бензин А-95") == "a95"
    assert title_to_fuel("LPG") == "gas"
    assert title_to_fuel("NANO 100") is None
    assert title_to_fuel("AdBlue") is None


def test_parse_prices() -> None:
    """Selected fuels should resolve from SOCAR blocks."""
    data = parse_prices(
        SOCAR_HTML,
        ["a95_plus", "a95", "diesel", "diesel_plus", "gas"],
    )
    assert data["diesel_plus"] == 97.9
    assert data["diesel"] == 94.9
    assert data["a95_plus"] == 88.4
    assert data["a95"] == 85.4
    assert data["gas"] == 43.9
