# 🗺️ DS News Aggregator - 기능 추가 로드맵

## 📅 Phase 7: Advanced Features

### 우선순위: 높음

---

## 1️⃣ 중복 방지 시스템 (Priority: HIGH)

### 목표
- URL 해시 기반 중복 기사 자동 제거
- 동일 기사가 여러 소스에서 수집되는 경우 처리
- 히스토리 기반 중복 체크

### 구현 계획

#### 1.1 URL 해시 시스템
```python
# utils/deduplication.py
import hashlib
import json
from datetime import datetime, timedelta

class ArticleDeduplicator:
    def __init__(self, history_file='data/article_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def get_url_hash(self, url):
        """URL을 해시로 변환"""
        # URL 정규화 (쿼리 파라미터 제거 등)
        normalized_url = self._normalize_url(url)
        return hashlib.md5(normalized_url.encode()).hexdigest()
    
    def is_duplicate(self, url, days=7):
        """최근 N일 이내 중복 체크"""
        url_hash = self.get_url_hash(url)
        if url_hash in self.history:
            collected_date = datetime.fromisoformat(self.history[url_hash])
            if datetime.now() - collected_date < timedelta(days=days):
                return True
        return False
    
    def mark_collected(self, url):
        """수집 기록 저장"""
        url_hash = self.get_url_hash(url)
        self.history[url_hash] = datetime.now().isoformat()
        self._save_history()
```

#### 1.2 파이프라인 통합
```python
# processors/pipeline.py 수정
from utils.deduplication import ArticleDeduplicator

def step2_filter_articles(all_articles):
    deduplicator = ArticleDeduplicator()
    
    # 중복 제거
    unique_articles = []
    for article in all_articles:
        if not deduplicator.is_duplicate(article['url']):
            unique_articles.append(article)
            deduplicator.mark_collected(article['url'])
    
    logger.info(f"중복 제거: {len(all_articles)} → {len(unique_articles)}개")
    return unique_articles
```

#### 1.3 히스토리 관리
- **저장 주기**: 매 수집시 자동 저장
- **정리 주기**: 30일 이상 된 기록 자동 삭제
- **파일 크기**: JSON 압축 저장으로 용량 최적화

### 예상 작업 시간: **2-3시간**

---

## 2️⃣ 추가 뉴스 소스 (Priority: HIGH)

### 목표
- AI/ML 관련 해외/국내 뉴스 소스 10개 이상 확보
- 소스별 품질 검증 및 점수 조정
- RSS 피드 안정성 확인

### 추가할 소스 리스트

#### 2.1 해외 뉴스 미디어 (추가 5개)
| 소스 | RSS URL | 기본점수 | 특징 |
|------|---------|---------|------|
| **AI News** | https://www.artificialintelligence-news.com/feed/ | 100 | AI 전문 뉴스 |
| **VentureBeat** | https://venturebeat.com/category/ai/feed/ | 100 | AI 비즈니스 |
| **Ars Technica AI** | https://feeds.arstechnica.com/arstechnica/technology-lab | 95 | 기술 심층 분석 |
| **The Register AI** | https://www.theregister.com/software/ai_ml/headlines.atom | 90 | AI/ML 뉴스 |
| **InfoQ AI** | https://feed.infoq.com/ai-ml-data-eng/ | 90 | AI 엔지니어링 |

#### 2.2 국내 뉴스 미디어 (추가 3개)
| 소스 | RSS URL | 기본점수 | 특징 |
|------|---------|---------|------|
| **AI타임즈** | https://www.aitimes.com/rss/allArticle.xml | 85 | 국내 AI 뉴스 |
| **데이터넷** | http://www.datanet.co.kr/news/rss.xml | 80 | 데이터/AI 산업 |
| **디지털투데이** | https://www.digitaltoday.co.kr/rss/allArticle.xml | 80 | IT/AI 뉴스 |

