from flask import Flask, request
import requests
import os
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
print(f"TOKEN ON START: {TELEGRAM_BOT_TOKEN}", flush=True)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
RESTAURANT_NAME = "Ресторан"

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

conversation_state = {}


@app.route('/')
def index():
    return {
        'status': 'ok',
        'message': 'Telegram Bot Webhook Server is running'
    }, 200


@app.route('/webhook', methods=['POST'])
def webhook():
    print("WEBHOOK CALLED!", flush=True)
    try:
        data = request.get_json()
        print(f"DATA: {data}", flush=True)
        if 'message' not in data:
            print("NO MESSAGE IN DATA", flush=True)
            return {'ok': True}, 200

        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        print(f"DATA: {data}")
        print(f"chat_id: {chat_id}, text: {text}", flush=True)
        print(f"TOKEN: {TELEGRAM_BOT_TOKEN}", flush=True)
        print(f"Message from {chat_id}: {text}")

        if chat_id not in conversation_state:
            conversation_state[chat_id] = {
                'step': 0,
                'client_name': '',
                'visit_frequency': '',
                'rating_food': 0,
                'rating_service': 0,
                'rating_atmosphere': 0,
                'rating_speed': 0,
                'feedback_positive': '',
                'feedback_negative': '',
                'favorite_dish': '',
                'visit_type': ''
            }

        state = conversation_state[chat_id]
        response_text = handle_conversation(chat_id, text, state)
        send_telegram_message(chat_id, response_text)

        return {'ok': True}, 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'ok': True}, 200


