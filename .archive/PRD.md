# DS News Aggregator - Lean MVP PRD v2.0

## 1. Executive Summary

데이터 사이언티스트 개인용 AI/ML 뉴스 중심 자동 큐레이션 웹사이트를 구축한다. 매일 자동으로 해외/국내 기술 뉴스(50%) + 실용 블로그·꿀팁(30%) + 회사 기술블로그(20%)를 수집하여 한국어 번역과 3문장 요약을 제공한다. GitHub Actions로 컴퓨터 독립적 자동 실행, Railway 배포로 모바일 출퇴근 중에도 접속 가능. 가설: 매일 30분 정보 수집 시간을 5분으로 단축하면서 뉴스 시의성과 실용 정보 품질은 향상. 1주차 데모는 10개 소스에서 일 5-10개 엄선된 글 제공. 성공 지표는 "도움되는 글" 비율 70% 이상.

## 2. Problem & Context

| 페인포인트 | 현재 대안 | 차별점 |
|------------|-----------|--------|
| 해외 뉴스는 영어, 국내는 산발적 | 개별 사이트 순회 | 뉴스 중심 통합 + 자동 번역 |
| 뉴스 vs 블로그 글 균형 부족 | RSS 리더 수동 관리 | 뉴스 50% 보장 + 꿀팁 30% |
| 컴퓨터 켜야만 수집 가능 | 로컬 크론잡 | GitHub Actions 클라우드 자동화 |

## 3. Objectives & Metrics

**North Star Metric (OEC)**
- 정의: 일일 유용한 글 발견률 (요약을 읽고 도움된 글 수 / 전체 수집 글 수)
- 측정식: `daily_useful_articles / daily_collected_articles`

**Primary Metrics (≤2)**
- 개인 사용 만족도: 주관적 평가 (1주일 후 체크)
- 일일 실사용 여부: 접속했는지만 간단 확인

**Guardrail Metrics (≤2)**
- 수집 안정성: GitHub Actions 실행 성공률 (목표: >90%)
- 뉴스 비율: 전체 글 중 뉴스 미디어 비율 (목표: 40-60%)

**목표치**: 기준선(0) → 1주(만족도 평가) → 4주(유용 글 비율 70%)

## 4. MVP Scope (제약 적합성 명시)

### In-Scope (핵심 기능)
1. **뉴스 중심 수집기** (M, 2h): 해외 뉴스 3개 + 국내 뉴스 3개 + 블로그 4개
2. **GitHub Actions 자동화** (S, 0.5h): 매일 자동 실행, 컴퓨터 독립적
3. **번역/요약 파이프라인** (M, 2h): Google Translate + Gemini API
4. **웹 앱 + Railway 배포** (S, 0.5h): 모바일 친화 카드 UI

**총 시간: 5시간** ✅

### Out-of-Scope (다음 루프)
- 북마크 기능, PWA 변환, 알림 시스템, 고급 개인화

### 제약 체크
- **월 비용**: 모든 API/서비스 무료 플랜
- **총 월비용: ₩0** ✅
- **시간**: 5시간 (여유 0%)

## 5. User Flow & UX Notes

**핵심 플로우** (모바일 + 데스크톱)
1. GitHub Actions가 매일 오전 8시(KST) 자동으로 수집+번역+요약 실행
2. 출퇴근 중 모바일 또는 회사에서 https://your-app.railway.app 접속
3. 카드 형태로 **요약만** 표시: [뉴스/블로그] 제목(한글) + 3줄 요약 + 태그
4. 관심 카드 클릭 → **모달창**에서 번역된 전문 표시
5. "원문 보기" 클릭시 새 탭에서 원문 사이트로 이동
6. 읽은 글은 체크 표시 (localStorage)

**상태 처리**
- 로딩: "최신 뉴스 불러오는 중..."
- 번역 실패: 원문 그대로 + "번역 실패" 배지
- 요약 실패: 첫 100자 표시 + "요약 실패" 배지
- 빈 상태: "오늘 수집된 글이 없습니다"
- GitHub Actions 실패: "자동 수집 실패, 관리자 확인 필요"

## 6. Requirements

