from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/alice', methods=['POST'])
def alice_webhook():
    print("!!! ТЕСТОВЫЙ КОД ЗАПУЩЕН !!!")
    
    body = request.json
    user_text = body.get('request', {}).get('original_utterance', 'пусто')
    
    print(f"Запрос: {user_text}")
    
    return jsonify({
        "response": {
            "text": f"Вы сказали: {user_text}",
            "end_session": False
        },
        "version": "1.0"
    })

if __name__ == '__main__':
    print("Сервер запущен!")
    app.run(host='0.0.0.0', port=10000)
