# Ukrainian Fuel Prices for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/sniffy1988/ha-fuel?style=flat-square)](https://github.com/sniffy1988/ha-fuel/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

Кастомна інтеграція для **Home Assistant**, яка збирає актуальні ціни на пальне в **Харківській області** з [Мінфіну](https://index.minfin.com.ua/ua/markets/fuel/reg/harkovskaya/) для вибраних мереж АЗС (**Укрнафта**, **SOCAR**, **ОККО**, **WOG** та інші) та видів палива.

---

## Можливості

* **Вибір палива для кожної АЗС окремо**: спочатку обираєте операторів, далі для кожного — свої види палива (наприклад, `А-92` лише для Укрнафти, без SOCAR).
* **SOCAR з офіційного сайту**: для SOCAR ціни беруться з [socar.ua/fuel](https://socar.ua/fuel) (включно з **ДП+**); інші АЗС — з [Мінфіну](https://index.minfin.com.ua/ua/markets/fuel/reg/harkovskaya/) (Харківська обл.).
* **Регіон для інших АЗС — Харківська обл.**: оператори підтягуються з актуальної таблиці, а при недоступності сайту — із запасного списку.
* **Зміна налаштувань**: операторів і паливо можна змінити пізніше в опціях інтеграції.
* **Автоматичне оновлення**: фонове опитування джерела щогодини.
* **Надійність**: відсутня ціна для пари АЗС/паливо робить сенсор unavailable, без падіння інтеграції.

---

## Встановлення через HACS (Рекомендовано)

1. Відкрийте ваш **Home Assistant** і перейдіть у **HACS**.
2. Натисніть на три крапки у правому верхньому кутку та виберіть **Користувацькі репозиторії (Custom repositories)**.
3. Вставте посилання на цей репозиторій:

   ```text
   https://github.com/sniffy1988/ha-fuel
   ```

4. Оберіть тип **Integration**, додайте репозиторій і встановіть **Ukrainian Fuel Prices**.
5. Перезавантажте Home Assistant.
6. Перейдіть у **Налаштування → Пристрої та служби → Додати інтеграцію** і знайдіть **Ukrainian Fuel Prices**.
7. Оберіть потрібні АЗС та види палива — для кожної пари буде створено окремий сенсор.

Щоб змінити вибір пізніше: **Налаштування → Пристрої та служби → Ukrainian Fuel Prices → Налаштувати**.

---

## Ручне встановлення

1. Скопіюйте теку `custom_components/ukr_fuel` у директорію `config/custom_components/` вашого Home Assistant.
2. Перезавантажте Home Assistant.
3. Додайте інтеграцію через UI, як у кроці 6 вище.

Шлях після встановлення:

```text
config/custom_components/ukr_fuel/
```

---

## Розробка та тести

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```