#### 2.3 실용 블로그 (추가 3개)
| 소스 | RSS URL | 기본점수 | 특징 |
|------|---------|---------|------|
| **Machine Learning Mastery** | https://machinelearningmastery.com/feed/ | 85 | 실용 가이드 |
| **Distill.pub** | https://distill.pub/rss.xml | 90 | 인터랙티브 ML 논문 |
| **Papers With Code** | https://paperswithcode.com/latest/rss | 85 | 최신 AI 논문 코드 |

### 구현 계획

#### 2.1 config.py 업데이트
```python
# 추가 뉴스 소스
NEWS_MEDIA_SOURCES = {
    # 기존 소스...
    'ai_news': {
        'name': 'AI News',
        'rss_url': 'https://www.artificialintelligence-news.com/feed/',
        'base_score': 100
    },
    'venturebeat': {
        'name': 'VentureBeat',
        'rss_url': 'https://venturebeat.com/category/ai/feed/',
        'base_score': 100
    },
    # ... 나머지 소스
}
```

#### 2.2 RSS 피드 검증
- 각 소스별 RSS 유효성 검사
- 404/500 오류 처리
- 대체 RSS URL 확보

### 예상 작업 시간: **3-4시간**

---

## 3️⃣ 검색 기능 (Priority: MEDIUM)

### 목표
- 제목/내용/태그 기반 실시간 검색
- 검색 결과 하이라이팅
- 검색 히스토리 저장

### 기능 명세

#### 3.1 검색 UI
```html
<!-- dashboard.html에 추가 -->
<div class="search-container mb-6">
    <div class="relative">
        <input type="text" 
               id="searchInput"
               placeholder="🔍 제목, 내용, 태그로 검색..."
               class="w-full px-4 py-3 pl-12 rounded-lg border-2 border-gray-300 
                      focus:border-blue-500 focus:outline-none dark:bg-gray-800 
                      dark:border-gray-600 dark:text-gray-200"
               oninput="searchArticles(this.value)">
        <i class="fas fa-search absolute left-4 top-4 text-gray-400"></i>
        <button id="clearSearch" 
                class="absolute right-4 top-3 text-gray-400 hover:text-gray-600 hidden"
                onclick="clearSearch()">
            <i class="fas fa-times-circle"></i>
        </button>
    </div>
</div>
```

#### 3.2 검색 로직
```javascript
// static/app.js에 추가
function searchArticles(query) {
    console.log('검색:', query);
    
    if (!query || query.trim() === '') {
        // 검색어 없으면 모든 카드 표시
        showAllArticles();
        hideElement(elements.clearSearchBtn);
        return;
    }
    
    const lowerQuery = query.toLowerCase();
    const allCards = document.querySelectorAll('.article-card');
    let matchCount = 0;
    
    allCards.forEach(card => {
        const articleId = card.dataset.articleId;
        const article = articlesData.find(a => a.id === articleId);
        
        if (!article) {
            card.style.display = 'none';
            return;
        }
        
        // 제목, 내용, 태그에서 검색
        const titleMatch = (article.title_ko || '').toLowerCase().includes(lowerQuery);
        const contentMatch = (article.content_ko || '').toLowerCase().includes(lowerQuery);
        const summaryMatch = (article.summary || '').toLowerCase().includes(lowerQuery);
        const tagsMatch = (article.tags || []).some(tag => 
            tag.toLowerCase().includes(lowerQuery)
        );
        
        if (titleMatch || contentMatch || summaryMatch || tagsMatch) {
            card.style.display = 'block';
            highlightText(card, query);
            matchCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    showElement(elements.clearSearchBtn);
    showToast(`${matchCount}개 검색 결과`, 'info');
}

function highlightText(element, query) {
    // 검색어 하이라이팅
    const title = element.querySelector('h3');
    if (title) {
        const originalText = title.textContent;
        const regex = new RegExp(`(${query})`, 'gi');
        title.innerHTML = originalText.replace(regex, 
            '<mark class="bg-yellow-300 dark:bg-yellow-600">$1</mark>'
        );
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    showAllArticles();
    hideElement(elements.clearSearchBtn);
    
    // 하이라이팅 제거
    document.querySelectorAll('mark').forEach(mark => {
        mark.outerHTML = mark.textContent;
    });
}
```