def handle_conversation(chat_id, text, state):
    """Полный диалог опроса клиента"""

    # 🔄 ПЕРВОЕ - проверяем /start ДО всех шагов (сброс состояния)
    if text == '/start':
        state.update({
            'step': 1,
            'client_name': '',
            'visit_frequency': '',
            'rating_food': 0,
            'rating_service': 0,
            'rating_atmosphere': 0,
            'rating_speed': 0,
            'feedback_positive': '',
            'feedback_negative': '',
            'favorite_dish': '',
            'visit_type': ''
        })
        return (f"Привет! 👋 Я помощник ресторана \"{RESTAURANT_NAME}\"\n"
                f"Спасибо, что посетили нас! Помогите нам улучшать сервис.\n\n"
                f"Как вас зовут? 👤")

    step = state['step']

    # 🔁 Если опрос уже завершен (step > 10)
    if step > 10:
        return "✅ Опрос завершен! Отправьте /start чтобы начать заново"

    # Шаг 0: Приветствие (если вдруг step=0)
    if step == 0:
        state['step'] = 1
        return (f"Привет! 👋 Я помощник ресторана \"{RESTAURANT_NAME}\"\n"
                f"Спасибо, что посетили нас! Помогите нам улучшать сервис.\n\n"
                f"Как вас зовут? 👤")

    # Шаг 1: Имя клиента
    if step == 1 and state['client_name'] == '':
        if len(text) < 2:
            return "Пожалуйста, введите ваше имя (минимум 2 символа)"
        state['client_name'] = text
        state['step'] = 2
        return (f"Спасибо, {state['client_name']}! 😊\n\n"
                f"Это ваш первый визит к нам?\n"
                f"1️⃣ Первый раз\n"
                f"2️⃣ Бываю иногда\n"
                f"3️⃣ Постоянный клиент")

    # Шаг 2: Частота посещений
    if step == 2 and state['visit_frequency'] == '':
        freq_map = {
            '1': 'Первый раз',
            '2': 'Бываю иногда',
            '3': 'Постоянный клиент'
        }
        if text in freq_map:
            state['visit_frequency'] = freq_map[text]
            state['step'] = 3
            return (f"Спасибо! 🙏\n\n"
                    f"Оцените по шкале 1-5:\n"
                    f"🍽️ Качество блюд? (введите число 1-5)")
        return "Выберите 1, 2 или 3"

    # Шаг 3: Оценка качества блюд
    if step == 3 and state['rating_food'] == 0:
        try:
            rating = int(text)
            if 1 <= rating <= 5:
                state['rating_food'] = rating
                state['step'] = 4
                return "👨‍ Обслуживание? (введите число 1-5)"
            return "Введите число от 1 до 5"
        except:
            return "Пожалуйста, введите число от 1 до 5"

    # Шаг 4: Оценка обслуживания
    if step == 4 and state['rating_service'] == 0:
        try:
            rating = int(text)
            if 1 <= rating <= 5:
                state['rating_service'] = rating
                state['step'] = 5
                return "🏢 Атмосфера в ресторане? (введите число 1-5)"
            return "Введите число от 1 до 5"
        except:
            return "Пожалуйста, введите число от 1 до 5"

    # Шаг 5: Оценка атмосферы
    if step == 5 and state['rating_atmosphere'] == 0:
        try:
            rating = int(text)
            if 1 <= rating <= 5:
                state['rating_atmosphere'] = rating
                state['step'] = 6
                return "⏱️ Скорость подачи блюд? (введите число 1-5)"
            return "Введите число от 1 до 5"
        except:
            return "Пожалуйста, введите число от 1 до 5"

    # Шаг 6: Оценка скорости подачи
    if step == 6 and state['rating_speed'] == 0:
        try:
            rating = int(text)
            if 1 <= rating <= 5:
                state['rating_speed'] = rating
                state['step'] = 7
                return (f"Спасибо за оценки! ⭐\n\n"
                        f"Что вам больше всего понравилось? "
                        f"(опишите одним предложением)")
            return "Введите число от 1 до 5"
        except:
            return "Пожалуйста, введите число от 1 до 5"

    # Шаг 7: Положительный отзыв
    if step == 7 and state['feedback_positive'] == '':
        if len(text) < 5:
            return "Пожалуйста, опишите подробнее (минимум 5 символов)"
        state['feedback_positive'] = text
        state['step'] = 8
        return "Что можно улучшить? (ваши предложения)"

    # Шаг 8: Предложения по улучшению
    if step == 8 and state['feedback_negative'] == '':
        if len(text) < 5:
            return "Пожалуйста, опишите подробнее (минимум 5 символов)"
        state['feedback_negative'] = text
        state['step'] = 9
        return "Какое блюдо вам понравилось больше всего?"

    # Шаг 9: Любимое блюдо
    if step == 9 and state['favorite_dish'] == '':
        if len(text) < 2:
            return "Пожалуйста, назовите блюдо (минимум 2 символа)"
        state['favorite_dish'] = text
        state['step'] = 10
        return (f"С кем вы пришли?\n"
                f"1️⃣ Один\n"
                f"2️⃣ С семьей\n"
                f"3️⃣ С друзьями\n"
                f"4️⃣ Деловой обед")

    # Шаг 10: Завершение и тип визита
    if step == 10 and state['visit_type'] == '':
        visit_map = {
            '1': 'Один',
            '2': 'С семьей',
            '3': 'С друзьями',
            '4': 'Деловой обед'
        }
        if text in visit_map:
            state['visit_type'] = visit_map[text]
            save_to_sheets(chat_id, state)
            state['step'] = 99  # 🔒 Флаг "завершен"
            return (f"Спасибо за ваш отзыв, {state['client_name']}! 🙏\n\n"
                    f"🎟️ Код скидки: THANKFUL10\n"
                    f"Получите 10% скидку на следующий визит! 🎉\n\n"
                    f"Отправьте /start для нового опроса")
        return "Выберите 1, 2, 3 или 4"

    return "Что-то пошло не так. Отправьте /start чтобы начать заново"


def send_telegram_message(chat_id, text):
    """Отправить сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Message sent to {chat_id}")
    except Exception as e:
        print(f"Send error: {str(e)}")


# def analyze_feedback_with_ai(state):
    """AI анализ отзыва клиента"""
    if not openai_client:
        return "AI анализ недоступен"  #

    try:
        feedback_text = f"""
        Клиент: {state['client_name']}
        Частота посещений: {state['visit_frequency']}
        Оценка блюд: {state['rating_food']}/5
        Оценка обслуживания: {state['rating_service']}/5
        Оценка атмосферы: {state['rating_atmosphere']}/5
        Оценка скорости: {state['rating_speed']}/5
        Понравилось: {state['feedback_positive']}
        Улучшить: {state['feedback_negative']}
        Любимое блюдо: {state['favorite_dish']}
        Тип визита: {state['visit_type']}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role":
                "system",
                "content":
                "Ты эксперт по анализу отзывов ресторана. Дай краткий анализ (2-3 предложения): общее впечатление, ключевые моменты, рекомендации для ресторана."
            }, {
                "role": "user",
                "content": feedback_text
            }],
            max_tokens=200)
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI analysis error: {e}")
        return "Ошибка AI анализа"


