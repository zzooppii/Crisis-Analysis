# config.py — 상수, 임계값, 티커 심볼

TICKERS = {
    "VIX": "^VIX",
    "OWL": "OWL",
    "BX": "BX",
    "IGV": "IGV",
    "HYG": "HYG",
    "ARCC": "ARCC",
    "FSK": "FSK",
}

THRESHOLDS = {
    "vix_crisis": 30.0,
    "hyg_crisis": 75.0,
    "pe_drop_pct": 30.0,       # 52주 고점 대비 하락률 (%)
    "pe_ma20_drop_pct": 30.0,  # 20일 이동평균 대비 하락률 (%)
    "owl_short_pct": 15.0,     # OWL 공매도 비율 (%)
    "bdc_5day_decline_pct": 2.0,  # BDC 5일 하락률 (%)
}

SCORE_WEIGHTS = {
    "vix": 2,
    "hyg": 2,
    "pe_drop": 2,
    "pe_ma20": 2,
    "owl_short": 1,
    "bdc_5day": 1,
}

SCORE_LEVELS = [
    (0, 2, "낮음 (Low)", "🟢"),
    (3, 4, "관심 (Watch)", "🟡"),
    (5, 6, "주의 (Caution)", "🟠"),
    (7, 8, "경고 (Warning)", "🔴"),
    (9, 10, "위기 (Crisis)", "🚨"),
]

MA_WINDOW = 20
PERFORMANCE_DAYS = 5

HISTORY_FILE = "data/history.json"
REPORTS_DIR = "reports"
