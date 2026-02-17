# 🍽️ Restaurant Feedback Bot

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-webhook-lightgrey?logo=flask)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?logo=telegram)
![Google Sheets](https://img.shields.io/badge/Google-Sheets-green?logo=google-sheets)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-orange?logo=openai)
![Replit](https://img.shields.io/badge/Deployed-Replit-orange?logo=replit)
![Status](https://img.shields.io/badge/status-active-success.svg)

> Telegram-бот для автоматизированного сбора обратной связи от посетителей ресторана с интеграцией в Google Sheets и AI-анализом отзывов

**Telegram:** [@oprosnik_rest_bot](https://t.me/oprosnik_rest_bot)

---

## 📋 О проекте

**Restaurant Feedback Bot** — это автоматизированное решение для сбора и анализа отзывов гостей ресторана в реальном времени. Бот ведёт пошаговый диалог с посетителем, собирает структурированную обратную связь, сохраняет данные в Google Таблицы и автоматически генерирует AI-аналитику по каждому отзыву.

---

## ✨ Функционал

### 💬 Опросник (10 шагов)
- Персонализированное приветствие по имени
- Определение типа посетителя (первый раз / бывало иногда / постоянный клиент)
- Оценка по 4 метрикам (шкала 1–5): качество блюд, обслуживание, атмосфера, скорость подачи
- Открытые вопросы: что понравилось, что улучшить, любимое блюдо
- Определение типа визита: один, с семьёй, с друзьями, деловой обед
- Промокод на скидку по завершении опроса

### 📊 Google Sheets интеграция
Каждый ответ сохраняется в таблицу с полями:

| Поле | Описание |
|------|----------|
| `time_stamp` | Дата и время отзыва |
| `telegram_id` | ID пользователя |
| `Имя` | Имя посетителя |
| `Частота посещений` | Тип гостя |
| `Качество блюд` | Оценка 1–5 |
| `Оценка обслуживания` | Оценка 1–5 |
| `Оценка атмосферы` | Оценка 1–5 |
| `Оценка скорости` | Оценка 1–5 |
| `Что понравилось` | Текст |
| `Что улучшить` | Текст |
| `Любимое блюдо` | Текст |
| `Тип визита` | Категория |
| `тональность` | AI-анализ |
| `сегмент клиента` | AI-анализ |
| `инсайты и рекомендации` | AI-анализ |

### 🤖 AI-анализ отзывов
После каждого опроса OpenAI автоматически генерирует:
- **Тональность** — positive / neutral / negative
- **Сегмент клиента** — New / Regular / AtRisk
- **Инсайты и рекомендации** — конкретные советы по улучшению сервиса на основе отзыва

---

## 🖼️ Скриншоты

### Диалог с ботом
![Bot conversation](screenshots/bot-conversation.png)

### Данные в Google Sheets с AI-анализом
![Google Sheets](screenshots/google-sheets-data.png)

---

## 🛠️ Технологии

- **Python 3.11** — основной язык
- **Flask** — webhook-сервер для получения сообщений от Telegram
- **python-telegram-bot / Telegram Bot API** — взаимодействие с Telegram
- **Google Apps Script** — запись данных в Google Sheets
- **OpenAI API (GPT)** — AI-анализ отзывов
- **Replit Autoscale** — деплой и хостинг 24/7

---

## 🏗️ Архитектура

```
Telegram User
     │
     ▼
Telegram Bot API
     │  (webhook POST)
     ▼
Flask Server (main.py)
     │
     ├──► handle_conversation() — логика опроса
     │         │
     │         └──► conversation_state{} — состояние диалога
     │
     ├──► send_telegram_message() — ответы пользователю
     │
     ├──► analyze_feedback_with_ai() — OpenAI анализ
     │
     └──► save_to_sheets() — Google Apps Script → Google Sheets
```

---

## 🚀 Установка и запуск

### Требования
- Python 3.11+
- Telegram Bot Token (от [@BotFather](https://t.me/botfather))
- OpenAI API Key
- Google Apps Script URL (для записи в Sheets)

### Локальный запуск

```bash
git clone https://github.com/KirillTomenko/-Restaurant-Feedback-Bot.git
cd -Restaurant-Feedback-Bot
pip install -r requirements.txt
```

Создайте файл `.env`:
```env
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
GAS_URL=your_google_apps_script_url
```

Запустите:
```bash
python main.py
```

Настройте webhook (замените URL):
```
https://api.telegram.org/botВАШ_ТОКЕН/setWebhook?url=https://ваш-сервер.com/webhook
```

### Деплой на Replit

1. Форкните репозиторий на Replit
2. Добавьте Secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `GAS_URL`
3. Нажмите **Deploy** → **Autoscale**
4. Установите webhook на полученный URL

---

## 📁 Структура проекта

```
├── main.py              # Flask-сервер + логика бота
├── conversation.py      # Вспомогательные функции диалога
├── sheets_handler.py    # Модуль работы с Google Sheets
├── requirements.txt     # Зависимости Python
├── .replit              # Конфигурация Replit
├── Procfile             # Команда запуска
└── screenshots/         # Скриншоты для README
```

---

## 🔮 Планы развития

- [ ] Inline-кнопки вместо ввода цифр (1, 2, 3...)
- [ ] Уведомления менеджеру при низких оценках
- [ ] Dashboard с визуализацией статистики
- [ ] Мультиязычность (RU / EN)
- [ ] Интеграция с CRM

---

## 📄 Лицензия

MIT License — используйте свободно для своих проектов.

---

<div align="center">

**Сделано с ❤️ для улучшения качества сервиса**

[🤖 Попробовать бота](https://t.me/oprosnik_rest_bot) · [⭐ Поставить звезду](https://github.com/KirillTomenko/-Restaurant-Feedback-Bot)

</div>
