# Sleeper NBA Fantasy Monitor

Sleeper NBA 판타지 리그의 부상 알람, 라인업 알람, 비시즌 FA 리포트를 텔레그램으로 받아보는 모니터링 툴입니다.

## 알람 종류

### 시즌 중 (실시간 모니터링)

| 알람 | 조건 |
|------|------|
| ⚠️ 부상 알람 | 로스터 선수의 부상 상태 변경 시 |
| ✅ 부상 해제 | 부상 → 정상 복귀 시 |
| 📋 벤치 선수 출전 가능 | 벤치 선수 팀이 오늘 경기 있을 때 |
| 🚨 스타터 결장 위험 | 스타터가 OUT/DTD 상태인데 오늘 경기 있을 때 |

### 비시즌 (주간 FA 리포트)

| 알람 | 내용 |
|------|------|
| ⭐ 주목 FA | 리그 내 미소유 선수 중 판타지 순위 상위 10명 |
| 🌱 루키 FA | 리그 내 미소유 루키 선수 상위 5명 |

## 설치 및 설정

### 1. 의존성 설치

```bash
# uv 사용 (권장)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# 또는 pip
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일 생성 후 값 입력:

```bash
cp .env.example .env
```

| 변수명 | 설명 |
|--------|------|
| `TELEGRAM_BOT_TOKEN` | BotFather에서 발급받은 봇 토큰 |
| `TELEGRAM_CHAT_ID` | 알람을 받을 텔레그램 채팅 ID |
| `SLEEPER_USER_ID` | Sleeper 유저 ID |
| `SLEEPER_USERNAME` | Sleeper 유저네임 |
| `LEAGUE2_ID` | Dynasty 리그 ID |
| `LEAGUE2_ROSTER_ID` | Dynasty 리그에서 내 roster ID |

> Sleeper 유저 ID 확인: `https://api.sleeper.app/v1/user/<유저네임>`
> Sleeper 리그 ID 확인: `https://api.sleeper.app/v1/user/<유저ID>/leagues/nba/2025`
> 텔레그램 Chat ID 확인: 봇에게 메시지 전송 후 `https://api.telegram.org/bot<TOKEN>/getUpdates`

### 3. 실행

```bash
# 시즌 중 — 5분 주기 실시간 모니터링
python main.py

# 시즌 중 — 한 번만 실행
python check.py

# 비시즌 — 주간 FA 리포트
python offseason_check.py
```

## GitHub Actions로 자동 실행 (추천)

컴퓨터를 켜두지 않아도 GitHub이 자동으로 실행해줍니다.

| 워크플로우 | 파일 | 실행 주기 |
|---|---|---|
| 시즌 중 부상/라인업 모니터링 | `monitor.yml` | 수동 실행만 (비시즌 비활성화) |
| 비시즌 주간 FA 리포트 | `offseason.yml` | 매주 월요일 오후 6시 (KST) |

### 설정 방법

1. 이 레포를 GitHub에 push
2. 레포 **Settings → Secrets and variables → Actions** 에서 위 환경변수를 Secrets으로 등록
3. Actions 탭에서 워크플로우 확인

## 프로젝트 구조

```
├── main.py                # 로컬 실행 진입점 (폴링 루프)
├── check.py               # 한 번만 실행하는 진입점 (시즌 중 GitHub Actions용)
├── offseason_check.py     # 비시즌 주간 FA 리포트 진입점
├── config.py              # 설정 로드
├── requirements.txt
├── .env                   # 환경변수 (git 제외)
├── .env.example           # 환경변수 예시
└── src/
    ├── sleeper_client.py  # Sleeper API 호출
    ├── nba_schedule.py    # 오늘 NBA 경기 조회
    ├── notifier.py        # 텔레그램 알림 전송
    ├── monitor.py         # 부상/라인업 체크 로직
    └── offseason.py       # 비시즌 FA 리포트 로직
```