#### 3.3 검색 히스토리 (선택)
```javascript
// 최근 검색어 저장
const SEARCH_HISTORY_KEY = 'ds_news_search_history';

function saveSearchHistory(query) {
    let history = JSON.parse(localStorage.getItem(SEARCH_HISTORY_KEY) || '[]');
    history = [query, ...history.filter(q => q !== query)].slice(0, 10);
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history));
}

function showSearchSuggestions() {
    const history = JSON.parse(localStorage.getItem(SEARCH_HISTORY_KEY) || '[]');
    // 드롭다운으로 최근 검색어 표시
}
```

### 예상 작업 시간: **4-5시간**

---

## 📊 전체 작업 계획

### Timeline (추천 순서)

```
Week 1: 중복 방지 시스템 (2-3시간)
├── Day 1: ArticleDeduplicator 클래스 구현
├── Day 2: 파이프라인 통합 및 테스트
└── Day 3: 히스토리 관리 및 최적화

Week 2: 추가 뉴스 소스 (3-4시간)
├── Day 1: RSS 피드 검증 (5개 소스)
├── Day 2: config.py 업데이트 및 수집기 통합
└── Day 3: 전체 테스트 및 점수 조정

Week 3: 검색 기능 (4-5시간)
├── Day 1: 검색 UI 구현
├── Day 2: 검색 로직 및 하이라이팅
└── Day 3: 검색 히스토리 및 최적화
```

### 우선순위 추천

1. **중복 방지 시스템** (가장 시급)
   - 현재 중복 기사가 수집될 수 있음
   - 데이터 품질 향상에 필수

2. **추가 뉴스 소스** (콘텐츠 확장)
   - 더 다양한 뉴스 제공
   - 사용자 만족도 향상

3. **검색 기능** (사용성 개선)
   - 많은 기사 중 원하는 내용 빠르게 찾기
   - UX 향상

---

## 🎯 완료 후 기대 효과

### 중복 방지 시스템
- ✅ 데이터 품질 30% 향상
- ✅ 저장 공간 절약
- ✅ 사용자가 같은 기사를 반복해서 보지 않음

### 추가 뉴스 소스
- ✅ 뉴스 수집량 2배 증가 (10→20개/주)
- ✅ 다양한 관점의 AI 뉴스 제공
- ✅ 국내외 균형잡힌 소스 구성

### 검색 기능
- ✅ 원하는 기사 찾는 시간 90% 단축
- ✅ 특정 주제 집중 탐색 가능
- ✅ 사용자 경험 크게 향상

---

## 📝 구현 체크리스트

### 중복 방지 시스템
- [ ] ArticleDeduplicator 클래스 구현
- [ ] URL 정규화 함수
- [ ] 히스토리 파일 저장/로드
- [ ] 파이프라인 통합
- [ ] 30일 자동 정리 크론잡
- [ ] 테스트 및 검증

### 추가 뉴스 소스
- [ ] RSS 피드 URL 검증 (8개)
- [ ] config.py 업데이트
- [ ] 수집기 통합
- [ ] 점수 시스템 조정
- [ ] 에러 핸들링
- [ ] 전체 테스트

### 검색 기능
- [ ] 검색 UI 구현
- [ ] searchArticles() 함수
- [ ] highlightText() 함수
- [ ] clearSearch() 함수
- [ ] 검색 히스토리 (선택)
- [ ] 반응형 디자인 확인
- [ ] 성능 최적화

---

**다음에 어떤 기능부터 구현할까요?** 😊