### 6.1 Functional Requirements

**FR-1: 뉴스 중심 다채널 수집**
- 사용자 스토리: 해외/국내 기술 뉴스가 우선적으로, 그 다음 실용 블로그가 수집되어야 한다
- Given: 10개 소스가 설정되어 있을 때
- When: GitHub Actions가 매일 실행되면
- Then: TechCrunch AI, VentureBeat AI, MIT Tech Review에서 뉴스를 수집한다
- And Then: AI타임스, ZDNet Korea, Tech42에서 국내 뉴스를 수집한다
- And Then: Towards Data Science, Analytics Vidhya, KDnuggets, Neptune.ai에서 블로그를 수집한다

**FR-2: 뉴스 우선 필터링**
- 사용자 스토리: 뉴스가 50% 비율을 유지하고 고품질 글만 선별되어야 한다
- Given: 수집된 글들이 있을 때
- When: 필터링 로직을 실행하면
- Then: 뉴스 미디어 글에 기본 100점, 블로그 글에 80점을 부여한다
- And Then: "발표", "공개", "출시" 포함시 +30점, "방법", "가이드" 포함시 +20점을 추가한다
- And Then: 최종 70점 이상 글만 선별하여 뉴스 50%, 블로그 50% 비율로 5-10개 선택한다

**FR-3: Gemini 번역/요약**
- 사용자 스토리: 영문 글은 한국어로 번역되고 모든 글은 3문장으로 요약되어야 한다
- Given: 필터링된 글들이 있을 때
- When: 번역/요약 파이프라인을 실행하면
- Then: Google Translate로 영문 제목/내용을 한국어로 번역한다
- And Then: Gemini API로 각 글을 정확히 3문장으로 한국어 요약한다

**FR-4: 모바일 친화 웹 UI**
- 사용자 스토리: 모바일과 데스크톱에서 카드를 클릭해 전문을 볼 수 있어야 한다
- Given: Railway에 배포된 웹앱에 접속했을 때
- When: 메인 화면을 로드하면
- Then: [뉴스] 또는 [블로그] 태그와 함께 카드 형태로 요약이 표시된다
- And Then: 카드 클릭시 모달창에서 번역된 전문과 "원문 보기" 버튼이 표시된다

**FR-5: GitHub Actions 자동화**
- 사용자 스토리: 컴퓨터가 꺼져있어도 매일 자동으로 수집이 실행되어야 한다
- Given: GitHub Actions workflow가 설정되어 있을 때
- When: 매일 오전 8시(KST)가 되면
- Then: 클라우드 환경에서 자동으로 수집 파이프라인이 실행된다
- And Then: 결과를 Git에 커밋하고 Railway가 자동으로 재배포한다

### 6.2 Non-Functional Requirements

**NFR-1: 품질 기준**
- 뉴스 비율: 전체 글 중 40-60% 유지
- 정보성 글 비율: 80% 이상 (주관적 평가)
- 번역/요약 품질: 샘플 10개 중 8개 이상 만족

**NFR-2: 성능**
- GitHub Actions 실행: 15분 이내 완료
- 웹페이지 로딩: 모바일에서 3초 이내
- API 호출: Gemini 일 15회 이내 (무료 한도 여유)

**NFR-3: 안정성**
- GitHub Actions 성공률: 90% 이상
- API 실패시 graceful degradation (번역/요약 없이라도 원문 제공)
- Railway 배포 자동화

**NFR-4: 접근성**
- 모바일 반응형 디자인 필수
- 다크/라이트 모드 지원
- 터치 인터랙션 최적화

## 7. Data & Analytics Plan (미니)

### 이벤트 테이블 (최소화)
| Event | Trigger | Props | 보존기간 | 목적 |
|-------|---------|-------|----------|------|
| github_action_run | Actions 실행 완료 | success, collected_count, news_ratio | 60일 | 수집 안정성 |
| translation_batch | 번역 완료 | processed_count, fail_rate | 30일 | 번역 품질 |
| summary_batch | 요약 완료 | gemini_calls, avg_length | 30일 | API 사용량 |

