# GitHub Actions 자동 수집 설정 가이드

## 📋 목차
1. [GitHub Secrets 설정](#github-secrets-설정)
2. [워크플로우 활성화 확인](#워크플로우-활성화-확인)
3. [수동 실행 방법](#수동-실행-방법)
4. [실행 로그 확인](#실행-로그-확인)
5. [문제 해결](#문제-해결)

---

## 1. GitHub Secrets 설정

### 필수 Secrets
GitHub Actions가 정상 작동하려면 다음 Secrets가 설정되어 있어야 합니다:

1. **GEMINI_API_KEY** (필수)
   - Gemini Pro API 키
   - 글 요약에 사용

2. **SECRET_KEY** (선택)
   - Flask 애플리케이션 시크릿 키
   - 기본값으로 설정되어 있어 선택사항

### 설정 방법

1. GitHub 저장소로 이동
   ```
   https://github.com/hjkim909/DS-News-Aggregator
   ```

2. **Settings** 탭 클릭

3. 왼쪽 사이드바에서 **Secrets and variables** > **Actions** 클릭

4. **New repository secret** 버튼 클릭

5. Secret 추가:
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: 여러분의 Gemini API 키 입력
   - **Add secret** 클릭

### ✅ Secret 확인 방법

설정된 Secrets 목록에서 다음이 표시되어야 합니다:
- ✓ `GEMINI_API_KEY` (Updated X days ago)
- ✓ `SECRET_KEY` (선택)

---

## 2. 워크플로우 활성화 확인

### 확인 방법

1. GitHub 저장소에서 **Actions** 탭 클릭

2. 워크플로우 목록 확인:
   - **Weekly News Collection** 워크플로우가 보여야 함

3. 워크플로우 상태 확인:
   - 비활성화되어 있다면 **Enable workflow** 버튼 클릭

### 현재 스케줄

```yaml
schedule:
  - cron: '0 23 * * 0'  # UTC 23:00 일요일 = KST 08:00 월요일
```

**실행 시간**: 매주 월요일 오전 8시 (한국 시간)

---

## 3. 수동 실행 방법

자동 스케줄을 기다리지 않고 즉시 수집을 실행하려면:

### 웹 인터페이스로 실행

1. GitHub 저장소 > **Actions** 탭

2. 왼쪽에서 **Weekly News Collection** 클릭

3. 오른쪽 상단 **Run workflow** 버튼 클릭

4. 브랜치 선택 (기본: `main`)

5. **Run workflow** 클릭

### 실행 결과 확인

- 실행이 시작되면 노란색 원 🟡 표시
- 성공하면 초록색 체크 ✅ 표시
- 실패하면 빨간색 X ❌ 표시

---

## 4. 실행 로그 확인

### 최근 실행 기록 보기

1. **Actions** 탭에서 워크플로우 클릭

2. 실행 목록에서 특정 실행 클릭

3. 각 단계의 로그 확인:
   - 📥 저장소 체크아웃
   - 🐍 Python 설정
   - 📦 의존성 설치
   - 🌐 환경변수 설정
   - **📰 뉴스 수집 실행** ← 가장 중요
   - 📊 결과 확인
   - 💾 커밋 및 푸시
   - 📋 수집 통계

### 에러 확인

각 단계를 클릭하면 상세 로그를 볼 수 있습니다. 에러가 있다면 빨간색으로 표시됩니다.

---

## 5. 문제 해결

### 문제 1: "GEMINI_API_KEY not found" 에러

**원인**: Secret이 설정되지 않음

**해결**:
1. [GitHub Secrets 설정](#github-secrets-설정) 참고
2. `GEMINI_API_KEY` 추가
3. 워크플로우 다시 실행

### 문제 2: "수집된 글이 없습니다"

**원인**: RSS 피드 문제 또는 필터링 설정

**해결**:
1. `config.py`의 RSS 피드 URL 확인
2. 로컬에서 테스트:
   ```bash
   python -c "from processors.pipeline import run_ds_news_pipeline; run_ds_news_pipeline()"
   ```

### 문제 3: "API rate limit exceeded"

**원인**: Gemini API 무료 한도 초과

**해결**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 에서 API 사용량 확인
2. 필요시 API 키 재발급 또는 유료 플랜 고려
3. `config.py`에서 수집량 조정:
   ```python
   NEWS_MEDIA_MAX_ARTICLES = 3  # 6 → 3으로 감소
   PRACTICAL_BLOG_MAX_ARTICLES = 2  # 4 → 2로 감소
   COMPANY_BLOG_MAX_ARTICLES = 1  # 3 → 1로 감소
   ```

### 문제 4: 스케줄이 실행되지 않음

**원인**: GitHub Actions의 cron 지연 또는 저장소 비활성화

**참고사항**:
- GitHub Actions의 cron은 정확한 시간에 실행되지 않을 수 있습니다 (최대 30분 지연 가능)
- 저장소가 60일 이상 활동이 없으면 워크플로우가 자동 비활성화됩니다

**해결**:
1. 저장소를 정기적으로 업데이트 (커밋)
2. 필요시 수동으로 실행 ([수동 실행 방법](#수동-실행-방법) 참고)

### 문제 5: 커밋 및 푸시 실패

**원인**: Git 권한 문제

**해결**:
1. `GITHUB_TOKEN`은 자동으로 제공되므로 별도 설정 불필요
2. 저장소 설정 > Actions > General > Workflow permissions 확인
3. **Read and write permissions** 선택되어야 함

---

## 📊 정상 실행 예시

성공적인 실행의 로그 예시:

```
===== 수집 완료 =====
수집: 32개 → 필터링: 9개 → 번역: 8개 → 요약: 9개 → 저장: 9개
소요시간: 0:01:05

✅ 수집 완료!
수집된 글 개수: 9

📊 총 글 개수: 9
📅 수집 날짜: 2025-10-13

📰 소스별 분포:
  - TechCrunch AI: 2개
  - MIT Technology Review: 2개
  - Towards Data Science: 2개
  - AWS Machine Learning Blog: 1개
  - Hugging Face Blog: 2개
```

---

## 🔗 관련 문서

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Gemini API 문서](https://ai.google.dev/docs)
- [프로젝트 ROADMAP](./ROADMAP.md)

---

**마지막 업데이트**: 2025-10-13

