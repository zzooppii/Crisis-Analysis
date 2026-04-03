# history.py — 주간 스냅샷 저장 및 이전 데이터 조회

import json
import os

from config import HISTORY_FILE


def load_history() -> list[dict]:
    """history.json 로드. 파일 없으면 빈 리스트 반환."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def get_previous_week(history: list[dict], today: str) -> dict | None:
    """오늘 날짜와 다른 가장 최근 스냅샷 반환. 없으면 None."""
    for entry in reversed(history):
        if entry.get("date") != today:
            return entry
    return None


def save_snapshot(data: dict, score: int) -> None:
    """현재 데이터를 history.json에 저장 (같은 날짜 재실행시 덮어쓰기)."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_history()

    snapshot = {**data, "crisis_score": score}

    # 같은 날짜 항목이 있으면 교체
    today = data.get("date", "")
    history = [e for e in history if e.get("date") != today]
    history.append(snapshot)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
