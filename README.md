# 사모펀드(Private Credit) 주간 위기 분석 도구

매주 `python main.py` 한 번으로 사모펀드 시장의 위기 신호를 자동 수집하고 한국어 리포트를 생성합니다.

## 권장 워크플로우: Python + Claude 연동

`main.py`는 **수치 수집과 점수 계산**을 담당하고, Claude는 **해석과 판단**을 담당합니다.

### Step 1 — 데이터 수집 (Python)

```bash
python main.py
```

`reports/report_YYYY-MM-DD.md` 파일이 생성됩니다.

### Step 2 — Claude에게 분석 요청

생성된 리포트를 Claude에 붙여넣고 아래 프롬프트를 사용합니다:

```
아래는 이번 주 사모펀드 위기 분석 리포트야.
수치 데이터는 yfinance로 자동 수집한 실제 값이야.

[report_YYYY-MM-DD.md 내용 붙여넣기]

다음을 분석해줘:
1. 이 점수가 나온 배경 — 현재 거시경제 상황(관세, 금리, 신용시장)과 연결해서 설명
2. 가장 주목해야 할 지표 1~2개와 그 이유
3. 지난주 대비 변화의 의미 (악화/개선/일시적인지)
4. 향후 1~2주 내 주시해야 할 이벤트나 지표
```

### 역할 분담 요약

| 역할 | 도구 | 이유 |
|------|------|------|
| 데이터 수집 | `main.py` | 정확한 실시간 수치, 무료, 매주 일관된 기준 |
| 수치 계산/점수화 | `main.py` | 임계값이 코드에 고정되어 오차 없음 |
| 거시경제 맥락 해석 | Claude | 뉴스·정책·시장 심리 종합 판단 |
| 이상 신호 설명 | Claude | "왜 이런 수치가 나왔는가" 서술 |
| 향후 전망 | Claude | 불확실성과 시나리오 기반 추론 |

---

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

실행하면:
1. yfinance로 시장 데이터 자동 수집 (VIX, OWL, BX, IGV, HYG, ARCC, FSK)
2. 6개 규칙 기반 위기 점수 계산 (0~10점)
3. 한국어 마크다운 리포트 출력 + 파일 저장
4. 주간 스냅샷 저장 (다음 주 실행 시 비교 표시)

## 위기 점수 규칙

| 규칙 | 조건 | 점수 |
|------|------|------|
| VIX 급등 | > 30 | +2 |
| HYG 하락 | < $75 | +2 |
| PE매니저 급락 | OWL 또는 BX가 52주 고점 대비 -30% 이상 | +2 |
| PE매니저 MA 이탈 | OWL 또는 BX가 20일 이동평균 대비 -30% 이상 | +2 |
| OWL 공매도 급증 | > 15% | +1 |
| BDC 하락 | ARCC 또는 FSK 5일 수익률 < -2% | +1 |

**위기 레벨:** 0-2 낮음 🟢 / 3-4 관심 🟡 / 5-6 주의 🟠 / 7-8 경고 🔴 / 9-10 위기 🚨

## 출력 파일

| 경로 | 설명 |
|------|------|
| `reports/report_YYYY-MM-DD.md` | 날짜별 마크다운 리포트 |
| `data/history.json` | 누적 주간 스냅샷 (지난주 대비 비교에 사용) |

## OWL 공매도 비율 데이터

yfinance가 제공하는 `shortPercentOfFloat` 값을 사용합니다 (SEC 공시 기준, 약 2주 지연).
자동 수집에 실패할 경우 다음 방법으로 수동 지정 가능합니다:

```bash
# 환경변수로 지정
OWL_SHORT_PCT=20.82 python main.py

# 또는 실행 중 프롬프트에서 직접 입력
```

## 파일 구조

```
Crisis-Analysis/
├── main.py              # 진입점
├── config.py            # 임계값 및 설정
├── data_fetcher.py      # yfinance 데이터 수집
├── crisis_scorer.py     # 위기 점수 계산
├── history.py           # 주간 스냅샷 저장/조회
├── report_generator.py  # 한국어 리포트 생성
├── requirements.txt
├── data/
│   └── history.json     # 누적 데이터
└── reports/
    └── report_*.md      # 생성된 리포트
```
