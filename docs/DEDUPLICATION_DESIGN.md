# 🔄 중복 뉴스 제거 시스템 설계 (간단 버전)

> **목표:** URL 기반 간단한 중복 제거로 데이터 품질 향상

**설계 원칙:** Keep It Simple! ✨

---

## 📋 문제 정의

### 현재 문제점
- 같은 URL의 뉴스가 여러 번 수집될 수 있음
- 사용자가 중복된 글을 보게 됨

### 목표
- ✅ 같은 URL의 중복 100% 제거
- ✅ 간단하고 효과적인 구현 (10줄 이내)
- ✅ 성능 영향 최소화

---

## 💡 간단한 해결책

### 방법 1: URL Set으로 중복 체크 (추천!) 

**아이디어:**
- 수집하면서 URL을 Set에 저장
- 이미 있는 URL이면 스킵
- **끝!**

**장점:**
- ✅ 구현 10줄
- ✅ 100% URL 중복 제거
- ✅ 빠름 (O(1) 조회)
- ✅ 추가 파일 불필요

### 방법 2: RSS 수집 기간 제한

**아이디어:**
- RSS 피드에서 최근 7~14일만 가져오기
- 오래된 글 자동 필터링

**장점:**
- ✅ 더 간단 (RSS 파라미터만 조정)
- ✅ 데이터 신선도 유지
- ✅ 자연스러운 중복 감소

### 최종 선택: 방법 1

**이유:**
- 구현이 매우 간단
- 효과 확실
- 성능 걱정 없음

---

## 🔨 구현

### Step 1: pipeline.py 수정

```python
class DSNewsPipeline:
    def __init__(self, config: Config = None):
        # ... 기존 코드 ...
        self.collected_urls = set()  # ✨ 이것만 추가!
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        간단한 URL 기반 중복 제거
        """
        unique_articles = []
        duplicates = 0
        
        for article in articles:
            url = article.get('url', '')
            
            # URL이 없거나 이미 수집된 경우 스킵
            if not url or url in self.collected_urls:
                duplicates += 1
                continue
            
            # 새로운 URL이면 추가
            unique_articles.append(article)
            self.collected_urls.add(url)
        
        logger.info(f"✂️ 중복 제거: {len(articles)}개 → {len(unique_articles)}개 (중복 {duplicates}개)")
        
        return unique_articles
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        # ... 기존 코드 ...
        
        # 1단계: 글 수집
        articles = self.step1_collect_articles()
        
        # 1.5단계: 중복 제거 (NEW!)
        articles = self.remove_duplicates(articles)
        
        # 2단계: 콘텐츠 필터링
        articles = self.step2_filter_articles(articles)
        
        # ... 나머지 단계 ...
```

**끝!** 10줄로 해결! 🎉

---

## 🧪 테스트

### 간단한 테스트

```python
# test_deduplication.py

def test_remove_duplicates():
    """중복 제거 테스트"""
    pipeline = DSNewsPipeline()
    
    # 중복 포함 기사
    articles = [
        {'url': 'https://example.com/1', 'title': 'Article 1'},
        {'url': 'https://example.com/1', 'title': 'Article 1'},  # 중복!
        {'url': 'https://example.com/2', 'title': 'Article 2'},
        {'url': 'https://example.com/2', 'title': 'Article 2'},  # 중복!
        {'url': 'https://example.com/3', 'title': 'Article 3'},
    ]
    
    unique = pipeline.remove_duplicates(articles)
    
    assert len(unique) == 3  # 3개만 남아야 함
    assert len(pipeline.collected_urls) == 3  # URL도 3개
```

### 실제 실행 테스트

```bash
# 로컬에서 테스트
python -c "from processors.pipeline import run_ds_news_pipeline; run_ds_news_pipeline()"

# 로그 확인
# ✂️ 중복 제거: 32개 → 28개 (중복 4개)
```

---

## 📊 예상 효과

### Before (중복 제거 전)
```
수집: 32개
├─ TechCrunch: 8개
├─ MIT Tech: 8개  
└─ OpenAI: 6개 (일부 중복!)
    ↓
필터링: 9개
```

### After (중복 제거 후)
```
수집: 32개
    ↓
✂️ 중복 제거: 28개 (4개 중복 제거)
├─ TechCrunch: 7개
├─ MIT Tech: 7개
└─ OpenAI: 5개
    ↓
필터링: 9개 (더 다양한 소스)
```

### 개선 효과
- ✅ URL 중복 100% 제거
- ✅ 데이터 품질 향상
- ✅ 다양한 글 보장
- ✅ 코드 10줄 추가

---

## ⏱️ 구현 일정

### 즉시 구현 가능! (30분)

```
1. pipeline.py 열기                    (1분)
2. __init__에 self.collected_urls 추가  (1분)
3. remove_duplicates() 메서드 추가      (10분)
4. run_full_pipeline()에 호출 추가      (2분)
5. 테스트                               (10분)
6. 커밋 & 푸시                          (5분)
─────────────────────────────────────────
총 소요 시간: 30분
```

---

## 🚀 배포

### 자동 배포
```
git add processors/pipeline.py
git commit -m "✂️ 중복 뉴스 제거 기능 추가

- URL 기반 간단한 중복 제거
- Set을 사용한 O(1) 조회
- 로그에 중복 통계 표시"

git push origin main
```

→ GitHub Actions 자동 실행  
→ Railway 자동 재배포  
→ 다음 수집부터 중복 제거 적용! ✨

---

## 📝 추가 고려사항 (선택)

### 나중에 필요하면 추가

1. **영구 저장** (현재는 메모리만)
   - 파이프라인 실행마다 Set 초기화됨
   - 필요하면 파일로 저장 가능
   - 하지만 지금은 괜찮음!

2. **날짜별 파일 중복 체크**
   - 기존 날짜별 파일도 체크하고 싶다면
   - 시작 시 최근 파일 URL 로드
   - 하지만 복잡해질 수 있음

3. **제목 유사도**
   - 다른 URL이지만 같은 뉴스
   - 복잡하고 효과 불확실
   - 나중에 문제되면 고려

**결론:** 현재 간단한 방법으로 충분! ✅

---

## 🎯 성공 기준

- ✅ 코드 10~20줄 이내
- ✅ URL 중복 100% 제거
- ✅ 성능 저하 없음 (<10ms 추가)
- ✅ 30분 내 구현 완료

---

**최종 업데이트:** 2025-10-13  
**담당자:** hjkim909  
**상태:** 설계 완료, 구현 대기  
**예상 소요:** 30분
