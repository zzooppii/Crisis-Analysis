# crisis_scorer.py — 위기 점수 계산

from config import THRESHOLDS, SCORE_WEIGHTS, SCORE_LEVELS


def _score_to_level(score: int) -> tuple[str, str]:
    """점수 → (레벨명, 이모지) 반환."""
    for lo, hi, label, emoji in SCORE_LEVELS:
        if lo <= score <= hi:
            return label, emoji
    return "위기 (Crisis)", "🚨"


def calculate_scores(data: dict) -> dict:
    """6개 위기 규칙을 평가하여 점수와 상세 내역을 반환."""
    details = []
    total = 0

    # ── 규칙 1: VIX > 30 ─────────────────────────────────
    vix = data.get("vix")
    if vix is not None:
        triggered = vix > THRESHOLDS["vix_crisis"]
        pts = SCORE_WEIGHTS["vix"] if triggered else 0
        total += pts
        details.append({
            "rule": f"VIX > {THRESHOLDS['vix_crisis']}",
            "triggered": triggered,
            "points": pts,
            "max_points": SCORE_WEIGHTS["vix"],
            "actual": f"{vix:.2f}",
        })
    else:
        details.append({"rule": "VIX > 30", "triggered": False, "points": 0,
                         "max_points": SCORE_WEIGHTS["vix"], "actual": "N/A"})

    # ── 규칙 2: HYG < $75 ────────────────────────────────
    hyg = data.get("hyg_price")
    if hyg is not None:
        triggered = hyg < THRESHOLDS["hyg_crisis"]
        pts = SCORE_WEIGHTS["hyg"] if triggered else 0
        total += pts
        details.append({
            "rule": f"HYG < ${THRESHOLDS['hyg_crisis']}",
            "triggered": triggered,
            "points": pts,
            "max_points": SCORE_WEIGHTS["hyg"],
            "actual": f"${hyg:.2f}",
        })
    else:
        details.append({"rule": "HYG < $75", "triggered": False, "points": 0,
                         "max_points": SCORE_WEIGHTS["hyg"], "actual": "N/A"})

    # ── 규칙 3: PE매니저 52주 고점 대비 -30% 이상 ───────
    owl_drop = data.get("owl_drop_from_high_pct")
    bx_drop = data.get("bx_drop_from_high_pct")
    threshold_drop = THRESHOLDS["pe_drop_pct"]
    triggered_list = []
    if owl_drop is not None and owl_drop >= threshold_drop:
        triggered_list.append(f"OWL -{owl_drop:.1f}%")
    if bx_drop is not None and bx_drop >= threshold_drop:
        triggered_list.append(f"BX -{bx_drop:.1f}%")
    triggered = len(triggered_list) > 0
    pts = SCORE_WEIGHTS["pe_drop"] if triggered else 0
    total += pts
    owl_str = f"OWL -{owl_drop:.1f}%" if owl_drop is not None else "OWL N/A"
    bx_str = f"BX -{bx_drop:.1f}%" if bx_drop is not None else "BX N/A"
    details.append({
        "rule": f"PE매니저 52주 고점 대비 -{threshold_drop}% 이상",
        "triggered": triggered,
        "points": pts,
        "max_points": SCORE_WEIGHTS["pe_drop"],
        "actual": f"{owl_str}, {bx_str}",
    })

    # ── 규칙 4: PE매니저 20일MA 대비 -30% 이상 ───────────
    owl_ma_gap = data.get("owl_ma20_gap_pct")
    bx_ma_gap = data.get("bx_ma20_gap_pct")
    threshold_ma = THRESHOLDS["pe_ma20_drop_pct"]
    triggered_list = []
    if owl_ma_gap is not None and owl_ma_gap <= -threshold_ma:
        triggered_list.append(f"OWL {owl_ma_gap:.1f}%")
    if bx_ma_gap is not None and bx_ma_gap <= -threshold_ma:
        triggered_list.append(f"BX {bx_ma_gap:.1f}%")
    triggered = len(triggered_list) > 0
    pts = SCORE_WEIGHTS["pe_ma20"] if triggered else 0
    total += pts
    owl_ma_str = f"OWL {owl_ma_gap:.1f}%" if owl_ma_gap is not None else "OWL N/A"
    bx_ma_str = f"BX {bx_ma_gap:.1f}%" if bx_ma_gap is not None else "BX N/A"
    details.append({
        "rule": f"PE매니저 20일MA 대비 -{threshold_ma}% 이상",
        "triggered": triggered,
        "points": pts,
        "max_points": SCORE_WEIGHTS["pe_ma20"],
        "actual": f"{owl_ma_str}, {bx_ma_str}",
    })

    # ── 규칙 5: OWL 공매도 비율 > 15% ────────────────────
    owl_short = data.get("owl_short_pct")
    if owl_short is not None:
        triggered = owl_short > THRESHOLDS["owl_short_pct"]
        pts = SCORE_WEIGHTS["owl_short"] if triggered else 0
        total += pts
        details.append({
            "rule": f"OWL 공매도 비율 > {THRESHOLDS['owl_short_pct']}%",
            "triggered": triggered,
            "points": pts,
            "max_points": SCORE_WEIGHTS["owl_short"],
            "actual": f"{owl_short:.2f}%",
        })
    else:
        details.append({
            "rule": f"OWL 공매도 비율 > {THRESHOLDS['owl_short_pct']}%",
            "triggered": False, "points": 0,
            "max_points": SCORE_WEIGHTS["owl_short"], "actual": "N/A (데이터 없음)",
        })

    # ── 규칙 6: BDC 5일 하락 > -2% ───────────────────────
    arcc_ret = data.get("arcc_5day_ret")
    fsk_ret = data.get("fsk_5day_ret")
    threshold_bdc = -THRESHOLDS["bdc_5day_decline_pct"]
    triggered_list = []
    if arcc_ret is not None and arcc_ret < threshold_bdc:
        triggered_list.append(f"ARCC {arcc_ret:.2f}%")
    if fsk_ret is not None and fsk_ret < threshold_bdc:
        triggered_list.append(f"FSK {fsk_ret:.2f}%")
    triggered = len(triggered_list) > 0
    pts = SCORE_WEIGHTS["bdc_5day"] if triggered else 0
    total += pts
    arcc_str = f"ARCC {arcc_ret:.2f}%" if arcc_ret is not None else "ARCC N/A"
    fsk_str = f"FSK {fsk_ret:.2f}%" if fsk_ret is not None else "FSK N/A"
    details.append({
        "rule": f"BDC 5일 수익률 < -{THRESHOLDS['bdc_5day_decline_pct']}%",
        "triggered": triggered,
        "points": pts,
        "max_points": SCORE_WEIGHTS["bdc_5day"],
        "actual": f"{arcc_str}, {fsk_str}",
    })

    level, emoji = _score_to_level(total)
    return {
        "total": total,
        "max": sum(SCORE_WEIGHTS.values()),
        "level": level,
        "level_emoji": emoji,
        "details": details,
    }
