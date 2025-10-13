# 🔄 중복 뉴스 제거 시스템 설계

> **목표:** URL 기반 중복 제거로 데이터 품질 향상 및 사용자 경험 개선

---

## 📋 목차

1. [문제 정의](#문제-정의)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [Phase 1: URL 해시 기반 중복 제거](#phase-1-url-해시-기반-중복-제거)
4. [Phase 2: 고급 중복 감지](#phase-2-고급-중복-감지)
5. [구현 계획](#구현-계획)
6. [테스트 계획](#테스트-계획)

---

## 🎯 문제 정의

### 현재 문제점

1. **동일 URL 중복**
   - 같은 뉴스가 여러 번 수집될 수 있음
   - 날짜별 파일 간 중복 체크 없음

2. **다른 소스의 같은 뉴스**
   - TechCrunch와 WIRED가 같은 뉴스를 다른 URL로 게재
   - 제목만 살짝 다르고 내용은 동일

3. **사용자 경험 저하**
   - 이미 본 글이 다시 나타남
   - 실제 새로운 뉴스가 적음

### 목표

- ✅ 중복 뉴스 95% 이상 제거
- ✅ 데이터 품질 30% 향상
- ✅ 저장 공간 30% 절약
- ✅ 사용자 만족도 향상

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    수집 파이프라인                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 글 수집 (TechCrunch, MIT, OpenAI, etc.)            │
│  - 32개 수집                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1.5: 중복 제거 (NEW!) 🔥                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ArticleDeduplicator                                   │  │
│  │ - URL 해시 체크                                        │  │
│  │ - 히스토리 파일 확인                                    │  │
│  │ - 제목 유사도 분석 (Phase 2)                           │  │
│  └───────────────────────────────────────────────────────┘  │
│  - 32개 → 24개 (8개 중복 제거)                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 콘텐츠 필터링                                        │
│  - 24개 → 9개                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3-5: 번역 → 요약 → 저장                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔨 Phase 1: URL 해시 기반 중복 제거

### 1.1 ArticleDeduplicator 클래스

**파일:** `processors/deduplicator.py`

```python
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set

class ArticleDeduplicator:
    """
    URL 해시 기반 중복 제거 시스템
    """
    
    def __init__(self, history_file: str = 'data/.dedup_history.json', 
                 retention_days: int = 30):
        """
        Args:
            history_file: 히스토리 파일 경로
            retention_days: 히스토리 보관 기간 (일)
        """
        self.history_file = history_file
        self.retention_days = retention_days
        self.url_hashes: Set[str] = set()
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'unique_articles': 0
        }
        
        # 히스토리 로드
        self._load_history()
    
    def _hash_url(self, url: str) -> str:
        """URL을 SHA256 해시로 변환"""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()
    
    def _load_history(self):
        """히스토리 파일 로드"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    
                # 30일 이내 URL만 로드
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                
                for entry in data.get('urls', []):
                    collected_date = datetime.fromisoformat(entry['collected_at'])
                    if collected_date > cutoff_date:
                        self.url_hashes.add(entry['hash'])
                        
            except Exception as e:
                print(f"히스토리 로드 실패: {e}")
                self.url_hashes = set()
        else:
            self.url_hashes = set()
    
    def _save_history(self):
        """히스토리 파일 저장"""
        # 최신 30일 데이터만 저장
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        urls_data = []
        for url_hash in self.url_hashes:
            urls_data.append({
                'hash': url_hash,
                'collected_at': datetime.now().isoformat()
            })
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'retention_days': self.retention_days,
            'total_urls': len(urls_data),
            'urls': urls_data
        }
        
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """
        URL 기반 중복 체크
        
        Args:
            article: 체크할 기사
            
        Returns:
            True if duplicate, False otherwise
        """
        url = article.get('url', '')
        if not url:
            return False
        
        url_hash = self._hash_url(url)
        return url_hash in self.url_hashes
    
    def add_article(self, article: Dict[str, Any]):
        """URL 해시 추가"""
        url = article.get('url', '')
        if url:
            url_hash = self._hash_url(url)
            self.url_hashes.add(url_hash)
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 제거 메인 메서드
        
        Args:
            articles: 체크할 기사 목록
            
        Returns:
            중복이 제거된 기사 목록
        """
        unique_articles = []
        
        for article in articles:
            self.stats['total_checked'] += 1
            
            if not self.is_duplicate(article):
                unique_articles.append(article)
                self.add_article(article)
                self.stats['unique_articles'] += 1
            else:
                self.stats['duplicates_found'] += 1
        
        # 히스토리 저장
        self._save_history()
        
        return unique_articles
    
    def get_stats(self) -> Dict[str, Any]:
        """중복 제거 통계 반환"""
        return {
            'total_checked': self.stats['total_checked'],
            'duplicates_found': self.stats['duplicates_found'],
            'unique_articles': self.stats['unique_articles'],
            'duplicate_rate': f"{self.stats['duplicates_found'] / max(self.stats['total_checked'], 1) * 100:.1f}%",
            'history_size': len(self.url_hashes)
        }
```

### 1.2 파이프라인 통합

**파일:** `processors/pipeline.py`

```python
from processors.deduplicator import ArticleDeduplicator

class DSNewsPipeline:
    def __init__(self, config: Config = None):
        # ... 기존 코드 ...
        
        # 중복 제거 시스템 추가
        self.deduplicator = ArticleDeduplicator()
    
    def step1_5_remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        1.5단계: 중복 제거 (NEW!)
        """
        self._log_stage_start("중복 제거")
        
        try:
            unique_articles = self.deduplicator.remove_duplicates(articles)
            
            # 통계 출력
            stats = self.deduplicator.get_stats()
            logger.info(f"중복 제거 완료: {stats}")
            logger.info(f"  - 전체: {stats['total_checked']}개")
            logger.info(f"  - 중복: {stats['duplicates_found']}개 ({stats['duplicate_rate']})")
            logger.info(f"  - 고유: {stats['unique_articles']}개")
            
            self.pipeline_stats['duplicates_removed'] = stats['duplicates_found']
            
        except Exception as e:
            logger.error(f"중복 제거 실패: {e}")
            unique_articles = articles  # 실패시 원본 반환
        
        self._log_stage_end("중복 제거", len(unique_articles))
        return unique_articles
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        # ... 기존 코드 ...
        
        # 1단계: 글 수집
        articles = self.step1_collect_articles()
        
        # 1.5단계: 중복 제거 (NEW!)
        articles = self.step1_5_remove_duplicates(articles)
        
        # 2단계: 콘텐츠 필터링
        articles = self.step2_filter_articles(articles)
        
        # ... 나머지 단계 ...
```

### 1.3 히스토리 파일 구조

**파일:** `data/.dedup_history.json`

```json
{
  "last_updated": "2025-10-13T18:00:00",
  "retention_days": 30,
  "total_urls": 245,
  "urls": [
    {
      "hash": "a3f5d9e8c2b1...",
      "collected_at": "2025-10-13T10:30:00"
    },
    {
      "hash": "b2e4c7a9f3d8...",
      "collected_at": "2025-10-12T08:15:00"
    }
  ]
}
```

---

## 🚀 Phase 2: 고급 중복 감지

### 2.1 제목 유사도 분석

**라이브러리:** `python-Levenshtein`

```python
from Levenshtein import ratio

class AdvancedDeduplicator(ArticleDeduplicator):
    """고급 중복 감지 시스템"""
    
    def __init__(self, similarity_threshold: float = 0.85, **kwargs):
        super().__init__(**kwargs)
        self.similarity_threshold = similarity_threshold
        self.title_cache: List[str] = []
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """
        두 제목의 유사도 계산
        
        Returns:
            0.0 ~ 1.0 (1.0 = 완전 동일)
        """
        # 소문자 변환 및 공백 정규화
        t1 = ' '.join(title1.lower().split())
        t2 = ' '.join(title2.lower().split())
        
        # Levenshtein distance 기반 유사도
        return ratio(t1, t2)
    
    def is_duplicate_advanced(self, article: Dict[str, Any]) -> bool:
        """
        URL + 제목 유사도 기반 중복 체크
        """
        # 1. URL 중복 체크 (기존)
        if self.is_duplicate(article):
            return True
        
        # 2. 제목 유사도 체크 (신규)
        current_title = article.get('title', '')
        if not current_title:
            return False
        
        for cached_title in self.title_cache:
            similarity = self._title_similarity(current_title, cached_title)
            
            if similarity >= self.similarity_threshold:
                # 85% 이상 유사하면 중복으로 간주
                logger.info(f"제목 유사도 중복 감지: {similarity*100:.1f}%")
                logger.info(f"  - 기존: {cached_title[:50]}...")
                logger.info(f"  - 신규: {current_title[:50]}...")
                return True
        
        return False
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 제거 (고급)"""
        unique_articles = []
        
        for article in articles:
            if not self.is_duplicate_advanced(article):
                unique_articles.append(article)
                self.add_article(article)
                
                # 제목 캐시 추가
                title = article.get('title', '')
                if title:
                    self.title_cache.append(title)
            
        self._save_history()
        return unique_articles
```

### 2.2 콘텐츠 핑거프린팅

```python
def _content_fingerprint(self, content: str, n: int = 100) -> str:
    """
    콘텐츠의 처음 n개 단어로 핑거프린트 생성
    """
    words = content.lower().split()[:n]
    text = ' '.join(words)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
```

---

## 📅 구현 계획

### Week 1: Phase 1 구현

**Day 1-2: ArticleDeduplicator 클래스**
- [ ] `processors/deduplicator.py` 생성
- [ ] URL 해시 메서드 구현
- [ ] 히스토리 로드/저장 구현
- [ ] 단위 테스트 작성

**Day 3-4: 파이프라인 통합**
- [ ] `pipeline.py`에 `step1_5_remove_duplicates()` 추가
- [ ] 로깅 및 통계 추가
- [ ] 통합 테스트

**Day 5: 히스토리 관리**
- [ ] 30일 자동 정리 구현
- [ ] 파일 크기 제한
- [ ] `.gitignore`에 히스토리 파일 추가

### Week 2-3: Phase 2 구현

**Week 2: 제목 유사도**
- [ ] `python-Levenshtein` 설치
- [ ] `AdvancedDeduplicator` 클래스 구현
- [ ] 제목 캐시 관리
- [ ] 유사도 임계값 튜닝

**Week 3: 콘텐츠 핑거프린팅**
- [ ] 콘텐츠 해시 메서드 구현
- [ ] 성능 최적화
- [ ] 전체 시스템 테스트

---

## 🧪 테스트 계획

### 단위 테스트

```python
# tests/test_deduplicator.py

def test_url_hash():
    """URL 해시 생성 테스트"""
    dedup = ArticleDeduplicator()
    hash1 = dedup._hash_url("https://example.com/article1")
    hash2 = dedup._hash_url("https://example.com/article1")
    hash3 = dedup._hash_url("https://example.com/article2")
    
    assert hash1 == hash2
    assert hash1 != hash3

def test_duplicate_detection():
    """중복 감지 테스트"""
    dedup = ArticleDeduplicator()
    
    article1 = {'url': 'https://example.com/1', 'title': 'Test'}
    article2 = {'url': 'https://example.com/1', 'title': 'Test'}
    
    assert not dedup.is_duplicate(article1)
    dedup.add_article(article1)
    assert dedup.is_duplicate(article2)

def test_title_similarity():
    """제목 유사도 테스트"""
    dedup = AdvancedDeduplicator()
    
    title1 = "OpenAI releases GPT-5"
    title2 = "OpenAI Releases GPT-5"
    title3 = "Google releases Gemini 2.0"
    
    sim1 = dedup._title_similarity(title1, title2)
    sim2 = dedup._title_similarity(title1, title3)
    
    assert sim1 > 0.95  # 거의 동일
    assert sim2 < 0.5   # 매우 다름
```

### 통합 테스트

```python
def test_pipeline_integration():
    """파이프라인 통합 테스트"""
    pipeline = DSNewsPipeline()
    
    # 중복 포함 기사 수집
    articles = [
        {'url': 'https://example.com/1', 'title': 'Article 1'},
        {'url': 'https://example.com/1', 'title': 'Article 1'},  # 중복
        {'url': 'https://example.com/2', 'title': 'Article 2'},
    ]
    
    unique = pipeline.step1_5_remove_duplicates(articles)
    
    assert len(unique) == 2
    assert pipeline.deduplicator.stats['duplicates_found'] == 1
```

---

## 📊 성공 지표

### Phase 1 목표
- ✅ URL 중복 100% 제거
- ✅ 히스토리 파일 크기 < 1MB
- ✅ 중복 제거 속도 < 100ms (100개 기사 기준)

### Phase 2 목표
- ✅ 제목 유사 중복 80% 이상 감지
- ✅ False Positive < 5%
- ✅ 전체 중복 제거율 95% 이상

---

## 🔧 설정 옵션

**config.py에 추가:**

```python
# 중복 제거 설정
DEDUP_ENABLED = True
DEDUP_HISTORY_FILE = 'data/.dedup_history.json'
DEDUP_RETENTION_DAYS = 30
DEDUP_TITLE_SIMILARITY_THRESHOLD = 0.85
DEDUP_USE_ADVANCED = False  # Phase 2 기능
```

---

## 📝 마이그레이션 계획

### 기존 데이터 처리

1. **히스토리 초기화**
   ```bash
   python -c "from processors.deduplicator import ArticleDeduplicator; 
              d = ArticleDeduplicator(); 
              d._save_history()"
   ```

2. **기존 글 URL 추가**
   ```python
   # 최근 30일 데이터에서 URL 추출
   for date_file in recent_files:
       articles = load_articles(date_file)
       for article in articles:
           dedup.add_article(article)
   ```

---

## 🎯 다음 단계

Phase 1 완료 후:
1. Phase 2 구현 검토
2. 사용자 피드백 수집
3. 성능 모니터링
4. 필요시 추가 최적화

---

**최종 업데이트:** 2025-10-13
**담당자:** hjkim909
**우선순위:** URGENT 🔥

