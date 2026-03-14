import json
import os
from datetime import date

import config
from src import sleeper_client, nba_schedule, notifier

# 부상 심각도 순서 (높을수록 심각)
INJURY_SEVERITY = {
    "OUT": 5,
    "IR": 5,
    "SUSP": 4,
    "DTD": 3,
    "DOUBTFUL": 3,
    "QUESTIONABLE": 2,
    "GTD": 1,
}


def load_state() -> dict:
    if os.path.exists(config.STATE_FILE):
        with open(config.STATE_FILE, "r") as f:
            return json.load(f)
    return {"injury_statuses": {}, "lineup_alerts": {}}


def save_state(state: dict):
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _get_player_label(player: dict) -> str:
    name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
    team = player.get("team") or "FA"
    pos = player.get("position") or ""
    return f"{name} ({team}/{pos})"


def check_injuries(state: dict, players: dict, roster_player_ids: list[str], league_name: str):
    """로스터 선수 부상 상태 변경 감지"""
    prev_statuses: dict = state.get("injury_statuses", {})
    updated_statuses = dict(prev_statuses)
    changed = False

    for pid in roster_player_ids:
        player = players.get(pid)
        if not player:
            continue

        current_status = player.get("injury_status")  # None이면 정상
        prev_status = prev_statuses.get(pid)

        if current_status == prev_status:
            continue

        # 상태가 바뀐 경우
        label = _get_player_label(player)
        changed = True
        updated_statuses[pid] = current_status

        if current_status is None:
            # 부상 해제
            notifier.send(
                title=f"✅ 부상 해제 [{league_name}]",
                message=f"{label} — {prev_status} → 정상",
                urgent=False,
            )
        elif current_status in config.ALERT_INJURY_STATUSES:
            severity = INJURY_SEVERITY.get(current_status, 0)
            urgent = severity >= 3  # DTD 이상이면 긴급
            body_part = player.get("injury_body_part") or "미상"
            notes = player.get("injury_notes") or ""
            detail = f"{body_part}" + (f" - {notes}" if notes else "")
            notifier.send(
                title=f"⚠️ 부상 알람 [{league_name}]",
                message=f"{label} → {current_status} ({detail})",
                urgent=urgent,
            )

    if changed:
        state["injury_statuses"] = updated_statuses


def check_lineup(state: dict, players: dict, league: dict, week: int):
    """오늘 경기 있는 벤치 선수 & 결장 스타터 감지"""
    league_id = league["id"]
    league_name = league["name"]
    roster_id = league["roster_id"]
    today_str = date.today().isoformat()

    # 오늘 이미 보낸 알람 목록
    sent_today: list = state.get("lineup_alerts", {}).get(today_str, [])

    # 오늘 경기하는 팀
    teams_playing = nba_schedule.get_todays_game_teams()
    if not teams_playing:
        return

    # 이번 주 매치업에서 내 로스터 찾기
    matchups = sleeper_client.get_matchups(league_id, week)
    my_matchup = next((m for m in matchups if m["roster_id"] == roster_id), None)
    if not my_matchup:
        return

    starters = set(my_matchup.get("starters") or [])
    all_players = set(my_matchup.get("players") or [])
    bench = all_players - starters

    # 1) 벤치 선수 중 오늘 경기 있는 선수
    for pid in bench:
        if pid in sent_today:
            continue
        player = players.get(pid)
        if not player:
            continue
        team = player.get("team")
        injury = player.get("injury_status")
        if team in teams_playing and injury not in {"OUT", "IR", "SUSP"}:
            label = _get_player_label(player)
            notifier.send(
                title=f"📋 벤치 선수 출전 가능 [{league_name}]",
                message=f"{label} — 오늘 경기 있음 (벤치 중)",
                urgent=False,
            )
            sent_today.append(pid)

    # 2) 스타터 중 OUT/DTD인데 오늘 경기가 있는 경우
    for pid in starters:
        alert_key = f"starter_out_{pid}"
        if alert_key in sent_today:
            continue
        player = players.get(pid)
        if not player:
            continue
        team = player.get("team")
        injury = player.get("injury_status")
        if team in teams_playing and injury in {"OUT", "DTD", "DOUBTFUL", "IR"}:
            label = _get_player_label(player)
            notifier.send(
                title=f"🚨 스타터 결장 위험 [{league_name}]",
                message=f"{label} → {injury}, 오늘 경기 있음! 교체 검토 필요",
                urgent=True,
            )
            sent_today.append(alert_key)

    state.setdefault("lineup_alerts", {})[today_str] = sent_today


def run_once():
    """한 번 전체 체크 실행"""
    print(f"\n[체크 중...]", end="", flush=True)
    state = load_state()
    players = sleeper_client.get_players()

    for league in config.LEAGUES:
        try:
            week = sleeper_client.get_current_week(league["id"])
            roster = sleeper_client.get_rosters(league["id"])
            my_roster = next(
                (r for r in roster if r["roster_id"] == league["roster_id"]), None
            )
            if not my_roster:
                continue

            all_player_ids = (my_roster.get("players") or []) + (my_roster.get("taxi") or [])

            check_injuries(state, players, all_player_ids, league["name"])
            check_lineup(state, players, league, week)

        except Exception as e:
            print(f"\n  [{league['name']}] 오류: {e}")

    save_state(state)
    print(" 완료")
