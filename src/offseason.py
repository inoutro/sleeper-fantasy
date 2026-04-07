from datetime import date

from src import sleeper_client

TOP_FA_COUNT = 10
TOP_ROOKIE_COUNT = 5
UNRANKED_THRESHOLD = 9999990


def get_owned_player_ids(league_id: str) -> set[str]:
    """리그 전체 로스터에 소속된 선수 ID 집합 (택시/IR 포함)"""
    rosters = sleeper_client.get_rosters(league_id)
    owned: set[str] = set()
    for roster in rosters:
        for field in ("players", "taxi", "reserve"):
            owned.update(roster.get(field) or [])
    return owned


def _is_active_nba_player(p: dict) -> bool:
    return bool(p.get("team")) and p.get("active") is not False


def _rank(p: dict) -> int:
    r = p.get("search_rank")
    return r if (r and r < UNRANKED_THRESHOLD) else 999999


def _player_line(p: dict) -> str:
    name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
    team = p.get("team") or "FA"
    pos = p.get("position") or "?"
    injury = p.get("injury_status")
    rank = p.get("search_rank")

    label = f"{name} ({pos}/{team})"
    if injury:
        label += f" [{injury}]"
    if rank and rank < UNRANKED_THRESHOLD:
        label += f" — #{rank}"
    return label


def generate_report(league: dict, players: dict) -> str:
    owned = get_owned_player_ids(league["id"])

    fa_players = [
        p for pid, p in players.items()
        if pid not in owned and _is_active_nba_player(p) and _rank(p) < 999999
    ]
    fa_players.sort(key=_rank)

    notable = fa_players[:TOP_FA_COUNT]
    rookies = [p for p in fa_players if p.get("years_exp", 1) == 0][:TOP_ROOKIE_COUNT]

    lines = [f"📅 {date.today().strftime('%Y-%m-%d')} 기준\n"]

    if notable:
        lines.append("⭐ 주목 FA (판타지 순위 상위)")
        for i, p in enumerate(notable, 1):
            lines.append(f"  {i}. {_player_line(p)}")

    if rookies:
        lines.append("\n🌱 루키 FA (미소유)")
        for i, p in enumerate(rookies, 1):
            lines.append(f"  {i}. {_player_line(p)}")

    if not notable and not rookies:
        lines.append("주목할 FA 없음")

    return "\n".join(lines)
