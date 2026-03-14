import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send(title: str, message: str, urgent: bool = False):
    timestamp = datetime.now().strftime("%H:%M")
    tag = "🚨" if urgent else "🔔"

    # 텔레그램 알림
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        text = f"*{title}*\n{message}"
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"},
                timeout=5,
            )
        except Exception as e:
            print(f"  [텔레그램 전송 실패] {e}")

    # 터미널 출력
    print(f"\n{tag} [{timestamp}] {title}")
    print(f"   {message}")
