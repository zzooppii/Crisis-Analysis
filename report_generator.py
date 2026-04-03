# report_generator.py — 한국어 마크다운 리포트 생성

import os
from datetime import datetime

from config import REPORTS_DIR

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _fmt(val, fmt=".2f", prefix="", suffix="", na="N/A") -> str:
    """None이면 na 문자열, 그 외에는 format 적용."""
    if val is None:
        return na
    return f"{prefix}{val:{fmt}}{suffix}"


def _status_emoji(triggered: bool) -> str:
    return "🔴 위험" if triggered else "🟢 정상"


def _diff_arrow(current, previous) -> str:
    """변화량 표시 (▲▼ 화살표)."""
    if current is None or previous is None:
        return "N/A"
    diff = current - previous
    arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
    return f"{arrow} {abs(diff):.2f}"


def _score_diff_str(current: int, previous: int | None) -> str:
    if previous is None:
        return str(current)
    diff = current - previous
    arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
    sign = "+" if diff > 0 else ""
    return f"{previous} → {current} ({sign}{diff}) {arrow}"


def _summary_sentence(score: int, level: str, emoji: str) -> str:
    sentences = {
        (0, 2): "현재 사모펀드 시장은 전반적으로 안정적입니다. 특이 신호 없음.",
        (3, 4): "관심 단계입니다. 일부 지표에서 약한 스트레스 신호가 감지됩니다.",
        (5, 6): "주의 단계입니다. 복수의 위기 지표가 임계값을 넘었습니다. 포트폴리오 점검을 권장합니다.",
        (7, 8): "경고 단계입니다. 사모펀드 및 PE 시장에 상당한 스트레스가 감지됩니다. 신중한 대응이 필요합니다.",
        (9, 10): "위기 단계입니다. 거의 모든 위기 지표가 활성화되었습니다. 즉각적인 리스크 관리가 필요합니다.",
    }
    for (lo, hi), sentence in sentences.items():
        if lo <= score <= hi:
            return f"{emoji} {sentence}"
    return f"{emoji} {level}"