### 기초 차트 (간소화)
1. **수집 안정성**: GitHub Actions 성공률 추이
2. **콘텐츠 균형**: 뉴스 vs 블로그 비율
3. **개인 만족도**: 주간 주관적 평가 메모

## 8. AI/LLM Design

### 번역 파이프라인
- **유스케이스**: 영문 제목/내용을 자연스러운 한국어로 번역
- **모델**: Google Translate API (무료 50만자/월)
- **가드레일**: 이미 한국어면 스킵, 1500자 이상은 첫 1000자만
- **오프라인 평가**: 번역 품질 샘플 10개

### 요약 파이프라인
- **유스케이스**: 뉴스/블로그 글을 3문장으로 핵심 요약
- **모델**: Google Gemini Pro API (무료 월 60회/분, 100만토큰/일)
- **프롬프트**: "다음 기술 기사/블로그를 정확히 3문장으로 요약해주세요. 핵심 내용과 결론을 포함하되 한국어로 답변하세요: [내용]"
- **가드레일**: 1500자 이하 입력만 처리, 한국어 출력 강제
- **오프라인 평가**: 요약 품질 샘플 10개

### 온라인 필터 및 킬스위치
- **번역 필터**: 번역 결과 비정상시 원문 사용
- **요약 필터**: 요약이 20자 미만 또는 300자 초과면 첫 100자 사용
- **킬스위치**: Gemini 오류율 70% 초과시 요약 기능 중단, 원문만 표시

## 9. Content Filtering Strategy

### 수집 소스 구성 (Tier 시스템)

**Tier 1: 뉴스 미디어 (50%, 목표 3-5개/일)**
```python
news_sources = {
    # 해외 AI 전문 뉴스
    "techcrunch_ai": {
        "url": "techcrunch.com/category/artificial-intelligence/feed",
        "score_bonus": 100,
        "tags": ["뉴스", "해외"]
    },
    "venturebeat_ai": {
        "url": "venturebeat.com/category/ai/feed",
        "score_bonus": 100,
        "tags": ["뉴스", "해외"]
    },
    "mit_tech_review": {
        "url": "technologyreview.com/topic/artificial-intelligence/feed",
        "score_bonus": 110,  # 높은 품질
        "tags": ["뉴스", "해외", "심층"]
    },
    
    # 국내 기술 뉴스
    "ai_times": {
        "url": "aitimes.com/rss.xml",
        "score_bonus": 100,
        "tags": ["뉴스", "국내"]
    },
    "zdnet_korea": {
        "url": "zdnet.co.kr/rss/ai.xml",
        "score_bonus": 90,
        "tags": ["뉴스", "국내"]
    },
    "tech42": {
        "url": "tech42.co.kr/feed",
        "score_bonus": 85,
        "tags": ["뉴스", "국내", "스타트업"]
    }
}
```

**Tier 2: 실용 블로그/꿀팁 (30%, 목표 2-3개/일)**
```python
practical_blogs = {
    "towards_data_science": {
        "url": "towardsdatascience.com/feed",
        "score_bonus": 80,
        "filter": "claps > 100",
        "tags": ["블로그", "튜토리얼"]
    },
    "analytics_vidhya": {
        "url": "analyticsvidhya.com/blog/feed",
        "score_bonus": 75,
        "tags": ["블로그", "실습"]
    },
    "kdnuggets": {
        "url": "kdnuggets.com/feed",
        "score_bonus": 75,
        "tags": ["블로그", "리소스"]
    },
    "neptune_ai": {
        "url": "neptune.ai/blog/feed",
        "score_bonus": 80,
        "tags": ["블로그", "MLOps", "꿀팁"]
    }
}
```

**Tier 3: 회사 기술블로그 (20%, 목표 1-2개/일)**
```python
company_blogs = {
    "google_ai": {
        "url": "ai.googleblog.com/feeds/posts/default",
        "score_bonus": 70,
        "tags": ["기업블로그", "연구"]
    },
    "openai_blog": {
        "url": "openai.com/blog/rss",
        "score_bonus": 90,
        "tags": ["기업블로그", "최신기술"]
    },
    "naver_d2": {
        "url": "d2.naver.com/helloworld.rss",
        "score_bonus": 75,
        "tags": ["기업블로그", "국내"]
    },
    "kakao_tech": {
        "url": "tech.kakao.com/rss.xml",
        "score_bonus": 75,
        "tags": ["기업블로그", "국내"]
    }
}
```

