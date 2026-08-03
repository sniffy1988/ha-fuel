"""Shared fixtures for Ukrainian Fuel Prices tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ukr_fuel.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations in every test."""
    yield


@pytest.fixture
def minfin_html() -> str:
    """Return sample Minfin HTML fixture."""
    return (Path(__file__).parent / "fixtures" / "minfin.html").read_text(
        encoding="utf-8"
    )


@pytest.fixture
def mock_minfin_html(minfin_html: str):
    """Patch Minfin HTML fetch to return the local fixture."""
    with patch(
        "custom_components.ukr_fuel.minfin.async_fetch_minfin_html",
        new=AsyncMock(return_value=minfin_html),
    ) as mock_fetch:
        yield mock_fetch


@pytest.fixture
def mock_socar_html():
    """Patch SOCAR HTML fetch with full product list."""
    html = """
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
    """
    with patch(
        "custom_components.ukr_fuel.socar.async_fetch_socar_html",
        new=AsyncMock(return_value=html),
    ) as mock_fetch:
        yield mock_fetch


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Ціни на пальне (Харків)",
        data={
            "operators": ["ukrnafta", "okko"],
            "fuels": ["a95", "diesel"],
        },
        version=1,
        unique_id=DOMAIN,
    )
