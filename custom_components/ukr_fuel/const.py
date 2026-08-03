"""Constants for the Ukrainian Fuel Prices integration."""

DOMAIN = "ukr_fuel"

FUELS = {
    "a95_plus": "А-95+",
    "a95": "А-95",
    "a92": "А-92",
    "diesel": "ДП",
    "diesel_plus": "ДП+",
    "gas": "Газ",
}

# Fallback list for Харківська обл. (used when Minfin is unreachable).
OPERATORS = {
    "amic": "AMIC",
    "brent_oil": "Brent Oil",
    "marshal": "Marshal",
    "ovis": "Ovis",
    "rodnik": "Rodnik",
    "socar": "SOCAR",
    "sun_oil": "SUN OIL",
    "ukrnafta": "UKRNAFTA",
    "upg": "UPG",
    "wog": "WOG",
    "brsmnafta": "БРСМ-Нафта",
    "dnipronafta": "ДНІПРОНАФТА",
    "okko": "ОККО",
}

DEFAULT_OPERATORS = ["ukrnafta", "socar", "okko", "wog", "upg"]
DEFAULT_FUELS = ["a95", "diesel", "gas"]

MINFIN_URL = "https://index.minfin.com.ua/ua/markets/fuel/reg/harkovskaya/"
SOCAR_URL = "https://socar.ua/fuel"
SOCAR_OPERATOR = "socar"