### 점수화 시스템

```python
def calculate_score(article):
    # 기본 점수 (소스 타입별)
    base_score = article.source_bonus  # 100(뉴스), 80(블로그), 70(기업)
    
    # 언어 감지 (영어/한국어 키워드 분리)
    is_korean = article.source in ["ai_times", "zdnet_korea", "tech42", "naver_d2", "kakao_tech"]
    
    # 콘텐츠 타입 보너스
    news_keywords_en = ["announces", "launches", "releases", "unveils", "introduces"]
    news_keywords_kr = ["발표", "공개", "출시", "론칭"]
    keywords = news_keywords_kr if is_korean else news_keywords_en
    if any(word.lower() in article.title.lower() for word in keywords):
        base_score += 30  # 뉴스 속보
    
    guide_keywords_en = ["how to", "guide", "tutorial", "walkthrough", "step-by-step"]
    guide_keywords_kr = ["방법", "가이드", "튜토리얼"]
    keywords = guide_keywords_kr if is_korean else guide_keywords_en
    if any(word.lower() in article.title.lower() for word in keywords):
        base_score += 20  # 실용 가이드
    
    case_keywords_en = ["case study", "experience", "lessons learned", "how we", "implementation"]
    case_keywords_kr = ["사례", "적용", "경험", "후기"]
    keywords = case_keywords_kr if is_korean else case_keywords_en
    if any(word.lower() in article.title.lower() for word in keywords):
        base_score += 15  # 실무 사례
    
    # 관심 키워드 보너스 (LLM, 시계열 등) - 대부분 영어 용어
    llm_keywords = ["llm", "gpt", "transformer", "language model", "claude", "gemini", "대규모언어모델"]
    if any(word.lower() in article.title.lower() or word.lower() in article.content.lower() for word in llm_keywords):
        base_score += 10
    
    timeseries_keywords = ["time series", "forecasting", "prediction", "시계열", "예측"]
    if any(word.lower() in article.title.lower() or word.lower() in article.content.lower() for word in timeseries_keywords):
        base_score += 10
    
    # 신선도 보너스
    hours_old = (now - article.published_time).hours
    if hours_old < 24:
        base_score += 10
    elif hours_old < 168:  # 1주일
        base_score += 5
    
    # 패널티
    opinion_keywords_en = ["opinion", "thoughts on", "my take", "commentary"]
    opinion_keywords_kr = ["의견", "생각", "논평"]
    keywords = opinion_keywords_kr if is_korean else opinion_keywords_en
    if any(word.lower() in article.title.lower() for word in keywords):
        base_score -= 20  # 의견 기사
    
    question_keywords_en = ["what do you think", "recommendations?", "suggestions?", "help me"]
    question_keywords_kr = ["추천해주세요", "어떻게 생각", "도움"]
    keywords = question_keywords_kr if is_korean else question_keywords_en
    if any(word.lower() in article.title.lower() for word in keywords):
        base_score -= 30  # 단순 질문
    
    if len(article.content) < 500:
        base_score -= 15  # 너무 짧은 글
    
    return base_score

# 최종 선별: 70점 이상 글 중에서
# - 뉴스 미디어: 3-5개 (50%)
# - 실용 블로그: 2-3개 (30%)
# - 기업 블로그: 1-2개 (20%)
# 총 5-10개 선택
```

## 10. Architecture & Ops (Solo)

### 아키텍처
```
[GitHub Actions - 매일 08:00 KST]
    ↓
[수집 파이프라인]
    ├─ Tier 1: 뉴스 6개 소스 → 뉴스 3-5개
    ├─ Tier 2: 블로그 4개 소스 → 블로그 2-3개
    └─ Tier 3: 기업 4개 소스 → 기업 1-2개
    ↓
[필터링: 점수화 시스템] → 70점 이상 글만
    ↓
[번역: Google Translate] → 영문 → 한국어
    ↓
[요약: Gemini API] → 각 글 3문장 요약
    ↓
[data/articles.json 저장]
    ↓
[Git Commit & Push]
    ↓
[Railway 자동 재배포]
    ↓
[Flask 웹앱] ← [모바일/데스크톱 사용자]
```

