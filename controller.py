import requests
import asyncio

API_URL = "http://127.0.0.1:8080/"
TTS_SERVER = "http://127.0.0.1:3000/generate_voice"

async def generate_story():
    """Запрашивает тему и отправляет её в OpenRouter.ai через Flask API"""
    response = requests.get(f"{API_URL}/get-item")
    data = response.json()

    if not data["status"]:
        print("❌ Нет новых тем!")
        return

    topic = data["topic"]
    print(f"🎙 Генерация на тему: {topic}")

    response = requests.post(f"{API_URL}/generate", json={"topic": topic})

    try:
        if response.status_code == 200:
            story = response.json().get("story", "Ошибка генерации!")
        else:
            print(f"❌ Ошибка генерации: {response.status_code}, {response.text}")
            return
    except ValueError as e:
        print(f"Ошибка декодирования JSON: {e}")
        story = "Ошибка обработки данных!"

    print(f"📜 Сценарий:\n{story}")

    dialogues = parse_dialogue(story)
    for dialogue in dialogues:
        audio_path = request_voice(dialogue["character"], dialogue["text"])
        print(f"🔊 Аудио файл: {audio_path}")

def parse_dialogue(text):
    """Парсит текст диалога и возвращает список реплик."""
    lines = text.split("\n")
    dialogues = []
    
    for line in lines:
        parts = line.split(":")
        if len(parts) == 2:
            character = parts[0].strip()
            dialogue = parts[1].strip()
            dialogues.append({"character": character, "text": dialogue})

    return dialogues

def request_voice(character, text):
    """Отправляет текст в TTS и получает ссылку на аудиофайл."""
    speaker_map = {
        "Владимир Жириновский": "zhirinovskiy",
        "Дмитрий Гордон": "gordon"
    }

    speaker = speaker_map.get(character, "zhirinovskiy")

    payload = {"text": text, "speaker": speaker}

    try:
        response = requests.post(TTS_SERVER, json=payload, timeout=60)
        return response.json().get("audio_wav_path", "❌ Ошибка генерации озвучки")
    except Exception as e:
        print(f"❌ Ошибка при запросе к TTS: {e}")
        return None

async def main():
    while True:
        await generate_story()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
