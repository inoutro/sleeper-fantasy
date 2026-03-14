#!/usr/bin/env python3
import time
from datetime import datetime

import config
from src.monitor import run_once


def main():
    print("=" * 50)
    print(" Sleeper NBA Fantasy 모니터 시작")
    print(f" 유저: {config.USERNAME}")
    print(f" 리그: {', '.join(l['name'] for l in config.LEAGUES)}")
    print(f" 체크 주기: {config.CHECK_INTERVAL}초")
    print("=" * 50)
    print(" Ctrl+C 로 종료\n")

    while True:
        try:
            run_once()
        except Exception as e:
            print(f"\n[오류] {e}")

        try:
            next_check = datetime.now().strftime("%H:%M:%S")
            print(f" 다음 체크: {config.CHECK_INTERVAL}초 후 ({next_check} 기준)")
            time.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n모니터 종료.")
            break


if __name__ == "__main__":
    main()
