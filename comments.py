import requests

API_URL = "http://127.0.0.1:8080"

def send_scenario(requestor_name, topic_text):
    """Отправляет тему на сервер Flask"""
    try:
        payload = {"author": requestor_name, "topic": topic_text}
        response = requests.post(f"{API_URL}/submit", json=payload)

        if response.status_code == 200:
            print(f"✅ Тема '{topic_text}' отправлена.")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

if __name__ == "__main__":
    while True:
        topic = input("Введите тему (или 'exit' для выхода): ").strip()
        if topic.lower() == "exit":
            break
        send_scenario("User", topic)
