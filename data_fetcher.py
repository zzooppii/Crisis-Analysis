# data_fetcher.py — yfinance를 이용한 시장 데이터 수집

import os
import time
from datetime import date

import yfinance as yf

from config import TICKERS, MA_WINDOW, PERFORMANCE_DAYS


def _get_info(symbol: str) -> dict:
    """yfinance .info 딕셔너리 반환. 실패시 빈 dict."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        print(f"  [경고] {symbol} info 수집 실패: {e}")
        return {}


def _get_current_price(info: dict) -> float | None:
    """현재가: regularMarketPrice → currentPrice → previousClose 순으로 시도."""
    for key in ("regularMarketPrice", "currentPrice", "previousClose"):
        val = info.get(key)
        if val is not None and val > 0:
            return float(val)
    return None


def _get_ma20_and_gap(symbol: str) -> tuple[float | None, float | None]:
    """20일 이동평균 및 현재가 대비 괴리율 반환. (ma20, pct_vs_ma)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2mo")
        if hist.empty or len(hist) < MA_WINDOW:
            return None, None
        ma20 = float(hist["Close"].rolling(MA_WINDOW).mean().iloc[-1])
        current = float(hist["Close"].iloc[-1])
        pct = (current / ma20 - 1) * 100
        return ma20, pct
    except Exception as e:
        print(f"  [경고] {symbol} MA20 계산 실패: {e}")
        return None, None


def _get_5day_return(symbol: str) -> float | None:
    """최근 5 거래일 수익률(%) 반환."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty or len(hist) < PERFORMANCE_DAYS + 1:
            return None
        close = hist["Close"]
        ret = (float(close.iloc[-1]) / float(close.iloc[-(PERFORMANCE_DAYS + 1)]) - 1) * 100
        return ret
    except Exception as e:
        print(f"  [경고] {symbol} 5일 수익률 계산 실패: {e}")
        return None


def _get_short_interest(info: dict, symbol: str) -> float | None:
    """공매도 비율(%) 반환. yfinance → 환경변수 → 수동입력 순으로 시도."""
    val = info.get("shortPercentOfFloat")
    if val is not None:
        return float(val) * 100

    # 환경변수 (예: OWL_SHORT_PCT=20.82)
    env_key = f"{symbol.upper()}_SHORT_PCT"
    env_val = os.environ.get(env_key)
    if env_val:
        try:
            return float(env_val)
        except ValueError:
            pass

    # 수동 입력
    try:
        raw = input(f"  {symbol} 공매도 비율을 입력하세요 (예: 15.5, 모르면 Enter): ").strip()
        if raw:
            return float(raw)
    except (EOFError, ValueError):
        pass

    return None


def fetch_all_data() -> dict:
    """모든 시장 데이터를 수집하여 단일 dict로 반환."""
    data: dict = {"date": date.today().isoformat()}

    # ── VIX ──────────────────────────────────────────────
    print("  VIX 수집 중...")
    info = _get_info(TICKERS["VIX"])
    data["vix"] = _get_current_price(info)
    time.sleep(0.5)

    # ── OWL (Blue Owl Capital) ────────────────────────────
    print("  OWL 수집 중...")
    info = _get_info(TICKERS["OWL"])
    data["owl_price"] = _get_current_price(info)
    data["owl_52w_high"] = info.get("fiftyTwoWeekHigh")
    data["owl_52w_low"] = info.get("fiftyTwoWeekLow")
    data["owl_short_pct"] = _get_short_interest(info, "OWL")
    data["owl_ma20"], data["owl_ma20_gap_pct"] = _get_ma20_and_gap(TICKERS["OWL"])
    if data["owl_price"] and data["owl_52w_high"]:
        data["owl_drop_from_high_pct"] = (1 - data["owl_price"] / data["owl_52w_high"]) * 100
    else:
        data["owl_drop_from_high_pct"] = None
    time.sleep(0.5)

    # ── BX (Blackstone) ───────────────────────────────────
    print("  BX 수집 중...")
    info = _get_info(TICKERS["BX"])
    data["bx_price"] = _get_current_price(info)
    data["bx_52w_high"] = info.get("fiftyTwoWeekHigh")
    data["bx_52w_low"] = info.get("fiftyTwoWeekLow")
    data["bx_ma20"], data["bx_ma20_gap_pct"] = _get_ma20_and_gap(TICKERS["BX"])
    if data["bx_price"] and data["bx_52w_high"]:
        data["bx_drop_from_high_pct"] = (1 - data["bx_price"] / data["bx_52w_high"]) * 100
    else:
        data["bx_drop_from_high_pct"] = None
    time.sleep(0.5)

    # ── IGV (Software ETF) ────────────────────────────────
    print("  IGV 수집 중...")
    info = _get_info(TICKERS["IGV"])
    data["igv_price"] = _get_current_price(info)
    data["igv_52w_high"] = info.get("fiftyTwoWeekHigh")
    data["igv_52w_low"] = info.get("fiftyTwoWeekLow")
    time.sleep(0.5)

    # ── HYG (High Yield ETF) ──────────────────────────────
    print("  HYG 수집 중...")
    info = _get_info(TICKERS["HYG"])
    data["hyg_price"] = _get_current_price(info)
    time.sleep(0.5)

    # ── ARCC ─────────────────────────────────────────────
    print("  ARCC 수집 중...")
    data["arcc_5day_ret"] = _get_5day_return(TICKERS["ARCC"])
    time.sleep(0.5)

    # ── FSK ──────────────────────────────────────────────
    print("  FSK 수집 중...")
    data["fsk_5day_ret"] = _get_5day_return(TICKERS["FSK"])

    return data
