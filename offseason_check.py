#!/usr/bin/env python3
"""비시즌 주간 FA 리포트 — cron으로 매주 실행"""
from datetime import date

import config
from src import sleeper_client, notifier, offseason


def main():
    print(f"[비시즌 FA 리포트] {date.today()}")
    players = sleeper_client.get_players()

    for league in config.LEAGUES:
        try:
            report = offseason.generate_report(league, players)
            notifier.send(
                title=f"[{league['name']}] 주간 FA 리포트",
                message=report,
                urgent=False,
            )
            print(f"  [{league['name']}] 전송 완료")
        except Exception as e:
            print(f"  [{league['name']}] 오류: {e}")


if __name__ == "__main__":
    main()