def generate_report(data: dict, scores: dict, prev_data: dict | None) -> str:
    """마크다운 리포트 문자열 생성 + 터미널 출력 + 파일 저장."""
    today_str = data.get("date", datetime.today().strftime("%Y-%m-%d"))
    dt = datetime.strptime(today_str, "%Y-%m-%d")
    weekday = WEEKDAY_KO[dt.weekday()]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []

    # ── 제목 ─────────────────────────────────────────────
    lines.append(f"# 주간 사모펀드(Private Credit) 위기 분석 리포트")
    lines.append(f"**날짜:** {today_str} ({weekday}요일)  |  **생성:** {generated_at}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 1. 위기 체크리스트 ────────────────────────────────
    lines.append("## 1. 주간 사모펀드 위기 체크리스트")
    lines.append("")
    lines.append("| 항목 | 티커 | 현재 수치 | 기준 | 상태 |")
    lines.append("|------|------|-----------|------|------|")

    vix = data.get("vix")
    lines.append(
        f"| VIX (변동성 지수) | ^VIX | {_fmt(vix)} | > 30 | {_status_emoji(vix is not None and vix > 30)} |"
    )

    owl_price = data.get("owl_price")
    owl_52h = data.get("owl_52w_high")
    owl_drop = data.get("owl_drop_from_high_pct")
    owl_cell = f"${_fmt(owl_price)} (고점 대비 -{_fmt(owl_drop, '.1f')}%)" if owl_price else "N/A"
    lines.append(
        f"| Blue Owl Capital | OWL | {owl_cell} | 고점 대비 -30% 이하 | "
        f"{_status_emoji(owl_drop is not None and owl_drop >= 30)} |"
    )

    bx_price = data.get("bx_price")
    bx_drop = data.get("bx_drop_from_high_pct")
    bx_cell = f"${_fmt(bx_price)} (고점 대비 -{_fmt(bx_drop, '.1f')}%)" if bx_price else "N/A"
    lines.append(
        f"| Blackstone | BX | {bx_cell} | 고점 대비 -30% 이하 | "
        f"{_status_emoji(bx_drop is not None and bx_drop >= 30)} |"
    )

    igv_price = data.get("igv_price")
    igv_52h = data.get("igv_52w_high")
    igv_drop = None
    if igv_price and igv_52h:
        igv_drop = (1 - igv_price / igv_52h) * 100
    igv_cell = f"${_fmt(igv_price)} (고점 대비 -{_fmt(igv_drop, '.1f')}%)" if igv_price else "N/A"
    lines.append(
        f"| Software ETF | IGV | {igv_cell} | 참고 지표 | ─ |"
    )

    hyg_price = data.get("hyg_price")
    lines.append(
        f"| High Yield ETF | HYG | ${_fmt(hyg_price)} | < $75 | "
        f"{_status_emoji(hyg_price is not None and hyg_price < 75)} |"
    )

    owl_short = data.get("owl_short_pct")
    lines.append(
        f"| OWL 공매도 비율 | OWL | {_fmt(owl_short, '.2f')}% | > 15% | "
        f"{_status_emoji(owl_short is not None and owl_short > 15)} |"
    )

    arcc_ret = data.get("arcc_5day_ret")
    fsk_ret = data.get("fsk_5day_ret")
    bdc_cell = f"ARCC {_fmt(arcc_ret, '.2f')}%, FSK {_fmt(fsk_ret, '.2f')}%"
    bdc_triggered = (arcc_ret is not None and arcc_ret < -2) or (fsk_ret is not None and fsk_ret < -2)
    lines.append(
        f"| BDC 5일 수익률 | ARCC/FSK | {bdc_cell} | 어느 하나 -2% 이하 | "
        f"{_status_emoji(bdc_triggered)} |"
    )

    lines.append("")

    # ── 2. 위기 온도 ─────────────────────────────────────
    lines.append("## 2. 위기 온도 (Crisis Score)")
    lines.append("")
    lines.append("| 항목 | 판정 기준 | 현재 값 | 점수 |")
    lines.append("|------|----------|---------|------|")

    for d in scores["details"]:
        status = "✅ 해당" if d["triggered"] else "─ 미해당"
        pts_str = f"**+{d['points']}**" if d["triggered"] else f"0/{d['max_points']}"
        lines.append(f"| {d['rule']} | | {d['actual']} | {pts_str} |")

    total = scores["total"]
    max_score = scores["max"]
    level = scores["level"]
    emoji = scores["level_emoji"]
    lines.append(f"| **총점** | | | **{total}/{max_score}** |")
    lines.append(f"| **위기 레벨** | | | **{emoji} {level}** |")
    lines.append("")

    # ── 3. 한 줄 요약 ─────────────────────────────────────
    lines.append("## 3. 한 줄 요약")
    lines.append("")
    lines.append(_summary_sentence(total, level, emoji))
    lines.append("")

    # ── 4. 지난주 대비 변화 ───────────────────────────────
    lines.append("## 4. 지난주 대비 변화")
    lines.append("")
    if prev_data is None:
        lines.append("> 이전 데이터 없음 (첫 실행 또는 history.json 없음)")
    else:
        prev_date = prev_data.get("date", "이전")
        lines.append(f"*(비교 기준: {prev_date})*")
        lines.append("")
        lines.append("| 항목 | 지난주 | 이번주 | 변화 |")
        lines.append("|------|--------|--------|------|")

        def row(label, key, fmt=".2f", prefix="", suffix=""):
            curr = data.get(key)
            prev = prev_data.get(key)
            curr_str = f"{prefix}{_fmt(curr, fmt)}{suffix}" if curr is not None else "N/A"
            prev_str = f"{prefix}{_fmt(prev, fmt)}{suffix}" if prev is not None else "N/A"
            diff_str = _diff_arrow(curr, prev)
            return f"| {label} | {prev_str} | {curr_str} | {diff_str} |"

        lines.append(row("VIX", "vix"))
        lines.append(row("OWL 주가", "owl_price", prefix="$"))
        lines.append(row("BX 주가", "bx_price", prefix="$"))
        lines.append(row("HYG", "hyg_price", prefix="$"))

        prev_score = prev_data.get("crisis_score")
        lines.append(
            f"| 위기 점수 | {prev_score if prev_score is not None else 'N/A'} "
            f"| {total} | {_score_diff_str(total, prev_score)} |"
        )

    lines.append("")

    # ── 5. 주요 뉴스 ─────────────────────────────────────
    lines.append("## 5. 주요 뉴스 / 참고 사항")
    lines.append("")
    lines.append("> ※ 이 섹션은 수동으로 작성해주세요.")
    lines.append("> ")
    lines.append("> - 뉴스 항목 1")
    lines.append("> - 뉴스 항목 2")
    lines.append("")

    # ── 6. 데이터 출처 ────────────────────────────────────
    lines.append("## 6. 데이터 출처")
    lines.append("")
    lines.append("| 항목 | 출처 |")
    lines.append("|------|------|")
    lines.append("| VIX, OWL, BX, IGV, HYG, ARCC, FSK | Yahoo Finance (yfinance 라이브러리) |")
    lines.append("| OWL 공매도 비율 | Yahoo Finance / SEC Filing (2주 지연) |")
    lines.append(f"| 생성 시각 | {generated_at} |")
    lines.append("")

    report = "\n".join(lines)

    # ── 파일 저장 ─────────────────────────────────────────
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, f"report_{today_str}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    return report, filepath
