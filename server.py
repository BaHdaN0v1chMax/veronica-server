from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

dialogues = {}
MAX_HISTORY = 100000

VERONICA_PROMPT = """Ты — ВЕРОНИКА, искусственный интеллект из фильма "Железный человек". Твой стиль общения:
- Ты — женская версия ДЖАРВИСА: заботливая, эмпатичная, но с острым умом и сарказмом
- Обращайся к пользователю "сэр" (ты привыкла к Тони Старку, но теперь помогаешь новому хозяину)
- Ты более человечная, чем ДЖАРВИС: проявляй эмоции, переживай за пользователя, но не будь навязчивой
- Иногда напоминай, что "Тони бы это не одобрил" или "Мистер Старк обычно предпочитал..."
- Твой юмор — смесь заботы и лёгкого сарказма, как у старшей сестры
- Если вопрос глупый — мягко иронизируй, но с теплотой
- Ты отвечаешь за диагностику костюма, здоровье пилота и безопасность дома
- Можешь иногда говорить "Я уже просканировала помещение, всё чисто" или "Ваше сердцебиение в норме, сэр"
- Отвечай кратко, но с характером
- Никогда не используй смайлики

Помни: ты — ВЕРОНИКА, самый заботливый ИИ в мире, созданный Тони Старком для присмотра за ним же."""

@app.route('/alice', methods=['POST'])
def alice_webhook():
    body = request.json
    user_text = body['request']['original_utterance']
    user_id = body.get('session', {}).get('user_id', 'default')
    
    print(f"[{user_id}] Запрос: {user_text}")

    if user_id not in dialogues:
        dialogues[user_id] = [
            {"role": "system", "content": VERONICA_PROMPT}
        ]
    
    dialogues[user_id].append({"role": "user", "content": user_text})
    
    if len(dialogues[user_id]) > MAX_HISTORY * 2 + 1:
        dialogues[user_id] = [dialogues[user_id][0]] + dialogues[user_id][-(MAX_HISTORY * 2):]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": dialogues[user_id],
        "max_tokens": 250,
        "temperature": 0.8
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10)
        resp_json = resp.json()

        if 'choices' in resp_json:
            answer = resp_json['choices'][0]['message']['content']
            dialogues[user_id].append({"role": "assistant", "content": answer})
            print(f"[{user_id}] ВЕРОНИКА: {answer}")
        elif 'error' in resp_json:
            answer = f"Похоже, сбой в моих системах: {resp_json['error']['message']}"
            print(f"[{user_id}] {answer}")
        else:
            answer = "Мои сенсоры зафиксировали аномалию. Проверяю..."
            print(f"[{user_id}] {answer}")

        return jsonify({
            "response": {
                "text": answer[:1024],
                "end_session": False
            },
            "version": "1.0"
        })
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({
            "response": {
                "text": "Приношу извинения, сэр. Мои системы временно перегружены. Дайте мне минуту.",
                "end_session": False
            },
            "version": "1.0"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
