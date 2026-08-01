"""Unit tests for Minfin HTML parsing."""

from __future__ import annotations

import pytest

from custom_components.ukr_fuel.minfin import (
    MinfinError,
    parse_operators,
    parse_price,
    parse_prices,
)


def test_parse_price_comma_decimal() -> None:
    """Ukrainian comma decimals should parse as floats."""
    assert parse_price("82,90") == 82.9
    assert parse_price(" 79,95 ") == 79.95


def test_parse_price_blank() -> None:
    """Blank / br cells should return None."""
    assert parse_price("") is None
    assert parse_price("\n") is None


def test_parse_operators(minfin_html: str) -> None:
    """Operator slugs and labels should be extracted from the table."""
    operators = parse_operators(minfin_html)
    assert operators["ukrnafta"] == "UKRNAFTA"
    assert operators["okko"] == "ОККО"
    assert operators["brent_oil"] == "Brent Oil"


def test_parse_prices(minfin_html: str) -> None:
    """Selected operator/fuel prices should be mapped correctly."""
    data = parse_prices(
        minfin_html,
        selected_operators=["ukrnafta", "okko", "brent_oil"],
        selected_fuels=["a95", "diesel", "a95_plus", "a92"],
    )
    assert data["ukrnafta_a95"] == 79.9
    assert data["okko_diesel"] == 92.5
    assert data["brent_oil_a95"] == 79.95
    assert data["brent_oil_a95_plus"] is None
    assert data["brent_oil_a92"] == 75.95
    assert data["okko_a95_plus"] == 85.9


def test_parse_operators_missing_table() -> None:
    """Missing table should raise MinfinError."""
    with pytest.raises(MinfinError):
        parse_operators("<html><body>no table</body></html>")