### 의존성
- **Python**: requests, flask, feedparser, google-generativeai, googletrans-py
- **외부 API**: Google Translate(무료), Gemini Pro(무료)
- **자동화**: GitHub Actions (무료 2,000분/월)
- **배포**: Railway (무료 플랜 500시간/월)
- **개발**: macOS + Cursor IDE

### 운영
- **로그**: GitHub Actions 실행 로그, Railway 애플리케이션 로그
- **알람**: GitHub Actions 실패시 이메일 자동 발송
- **롤백**: Git 이력으로 버전 관리, Railway에서 이전 배포로 즉시 복구
- **모니터링**: GitHub Actions 성공률, Gemini API 사용량

## 11. Release & Next Loop

### 1주 타임박스 (D+0 ~ D+7)
| 작업 | 예상시간 | 완료기준 | 맥북+Cursor 고려사항 |
|------|----------|----------|---------------------|
| 멀티 소스 수집기 | 2h | 10개 소스에서 RSS 수집 성공 | Cursor로 feedparser 빠른 구현 |
| 뉴스 우선 필터링 | 0.5h | 점수화 시스템, 50% 뉴스 비율 | 정규식과 키워드 매칭 |
| Gemini 번역/요약 | 1.5h | 영문→한글 번역 + 3문장 요약 | Google AI Studio API 키 발급 |
| 웹 UI + Railway | 0.5h | 카드→모달→원문 UI 완성 | Tailwind CSS 활용 |
| GitHub Actions | 0.5h | 자동 실행 성공 확인 | workflow yml 작성 |

### 베타 테스트
- 초대: 없음 (개인 사용)
- 피드백: 1주일간 뉴스 비율, 번역 품질, 요약 유용성 체크
- 평가: 매일 "도움된 글" 개수 메모

### 다음 루프 후보 (Backlog Top 5)
1. **Hacker News 통합** - 고품질 기술 뉴스 추가
2. **북마크 기능** - 나중에 읽을 글 저장
3. **PWA 변환** - 모바일 앱처럼 오프라인 읽기
4. **키워드 알림** - LLM 신기술 등장시 슬랙/이메일 알림
5. **읽기 패턴 분석** - 선호 주제 파악하여 개인화

## 12. 적합성 표

### 시간 적합성 ✅
| 작업 | 예상시간 | 여유 20% 포함 |
|------|----------|---------------|
| 총 개발 | 5h | 6h |
| 주당 한도 | 5h | - |
| **결과** | **✅ 적합** | **첫 주만 1h 초과** |

### 비용 적합성 ✅
| 항목 | 월 비용 | 상세 |
|------|---------|------|
| Google Translate | ₩0 | 무료 50만자 (충분) |
| Gemini Pro API | ₩0 | 무료 한도 (일 10개 요약 충분) |
| GitHub Actions | ₩0 | 무료 2,000분 (월 30회×15분 사용) |
| Railway 호스팅 | ₩0 | 무료 플랜 500시간 |
| **합계** | **₩0** | **완전 무료!** 🎉 |

### 리스크 Top 3 & 완화
1. **GitHub Actions 실패** → 이메일 알림 설정, 수동 트리거 버튼, 재시도 로직
2. **뉴스/블로그 비율 불균형** → 소스별 수집 개수 제한, 동적 조정 로직
3. **Gemini API 한도 초과** → 일일 처리량 모니터링, 캐싱으로 재요청 방지

---

## 13. 체크리스트

- [x] 시간/비용 한도 충족 (완전 무료)
- [x] FR당 Gherkin ≥2
- [x] 빈/로딩/오류 상태 정의
- [x] 이벤트 ≤5 & 모니터링 러프
- [x] PII/보안/접근성 항목
- [x] 베타 피드백 경로
- [x] 킬스위치/롤백 경로
- [x] GitHub Actions 자동화
- [x] 뉴스 중심 소스 구성 (50%)