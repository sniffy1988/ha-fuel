# Ukrainian Fuel Prices for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/YOUR_GITHUB_USERNAME/ha-ukr-fuel-prices?style=flat-square)](https://github.com/YOUR_GITHUB_USERNAME/ha-ukr-fuel-prices/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

Кастомна інтеграція для **Home Assistant**, яка збирає актуальні середні ціни на пальне в Україні з відкритих джерел (сайт *Мінфін*) для вибраних мереж АЗС (**Укрнафта**, **SOCAR**, **ОККО**, **WOG** та інші) та видів палива.

---

## 🚀 Можливості
* **Динамічний вибір через UI**: під час налаштування ви самі обираєте заправки та види палива (`А-95+`, `А-95`, `А-92`, `ДП`, `Газ`), які хочете моніторити.
* **Автоматичне оновлення**: фонове опитування джерела за розкладом (кожні 4 години).
* **Гнучкість**: підтримка будь-якого оператора та марки палива з таблиці моніторингу в один клік.
* **Надійність**: автоматичне розпізнавання числових значень та коректна обробка відсутності певного виду палива на конкретній заправці.

---

## 📥 Встановлення через HACS (Рекомендовано)

1. Відкрийте ваш **Home Assistant** і перейдіть у **HACS**.
2. Натисніть на три крапки у правому верхньому кутку та виберіть **Користувацькі репозиторії (Custom repositories)**.
3. Вставте посилання на цей репозиторій:
   ```text
   [https://github.com/YOUR_GITHUB_USERNAME/ha-ukr-fuel-prices](https://github.com/YOUR_GITHUB_USERNAME/ha-ukr-fuel-prices)