from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
     
# Ваши данные (замените на реальные)
TELEGRAM_BOT_TOKEN = "8282469899:AAH2Rm80lvV7u5vgGufH4fmpV5Qq_OjoYGI"
RESTAURANT_NAME = "Delicatesy"
GAS_URL = "https://script.google.com/macros/s/AKfycbz9v4zGTtFhOsGYM31_WA3x-42_08Uxpdo66N53ntCnAqMv-nZh8gYXANtOHQx7Zc6BRw/exec"

# Файл для хранения состояния диалогов
STATE_FILE = "conversation_states.json"

def load_states():
    """Загрузить состояние из файла"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_states(states):
    """Сохранить состояние в файл"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(states, f, ensure_ascii=False, indent=2)

def get_initial_state():
    """Начальное состояние для нового пользователя"""
    return {
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

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if 'message' not in data:
            return {'ok': True}, 200
        
        message = data['message']
        chat_id = str(message['chat']['id'])
        text = message.get('text', '').strip()
        
        print(f"Message from {chat_id}: {text}")
        
        # Загрузить состояния
        states = load_states()
        
        # Если новый пользователь - создать состояние
        if chat_id not in states:
            states[chat_id] = get_initial_state()
        
        state = states[chat_id]
        response_text = handle_conversation(chat_id, text, state)
        
        # Сохранить обновленное состояние
        states[chat_id] = state
        save_states(states)
        
        # Отправить ответ в Telegram
        send_telegram_message(chat_id, response_text)
        
        return {'ok': True}, 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'ok': True}, 200


def handle_conversation(chat_id, text, state):
    """Полный диалог опроса клиента"""
    step = state['step']
    
    # Шаг 0: Приветствие
    if step == 0:
        if text == '/start':
            state['step'] = 1
            return (f"Привет! 👋 Я помощник ресторана \"{RESTAURANT_NAME}\"\n"
                   f"Спасибо, что посетили нас! Помогите нам улучшать сервис.\n\n"
                   f"Как вас зовут? 👤")
        return "Отправьте /start для начала"
    
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
                return "👨‍💼 Обслуживание? (введите число 1-5)"
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
            
            # Сохранить в Google Sheets
            save_to_sheets(chat_id, state)
        
            # Завершить опрос (step 11 = завершено)
            state['step'] = 11
            
            return (f"Спасибо за ваш отзыв, {state['client_name']}! 🙏\n\n"
                   f"🎟️ Код скидки: THANKFUL10\n"
                   f"Получите 10% скидку на следующий визит! 🎉")
        return "Выберите 1, 2, 3 или 4"
    
    # Шаг 11: Опрос завершен - ждем новой команды /start
    if step == 11:
        if text == '/start':
            # Начать новый опрос - сбросить состояние
            new_state = get_initial_state()
            state.update(new_state)
            state['step'] = 1
            return (f"Привет! 👋 Новый опрос!\n\n"
                   f"Как вас зовут? 👤")
        return (f"Опрос уже завершен!\n"
               f"Напишите /start чтобы пройти опрос заново")
    
    return "✅ Опрос завершен! Спасибо!"


def send_telegram_message(chat_id, text):
    """Отправить сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Message sent to {chat_id}")
    except Exception as e:
        print(f"Send error: {str(e)}")


def save_to_sheets(chat_id, state):
    """Сохранить отзыв в Google Sheets через Google Apps Script"""
    try:
        payload = {
            'action': 'save',
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id,
            'client_name': state['client_name'],
            'visit_frequency': state['visit_frequency'],
            'rating_food': state['rating_food'],
            'rating_service': state['rating_service'],
            'rating_atmosphere': state['rating_atmosphere'],
            'rating_speed': state['rating_speed'],
            'feedback_positive': state['feedback_positive'],
            'feedback_negative': state['feedback_negative'],
            'favorite_dish': state['favorite_dish'],
            'visit_type': state['visit_type']
        }
        
        print(f"Saving to sheets: {state['client_name']}")
        response = requests.post(GAS_URL, json=payload, timeout=10)
        print(f"Sheets response: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"Save error: {str(e)}")

def reset_states():
    """Очистить все состояния диалогов"""
    try:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("States file deleted successfully")
        return {'ok': True, 'message': 'All conversation states reset'}, 200
    except Exception as e:
        return {'ok': False, 'error': str(e)}, 500



@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервера"""
    return {'status': 'ok', 'message': 'Server is running'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
