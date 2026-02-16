"""
Keep Alive Module for Replit
Создает простой веб-сервер для предотвращения засыпания бота на бесплатном плане Replit
"""

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Restaurant Feedback Bot - Status</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .status {
                    font-size: 24px;
                    margin: 20px;
                }
                .emoji {
                    font-size: 48px;
                }
            </style>
        </head>
        <body>
            <div class="emoji">🤖</div>
            <h1>Restaurant Feedback Bot</h1>
            <div class="status">✅ Bot is running!</div>
            <p>Telegram: <a href="https://t.me/oprosnik_rest_bot" style="color: white;">@oprosnik_rest_bot</a></p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint для мониторинга"""
    return {"status": "ok", "bot": "running"}

def run():
    """Запуск Flask приложения"""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запуск веб-сервера в отдельном потоке"""
    t = Thread(target=run)
    t.daemon = True  # Поток завершится при завершении основной программы
    t.start()
    print("Keep-alive web server started on port 8080")

if __name__ == '__main__':
    # Для тестирования
    run()
