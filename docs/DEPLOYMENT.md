# 🚀 DS News Aggregator 배포 가이드

이 문서는 DS News Aggregator를 Railway에 배포하는 방법을 설명합니다.

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Railway 배포](#railway-배포)
3. [환경 변수 설정](#환경-변수-설정)
4. [GitHub Actions 설정](#github-actions-설정)
5. [배포 확인](#배포-확인)
6. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 1. 필요한 계정

- ✅ **GitHub 계정**: 코드 저장소 관리
- ✅ **Railway 계정**: https://railway.app (GitHub 연동)
- ✅ **Google Gemini API 키**: https://makersuite.google.com/app/apikey

### 2. 프로젝트 준비

```bash
# Git 저장소 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub에 푸시
git remote add origin https://github.com/YOUR_USERNAME/DS_news_web.git
git push -u origin main
```

---

## Railway 배포

### 1단계: Railway 프로젝트 생성

1. **Railway 웹사이트 접속**: https://railway.app
2. **"Start a New Project"** 클릭
3. **"Deploy from GitHub repo"** 선택
4. GitHub 계정 연동 (처음이라면)
5. **DS_news_web 저장소** 선택

### 2단계: 자동 배포 확인

Railway가 자동으로:
- ✅ `railway.toml` 설정 파일 감지
- ✅ Python 환경 설정
- ✅ `requirements.txt` 패키지 설치
- ✅ Gunicorn으로 Flask 앱 실행

배포 로그를 확인하세요:
```
Building...
Installing dependencies from requirements.txt
Starting server with gunicorn
✅ Deployment successful!
```

### 3단계: 도메인 확인

1. **Railway 대시보드** → **Settings** → **Domains**
2. 자동 생성된 도메인 확인 (예: `ds-news-web-production.up.railway.app`)
3. 또는 **Generate Domain** 클릭하여 새 도메인 생성
4. (선택) **Custom Domain** 추가 가능

---

## 환경 변수 설정

### Railway 대시보드에서 설정

1. **Railway 대시보드** → **Variables** 탭 클릭
2. 다음 환경변수 추가:

#### 필수 환경변수

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `GEMINI_API_KEY` | `AIza...` | Google Gemini API 키 |
| `SECRET_KEY` | `랜덤문자열` | Flask 세션 암호화 키 |
| `PORT` | `5000` | Flask 앱 포트 (Railway 자동 설정) |

#### 선택적 환경변수

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `FLASK_ENV` | `production` | 운영 환경 |
| `FLASK_DEBUG` | `False` | 디버그 모드 off |

### SECRET_KEY 생성 방법

```bash
# Python으로 랜덤 키 생성
python -c "import secrets; print(secrets.token_hex(32))"
```

출력된 64자리 문자열을 `SECRET_KEY`로 사용하세요.

### 환경변수 추가 예시

```
# Railway 대시보드 → Variables 탭에서
GEMINI_API_KEY = AIzaSyB...your-actual-key...xyz
SECRET_KEY = a1b2c3d4e5f6...64자리...xyz123
PORT = 5000
FLASK_ENV = production
FLASK_DEBUG = False
```

**저장 후 자동 재배포됩니다!**

---

## GitHub Actions 설정

### 1단계: GitHub Secrets 설정

1. **GitHub 저장소** → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. 다음 Secrets 추가:

| Secret 이름 | 값 | 설명 |
|-------------|-----|------|
| `GEMINI_API_KEY` | `AIza...` | Google Gemini API 키 |
| `SECRET_KEY` | `랜덤문자열` | Flask 세션 암호화 키 |

### 2단계: GitHub Actions 워크플로우 확인

프로젝트에 이미 `.github/workflows/weekly_collect.yml` 파일이 있습니다.

**자동 실행 시간:**
- 📅 **매주 월요일 오전 8시 KST** (UTC 23:00 일요일)
- 자동으로 뉴스 수집 → 커밋 → 푸시

**수동 실행:**
1. **GitHub 저장소** → **Actions** 탭
2. **Weekly News Collection** 워크플로우 선택
3. **Run workflow** 버튼 클릭

### 3단계: 워크플로우 동작 확인

```bash
# 로컬에서 테스트 실행
python main.py

# data/articles.json 파일 생성 확인
ls -lh data/articles*.json
```

GitHub Actions 로그에서 다음을 확인:
```
✅ 수집 완료!
수집된 글 개수: 10
📰 주간 자동 수집: 2025-10-10 08:00 KST
✅ 커밋 및 푸시 완료
```

---

## 배포 확인

### 1. Railway 배포 상태

```bash
# Railway CLI 설치 (선택)
npm install -g @railway/cli

# 로그인
railway login

# 배포 로그 확인
railway logs
```

또는 Railway 대시보드에서:
- **Deployments** 탭 → 최신 배포 클릭 → 로그 확인

### 2. 웹사이트 접속

1. Railway 도메인 접속 (예: `https://your-app.up.railway.app`)
2. 다음 확인:
   - ✅ 메인 페이지 로드
   - ✅ 뉴스 카드 표시
   - ✅ 다크 모드 토글
   - ✅ 날짜 필터 동작
   - ✅ "수집하기" 버튼 동작

### 3. API 엔드포인트 테스트

```bash
# 글 목록 API
curl https://your-app.up.railway.app/api/articles

# 날짜 목록 API
curl https://your-app.up.railway.app/api/dates

# 시스템 상태 API
curl https://your-app.up.railway.app/api/status
```

---

## 트러블슈팅

### 문제 1: 배포는 성공했는데 사이트가 안 열려요

**원인**: 포트 설정 문제

**해결**:
```bash
# railway.toml 확인
[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT app:app"

# app.py 확인
port = int(os.environ.get('PORT', 5000))
```

### 문제 2: Gemini API 오류

**원인**: 환경변수 미설정

**해결**:
1. Railway 대시보드 → Variables 탭
2. `GEMINI_API_KEY` 확인
3. API 키가 정확한지 확인 (AIza로 시작)
4. Gemini API 활성화 확인: https://makersuite.google.com

### 문제 3: GitHub Actions가 실행되지 않아요

**원인**: GitHub Secrets 미설정

**해결**:
1. GitHub → Settings → Secrets → Actions
2. `GEMINI_API_KEY` 추가
3. `SECRET_KEY` 추가
4. Actions 탭에서 수동 실행 테스트

### 문제 4: 수집된 글이 0개예요

**원인**: RSS 피드 오류 또는 필터링 너무 엄격

**해결**:
```bash
# 로컬에서 테스트
python main.py

# 로그 확인
tail -f logs/app.log

# 필터링 점수 낮추기 (config.py)
QUALITY_THRESHOLD = 60  # 70 → 60으로 변경
```

### 문제 5: Railway 무료 플랜 한도 초과

**현재 상태 확인**:
- Railway 대시보드 → Usage 탭
- 무료 플랜: 월 500시간 ($5 상당)

**절약 방법**:
1. **슬립 모드 활성화**: 일정 시간 비활성시 자동 sleep
2. **최소 리소스 사용**:
   ```toml
   [resources]
   cpu = 1
   memory = 512  # 최소값
   ```
3. **지역 최적화**: Railway 대시보드에서 가까운 지역 선택

### 문제 6: 메모리 부족 오류

**증상**: `MemoryError` 또는 앱 크래시

**해결**:
```toml
# railway.toml
[resources]
memory = 1024  # 512 → 1024로 증가

# 또는 gunicorn workers 줄이기
[deploy]
startCommand = "gunicorn --workers=1 --bind 0.0.0.0:$PORT app:app"
```

---

## 배포 체크리스트

배포 전 확인:

- [ ] GitHub에 코드 푸시 완료
- [ ] `railway.toml` 파일 존재
- [ ] `requirements.txt` 최신 버전
- [ ] `.env.example` 파일 작성
- [ ] Railway 프로젝트 생성
- [ ] Railway 환경변수 설정 (`GEMINI_API_KEY`, `SECRET_KEY`)
- [ ] Railway 도메인 확인
- [ ] GitHub Secrets 설정 (`GEMINI_API_KEY`, `SECRET_KEY`)
- [ ] GitHub Actions 워크플로우 확인
- [ ] 웹사이트 접속 테스트
- [ ] API 엔드포인트 테스트
- [ ] 자동 수집 스케줄 확인

---

## 추가 리소스

### 공식 문서

- **Railway 문서**: https://docs.railway.app
- **GitHub Actions 문서**: https://docs.github.com/actions
- **Flask 배포 가이드**: https://flask.palletsprojects.com/deploying/
- **Gunicorn 문서**: https://docs.gunicorn.org

### 유용한 명령어

```bash
# Railway CLI
railway init          # 프로젝트 초기화
railway up            # 배포
railway logs          # 로그 확인
railway open          # 브라우저에서 열기
railway env           # 환경변수 확인
railway status        # 상태 확인

# Git 관련
git status            # 변경사항 확인
git log --oneline     # 커밋 히스토리
git pull              # 최신 코드 받기

# Python 관련
python main.py        # 로컬 수집 테스트
python app.py         # 로컬 서버 실행
pip list              # 설치된 패키지 확인
```

---

## 도움이 필요하신가요?

- **GitHub Issues**: 버그 신고 및 기능 제안
- **Discussions**: 질문 및 토론
- **Email**: your-email@example.com

---

**🎉 배포 완료! 이제 매일 자동으로 최신 AI/ML 뉴스를 받아보세요!**

