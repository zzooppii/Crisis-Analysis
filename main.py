#!/usr/bin/env python3
# main.py — 사모펀드 주간 위기 분석 리포트 생성기

from data_fetcher import fetch_all_data
from crisis_scorer import calculate_scores
from history import load_history, get_previous_week, save_snapshot
from report_generator import generate_report


def main():
    print("=" * 60)
    print("  사모펀드(Private Credit) 주간 위기 분석 리포트")
    print("=" * 60)
    print()

    # 1. 데이터 수집
    print("[1/4] 시장 데이터 수집 중...")
    data = fetch_all_data()
    print()

    # 2. 위기 점수 계산
    print("[2/4] 위기 점수 계산 중...")
    scores = calculate_scores(data)
    print(f"  → 위기 점수: {scores['total']}/{scores['max']} ({scores['level_emoji']} {scores['level']})")
    print()

    # 3. 이전 주 데이터 로드
    print("[3/4] 이전 데이터 로드 중...")
    history = load_history()
    prev_data = get_previous_week(history, data["date"])
    if prev_data:
        print(f"  → 이전 데이터: {prev_data['date']}")
    else:
        print("  → 이전 데이터 없음 (첫 실행)")
    print()

    # 4. 리포트 생성
    print("[4/4] 리포트 생성 중...")
    report, filepath = generate_report(data, scores, prev_data)
    print()

    # 리포트 출력
    print("=" * 60)
    print(report)
    print("=" * 60)

    # 스냅샷 저장
    save_snapshot(data, scores["total"])
    print(f"\n✅ 리포트 저장 완료: {filepath}")
    print(f"✅ 스냅샷 저장 완료: data/history.json")


if __name__ == "__main__":
    main()
