from flask import Flask, request
import requests, os, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GROUP_ID  = os.environ.get("GROUP_ID", "")
BASE      = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send(chat_id, text, parse_mode="HTML"):
    try:
        requests.post(f"{BASE}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                      timeout=10)
    except Exception as e:
        logging.error(f"send error: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg  = data.get("message") or data.get("channel_post")
    if not msg:
        return "ok"

    text      = msg.get("text", "")
    chat      = msg.get("chat", {})
    chat_id   = str(chat.get("id", ""))
    chat_type = chat.get("type", "")
    frm       = msg.get("from", {})
    name      = (frm.get("first_name","") + " " + frm.get("last_name","")).strip() or frm.get("username","알 수 없음")
    now       = datetime.now().strftime("%H:%M:%S")

    # 그룹 메시지는 전달하지 않음 (무한루프 방지)
    if chat_type in ("group", "supergroup", "channel"):
        return "ok"

    if not text:
        return "ok"

    # 그룹으로 전달
    forward = (f"📨 <b>새 메시지</b>\n"
               f"👤 {name}  |  🕐 {now}\n"
               f"─────────────\n"
               f"{text}")
    send(GROUP_ID, forward)

    # 발신자에게 확인 메시지
    send(chat_id, "✅ 메시지가 전달되었습니다.")
    return "ok"

@app.route("/set_webhook")
def set_webhook():
    """배포 후 한 번만 호출 — webhook 등록"""
    host = request.host_url.rstrip("/")
    url  = f"{host}/webhook"
    r    = requests.get(f"{BASE}/setWebhook", params={"url": url})
    return r.json()

@app.route("/")
def index():
    return "✅ K-ALPHA Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
