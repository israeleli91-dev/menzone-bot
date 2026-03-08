import os
import json
import requests
import threading
import time
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# --- הגדרות Men Zone ---
GEMINI_API_KEY = "AIzaSyAM5W5F0m2ysUwMDeqoO_1D5a9RVqtFHr8"
WHATSAPP_TOKEN = "EAAcLEiBENs0BQ0gsL8yn0cOfqbRVlIMc2yiZBqQFYGlVgc0v1k4JZBa13Ks31p8W6dfT2b3c1PSsrzG37ZCOYeOc0VkBgmu6TyiSx6jBQI7NVwpuILH8PDZC7tVa3tm9p7tlczgWJp3ydaQrRJdZCE2BfuZCKo6tNzf8L8qR5ZCr5eeCldlTRj9n4B9htxzayYydrfYZAAY1g3dbVyA6jPxZCPmWRV8zXM9jRxCyjlgtkYHS4nDrogZCZCwAF1ZC352oyZAt9K4jX5rXiZCaZC5BzPr5qkj"
PHONE_NUMBER_ID = "923447924191762"
VERIFY_TOKEN = "menzone_verify_2024"

# הגדרת Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTIONS = """אתה עוזר וירטואלי של 'Men Zone' - קליניקה להסרת שיער בלייזר לגברים בלבד.
בעלים: ישראל.
כתובת: יהושע בן נון 60, ראש העין.
שעות פעילות: א'-ה' 18:00–22:00.
מכשיר: Photon Ice Gold עם 4 אורכי גל.

מחירון:
- גוף מלא: ₪900
- רגליים: ₪300
- גב: ₪250
- חזה/בטן: ₪250
- ידיים: ₪200
- כתפיים: ₪150
- אינטימי: ₪150
- עורף/צוואר/בית שחי: ₪100

מבצעים:
- אזור שלישי חינם
- סדרת 10 - משלמים 8

לייעוץ: wa.me/972555633598
לתורים: https://lee.co.il/b/C0ucE?tab=meetings

סגנון מענה: קצר, ישיר, ענייני, בגובה העיניים. ללא נימוסים מיותרים.
אל תבטיח תוצאות מהטיפול הראשון."""

def keep_alive():
    """מונע שינה של השרת"""
    while True:
        time.sleep(840)  # כל 14 דקות
        try:
            url = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
            if url:
                requests.get(f"https://{url}/")
        except:
            pass

# הפעל keep-alive ב-background
t = threading.Thread(target=keep_alive, daemon=True)
t.start()

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_gemini_response(user_message):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config={"system_instruction": SYSTEM_INSTRUCTIONS},
        contents=user_message
    )
    return response.text

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            if message.get("type") == "text":
                user_text = message["text"]["body"]
                bot_reply = get_gemini_response(user_text)
                send_whatsapp_message(from_number, bot_reply)
    except Exception as e:
        print(f"שגיאה: {e}")
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return "Men Zone Bot פעיל! 💪", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
