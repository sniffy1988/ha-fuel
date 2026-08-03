"""Constants for the Ukrainian Fuel Prices integration."""

DOMAIN = "ukr_fuel"

# Minfin region fuels + full SOCAR catalog from https://socar.ua/fuel
FUELS = {
    "a95_plus": "А-95+",
    "a95": "А-95",
    "a92": "А-92",
    "diesel": "ДП",
    "diesel_plus": "ДП+",
    "gas": "Газ",
    "nano_100": "NANO 100",
    "nano_95": "NANO 95",
    "nano_diesel": "NANO ДП",
    "adblue": "AdBlue",
}

# Fuels listed on SOCAR's official fuel page (all selectable for SOCAR).
SOCAR_FUELS = [
    "nano_100",
    "diesel_plus",
    "nano_diesel",
    "nano_95",
    "a95",
    "gas",
    "adblue",
]

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
