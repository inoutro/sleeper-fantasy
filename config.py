import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

USER_ID = os.getenv("SLEEPER_USER_ID")
USERNAME = os.getenv("SLEEPER_USERNAME")

def _required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"필수 환경변수 누락: {key} (.env 파일을 확인하세요)")
    return value


LEAGUES = [
    {
        "id": _required("LEAGUE1_ID"),
        "name": "This is for you!",
        "roster_id": int(_required("LEAGUE1_ROSTER_ID")),
    },
    {
        "id": _required("LEAGUE2_ID"),
        "name": "모래지옥 NBA Dynasty 판타지 리그",
        "roster_id": int(_required("LEAGUE2_ROSTER_ID")),
    },
]

# 알람을 보낼 부상 상태 목록
ALERT_INJURY_STATUSES = {"OUT", "DTD", "DOUBTFUL", "QUESTIONABLE", "GTD", "IR", "SUSP"}

# 폴링 주기 (초)
CHECK_INTERVAL = 300  # 5분

# 상태 저장 파일
STATE_FILE = "state.json"