def ensure_headers_exist(access_token, spreadsheet_id, sheet_name):
    """Добавить заголовки в таблицу если их нет"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A1:M1"

    try:
        response = requests.get(url,
                                headers={
                                    "Authorization": f"Bearer {access_token}",
                                    "Accept": "application/json"
                                },
                                timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("values"):
                return True

        headers = [
            "Дата/Время", "Chat ID", "Имя клиента", "Частота посещений",
            "Оценка блюд", "Оценка обслуживания", "Оценка атмосферы",
            "Оценка скорости", "Что понравилось", "Что улучшить",
            "Любимое блюдо", "Тип визита", "AI Анализ"
        ]

        update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A1:M1?valueInputOption=RAW"

        requests.put(update_url,
                     headers={
                         "Authorization": f"Bearer {access_token}",
                         "Content-Type": "application/json"
                     },
                     json={"values": [headers]},
                     timeout=10)
        print("Headers created")
        return True

    except Exception as e:
        print(f"Headers error: {e}")
        return False


def get_google_access_token():
    """Получить токен доступа через Replit Connector"""
    hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
    repl_identity = os.environ.get("REPL_IDENTITY")
    web_repl_renewal = os.environ.get("WEB_REPL_RENEWAL")

    if repl_identity:
        x_replit_token = f"repl {repl_identity}"
    elif web_repl_renewal:
        x_replit_token = f"depl {web_repl_renewal}"
    else:
        print("No Replit token found")
        return None

    url = f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet"

    try:
        response = requests.get(url,
                                headers={
                                    "Accept": "application/json",
                                    "X_REPLIT_TOKEN": x_replit_token
                                },
                                timeout=10)
        response.raise_for_status()
        data = response.json()

        connection = data.get("items", [{}])[0]
        settings = connection.get("settings", {})

        access_token = settings.get("access_token") or \
                      settings.get("oauth", {}).get("credentials", {}).get("access_token")

        return access_token

    except Exception as e:
        print(f"Failed to get access token: {e}")
        return None


def save_to_sheets(chat_id, state):
    """Сохранить отзыв в Google Sheets с AI анализом"""
    spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
    sheet_name = "otkliks"

    if not spreadsheet_id:
        print("GOOGLE_SHEET_ID not set")
        return False

    access_token = get_google_access_token()
    if not access_token:
        print("Could not get access token")
        return False

    ensure_headers_exist(access_token, spreadsheet_id, sheet_name)

    # ai_analysis = analyze_feedback_with_ai(state)

    try:
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # A
            str(chat_id),  # B
            state['client_name'],  # C
            state['visit_frequency'],  # D
            str(state['rating_food']),  # E
            str(state['rating_service']),  # F
            str(state['rating_atmosphere']),  # G
            str(state['rating_speed']),  # H
            state['feedback_positive'],  # I
            state['feedback_negative'],  # J
            state['favorite_dish'],  # K
            state['visit_type'],  # L
            '',  # M - заполнит GAS
            '',  # N - заполнит GAS
            ''  # O - заполнит GAS
        ]

        url = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A:O:append"
            f"?valueInputOption=RAW&insertDataOption=INSERT_ROWS")

        response = requests.post(url,
                                 headers={
                                     "Authorization": f"Bearer {access_token}",
                                     "Content-Type": "application/json"
                                 },
                                 json={"values": [row_data]},
                                 timeout=15)

        response.raise_for_status()
        print(f"Saved to sheets: {state['client_name']}")
        return True

    except Exception as e:
        print(f"Save error: {str(e)}")


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервера"""
    return {'status': 'ok', 'message': 'Server is running'}, 200


@app.route('/setwebhook', methods=['GET'])
def set_webhook_route():
    """Установить вебхук программно"""
    url = "https://fla.resk-webapp--kiboto30replit.app/webhook"
    webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={url}"

    response = requests.get(webhook_url)
    return response.json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
