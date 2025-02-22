from flask import Flask, request, jsonify
import requests
import sqlite3
import os

app = Flask(__name__)

# Заменяем OpenAI API на OpenRouter.ai
OPENROUTER_API_KEY = "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"
MODEL_NAME = "deepseek/deepseek-r1:free"

DB_FILE = "database.db"

def init_db():
    """Создаёт SQLite базу данных, если её нет."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                topic TEXT
            )
        """)
        conn.commit()

@app.route("/submit", methods=["POST"])
def submit_topic():
    """Принимает тему и сохраняет в базу данных."""
    data = request.get_json()
    author = data.get("author", "Unknown")
    topic = data.get("topic", "")

    if not topic:
        return jsonify({"error": "Тема не может быть пустой"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO topics (author, topic) VALUES (?, ?)", (author, topic))
        conn.commit()

    return jsonify({"success": True, "message": "Тема сохранена!"})

@app.route("/get-item", methods=["GET"])
def get_topic():
    """Выдаёт тему для генерации диалога."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, topic FROM topics ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()

        if row:
            topic_id, topic = row
            cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
            conn.commit()
            return jsonify({"status": True, "topic": topic})

    return jsonify({"status": False})

@app.route("/story/getScenario", methods=["GET"])
def get_scenario():
    """Возвращает сгенерированный сценарий диалога."""
    # Пример сгенерированного диалога
    scenario = [
        {"text": "Жириновский: Вы что, с ума сошли? Я – самый великий политик!", "image": "path_to_zhirinovsky_image.jpg"},
        {"text": "Гордон: Но Жириновский, ты сам же сказал, что у нас все схвачено!", "image": "path_to_gordon_image.jpg"},
        {"text": "Жириновский: Я всегда прав! Я – лидер!", "image": "path_to_zhirinovsky_image.jpg"},
        {"text": "Гордон: Ты что, вообще не в себе, Жирик?", "image": "path_to_gordon_image.jpg"}
    ]

    return jsonify({"status": True, "scenario": scenario})

@app.route("/generate", methods=["POST"])
def generate_ai_story():
    """Отправляет запрос в OpenRouter.ai для генерации текста."""
    data = request.get_json()
    topic = data.get("topic", "")

    if not topic:
        return jsonify({"error": "Тема не указана"}), 400

    prompt = f"Создай комедийную беседу между Владимиром Жириновским и Дмитрием Гордоном. Тема: {topic}."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if response.status_code == 200:
        story = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Ошибка генерации!")
        return jsonify({"story": story})
    else:
        return jsonify({"error": f"Ошибка API: {response.status_code}, {response.text}"}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
