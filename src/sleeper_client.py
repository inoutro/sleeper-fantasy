import time
import requests

BASE_URL = "https://api.sleeper.app/v1"

# 플레이어 전체 데이터 캐시 (1시간 유효)
_players_cache: dict = {}
_players_cache_time: float = 0
PLAYERS_CACHE_TTL = 3600


def _get(path: str) -> dict | list:
    resp = requests.get(f"{BASE_URL}{path}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_league(league_id: str) -> dict:
    return _get(f"/league/{league_id}")


def get_rosters(league_id: str) -> list:
    return _get(f"/league/{league_id}/rosters")


def get_matchups(league_id: str, week: int) -> list:
    return _get(f"/league/{league_id}/matchups/{week}")


def get_players() -> dict:
    """전체 NBA 플레이어 데이터 (캐시 1시간)"""
    global _players_cache, _players_cache_time
    if time.time() - _players_cache_time > PLAYERS_CACHE_TTL or not _players_cache:
        print("  플레이어 데이터 갱신 중...")
        _players_cache = _get("/players/nba")
        _players_cache_time = time.time()
    return _players_cache


def get_current_week(league_id: str) -> int:
    league = get_league(league_id)
    return league["settings"]["leg"]
