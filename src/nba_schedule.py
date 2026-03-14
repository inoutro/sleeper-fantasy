import time

_schedule_cache: set = set()
_schedule_cache_time: float = 0
SCHEDULE_CACHE_TTL = 1800  # 30분


def get_todays_game_teams() -> set[str]:
    """오늘 경기하는 NBA 팀 약어 집합 반환 (예: {'LAL', 'GSW', 'BOS'})"""
    global _schedule_cache, _schedule_cache_time

    if time.time() - _schedule_cache_time < SCHEDULE_CACHE_TTL and _schedule_cache:
        return _schedule_cache

    try:
        from nba_api.live.nba.endpoints import scoreboard
        board = scoreboard.ScoreBoard()
        games = board.games.get_dict()

        teams = set()
        for game in games:
            teams.add(game["homeTeam"]["teamTricode"])
            teams.add(game["awayTeam"]["teamTricode"])

        _schedule_cache = teams
        _schedule_cache_time = time.time()
        return teams

    except Exception as e:
        print(f"  [경고] NBA 스케줄 로딩 실패: {e}")
        return _schedule_cache  # 이전 캐시 반환
