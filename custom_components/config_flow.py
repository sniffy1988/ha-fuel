from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from .const import DOMAIN

# Основні види палива з таблиці
FUELS = {
    "a95_plus": "А-95+",
    "a95": "А-95",
    "a92": "А-92",
    "diesel": "ДП",
    "gas": "Газ",
}

class UkrFuelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Конфігураційний потік для вибору заправок."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Ціни на пальне (Мінфін)",
                data=user_input,
            )

        # Дозволяємо користувачу ввести назви заправок через гамбургер/мультиселект або залишити порожнім для всіх
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("operators", default=["ukrnafta", "socar", "okko", "wog", "upg"]): vol.All(
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": "ukrnafta", "label": "Укрнафта"},
                                {"value": "socar", "label": "SOCAR"},
                                {"value": "okko", "label": "ОККО"},
                                {"value": "wog", "label": "WOG"},
                                {"value": "upg", "label": "UPG"},
                                {"value": "amic", "label": "AMIC"},
                                {"value": "bvs", "label": "BVS"},
                                {"value": "klo", "label": "KLO"},
                                {"value": "motto", "label": "Motto"},
                                {"value": "marshal", "label": "Marshal"},
                                {"value": "brsmnafta", "label": "БРСМ-Нафта"},
                                {"value": "avantaž_7", "label": "Авантаж 7"},
                            ],
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            custom_value=True,  # Можливість вписати інші бренди за бажанням
                        )
                    )
                ),
                vol.Required("fuels", default=["a95", "diesel", "gas"]): vol.All(
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[{"value": k, "label": v} for k, v in FUELS.items()],
                            multiple=True,
                            mode=selector.SelectSelectorMode.LISTBOX,
                        )
                    )
                ),
            }),
            errors=errors,
        )