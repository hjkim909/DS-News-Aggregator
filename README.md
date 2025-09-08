# 🤖 DS News Aggregator

> **데이터 사이언티스트를 위한 스마트 뉴스 큐레이션 시스템**  
> Reddit + 한국 기술블로그에서 DS/ML 관련 고품질 글을 자동 수집하고, AI로 번역/요약하여 카드 형태로 제공

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

## 📋 목차

- [🎯 프로젝트 개요](#-프로젝트-개요)
- [✨ 주요 기능](#-주요-기능)  
- [🛠 기술 스택](#-기술-스택)
- [🚀 설치 및 실행](#-설치-및-실행)
- [🔑 API 키 설정](#-api-키-설정)
- [🌐 웹 인터페이스](#-웹-인터페이스)
- [📊 데이터 수집 방식](#-데이터-수집-방식)
- [🚢 배포 방법](#-배포-방법)
- [⏰ 자동화 설정](#-자동화-설정)
- [📝 사용법](#-사용법)
- [🔧 개발자 가이드](#-개발자-가이드)
- [🤝 기여하기](#-기여하기)
- [📜 라이선스](#-라이선스)

## 🎯 프로젝트 개요

DS News Aggregator는 데이터 사이언티스트와 ML 엔지니어를 위한 개인 뉴스 큐레이션 시스템입니다. 

### 🎨 주요 특징

- **🌍 다채널 수집**: Reddit(r/MachineLearning, r/datascience) + 한국 기술블로그(네이버 D2, 카카오테크, AI타임스)
- **🧠 스마트 필터링**: 점수화 시스템으로 고품질 글만 선별 (잡담/단순질문 제외)
- **🌐 AI 번역/요약**: Google Translate + Gemini Pro로 영문→한국어 번역 및 3문장 요약
- **📱 모던 웹UI**: 반응형 디자인 + 다크모드 + 카드 형태 표시
- **⚡ 실시간 모달**: 카드 클릭 → 모달 → 번역 전문 → 원문 링크
- **💾 읽은글 관리**: localStorage 기반 읽음 상태 추적

## ✨ 주요 기능

### 📊 지능형 수집 시스템
- **Reddit API**: upvote 5개 이상 고품질 글만 선별
- **RSS 파싱**: 한국 기술블로그 실시간 모니터링  
- **키워드 필터링**: DS/ML 관련 키워드 자동 감지
- **중복 제거**: URL 기반 중복 글 자동 제거

### 🧮 스마트 점수화 시스템
```
기본점수(50점) + 우선키워드 보너스 + 소스 가중치 - 제외패턴 페널티
```
- **우선 키워드**: "방법"(+15), "가이드"(+20), "분석"(+15), "LLM"(+20) 등
- **소스 가중치**: 기술블로그(+30), Reddit(+10)  
- **품질 임계값**: 70점 이상만 선별하여 5-10개 제공

### 🌐 AI 번역/요약
- **번역**: googletrans로 영문→한국어 (2000자→1000자 제한)
- **요약**: Gemini Pro로 정확히 3문장 요약
- **대체 처리**: API 실패시 첫 2문장 자동 대체
- **킬스위치**: API 오류율 50% 이상시 자동 차단

### 🎨 모던 웹 인터페이스
- **반응형 디자인**: 모바일/태블릿/데스크톱 최적화
- **다크/라이트 모드**: 시스템 설정 연동 + 수동 토글
- **카드 레이아웃**: 제목(한글) + 3줄 요약 + 태그 + 메타정보
- **실시간 모달**: 부드러운 애니메이션 + 키보드 단축키
- **읽은글 관리**: localStorage 기반 상태 저장

## 🛠 기술 스택

### 🔙 백엔드
- **Python 3.8+**: 메인 언어
- **Flask 3.0**: 웹 프레임워크
- **praw**: Reddit API 클라이언트
- **feedparser**: RSS 파싱
- **beautifulsoup4**: 웹 스크래핑
- **googletrans**: 무료 번역 서비스
- **google-generativeai**: Gemini Pro API

### 🔚 프론트엔드  
- **Tailwind CSS**: 유틸리티 기반 CSS
- **Vanilla JavaScript**: 라이브러리 없는 순수 JS
- **Font Awesome**: 아이콘 시스템
- **HTML5/CSS3**: 시맨틱 마크업

### 🚀 배포/인프라
- **Railway**: 클라우드 배포 플랫폼
- **Gunicorn**: WSGI 서버
- **GitHub**: 소스코드 관리 + CI/CD
- **crontab**: 자동 수집 스케줄링

## 🚀 설치 및 실행

### 📋 필수 요구사항

- **Python 3.8 이상**
- **Git**
- **인터넷 연결** (API 사용)

### 1️⃣ 클론 및 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/DS_news_web.git
cd DS_news_web

# 2. 가상환경 생성 (선택적)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 필요한 디렉토리 생성
mkdir -p data logs static templates
```

### 2️⃣ 환경 설정

```bash
# 1. 환경변수 파일 생성
cp env.example .env

# 2. .env 파일에 API 키 설정 (아래 가이드 참고)
nano .env  # 또는 원하는 에디터
```

### 3️⃣ 실행

```bash
# 개발 서버 실행
python app.py

# 또는 프로덕션 서버 실행
gunicorn --bind 0.0.0.0:5000 app:app
```

🎉 **실행 완료!** 브라우저에서 `http://localhost:5000` 접속

## 🔑 API 키 설정

### 📋 필수 API 키

| API | 비용 | 용도 | 설정 가이드 |
|-----|------|------|-------------|
| **Reddit API** | 🆓 무료 | 글 수집 | [설정하기](#reddit-api-설정) |
| **Google Gemini** | 💰 유료 | AI 요약 | [설정하기](#google-gemini-api-설정) |

### 🔴 Reddit API 설정

1. **https://www.reddit.com/prefs/apps** 방문
2. **"Create App"** 클릭
3. 설정 입력:
   - **이름**: `DS News Aggregator`
   - **타입**: `script` 선택
   - **설명**: `개인 뉴스 수집용`
   - **redirect URI**: `http://localhost` (사용하지 않음)
4. 생성 후 정보 복사:
   ```bash
   REDDIT_CLIENT_ID=앱이름아래_14자리문자열
   REDDIT_CLIENT_SECRET=secret_뒤의_27자리문자열  
   REDDIT_USER_AGENT=DSNewsAggregator/1.0
   ```

### 🔵 Google Gemini API 설정

1. **https://makersuite.google.com/app/apikey** 방문
2. Google 계정 로그인
3. **"Create API key"** 클릭
4. 프로젝트 선택 또는 새로 생성
5. API 키 복사:
   ```bash
   GEMINI_API_KEY=AIza-로시작하는39자리키
   ```

### 💰 비용 가이드

- **Reddit API**: 완전 무료
- **Gemini Pro**: 월 15$ 이하 (일반 사용량 기준)
- **googletrans**: 무료 (번역용, 제한적)
- **Railway 배포**: 월 5$ (선택적)

## 🌐 웹 인터페이스

### 🏠 메인 화면

![메인 화면](docs/images/main-screen.png)

**구성 요소:**
- **헤더**: 제목 + 통계 + 다크모드 토글 + 수집하기 버튼
- **통계바**: 총 글수, 소스수, 수집일, 정렬/필터 옵션
- **카드 그리드**: 글 목록 (제목, 요약, 태그, 메타정보)

### 🪟 상세 모달

![모달 화면](docs/images/modal-screen.png)

**구성 요소:**
- **헤더**: 제목(한글) + 메타정보
- **내용**: 요약 박스 + 태그 + 번역된 전문
- **원문 토글**: 원문 보기/숨기기
- **푸터**: 읽음표시, 원문사이트 링크

### 🎨 다크 모드

![다크 모드](docs/images/dark-mode.png)

- **자동 감지**: 시스템 다크모드 설정 연동
- **수동 토글**: 헤더의 달/해 아이콘 클릭
- **상태 저장**: localStorage에 사용자 선택 저장

### ⌨️ 키보드 단축키

| 키 | 기능 |
|----|------|
| `ESC` | 모달 닫기 |
| `Ctrl+D` | 다크모드 토글 |
| `Ctrl+R` | 글 수집하기 |
| `1`, `2`, `3` | 정렬 변경 (품질/날짜/소스) |

## 📊 데이터 수집 방식

### 🎯 수집 소스

| 소스 | 타입 | 수집량 | 필터링 |
|------|------|--------|--------|
| **r/MachineLearning** | Reddit | 최대 20개 | upvote 5+ |
| **r/datascience** | Reddit | 최대 20개 | upvote 5+ |
| **네이버 D2** | RSS | 최대 10개 | DS/ML 키워드 |
| **카카오테크** | RSS | 최대 10개 | DS/ML 키워드 |
| **AI타임스** | RSS | 최대 10개 | DS/ML 키워드 |

### 🔍 필터링 알고리즘

```python
점수 = 기본점수(50) 
     + 우선키워드_보너스 
     + 소스가중치 
     - 제외패턴_페널티
     + 추가보너스(업보트, 길이 등)

if 점수 >= 70:
    선별대상.append(글)
```

**우선 키워드 (보너스):**
- `방법` (+15점), `가이드` (+20점)
- `분석` (+15점), `비교` (+15점)  
- `구현` (+20점), `LLM` (+20점)
- `시계열` (+15점)

**제외 패턴 (페널티):**
- `추천해주세요` (-30점)
- `어떻게 생각` (-30점)
- 과도한 감탄사 (-30점)

### 📁 데이터 형식

```json
{
  "date": "2024-12-30",
  "articles": [
    {
      "id": "article_1",
      "title": "원제목",
      "title_ko": "번역된 제목", 
      "content": "원문 내용",
      "content_ko": "번역된 내용",
      "summary": "3문장 요약",
      "url": "원문 링크",
      "source": "reddit|naver_d2|kakao_tech|ai_times",
      "tags": ["LLM", "시계열"],
      "score": 85,
      "published": "2024-12-30T08:00:00Z"
    }
  ]
}
```

## 🚢 배포 방법

### 🚂 Railway 배포 (추천)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

#### 1️⃣ GitHub 연동

```bash
# 1. GitHub에 푸시
git add .
git commit -m "DS News Aggregator 배포 준비"
git push origin main

# 2. Railway에서 GitHub 연결
# https://railway.app → New Project → Deploy from GitHub
```

#### 2️⃣ 환경변수 설정

Railway 대시보드에서 다음 환경변수 설정:

```bash
# 필수 환경변수
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=DSNewsAggregator/1.0
GEMINI_API_KEY=your-gemini-api-key
SECRET_KEY=your-production-secret-key

# 선택적 환경변수
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

#### 3️⃣ 도메인 설정

1. **Railway 대시보드** → **Settings** → **Domains**
2. **Generate Domain** 클릭 (무료 서브도메인)
3. 또는 **Custom Domain** 추가 (유료)
4. **HTTPS 자동 활성화** ✅

### 🐳 Docker 배포 (선택적)

```dockerfile
# Dockerfile (예시)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Docker 빌드 및 실행
docker build -t ds-news-aggregator .
docker run -p 5000:5000 --env-file .env ds-news-aggregator
```

### 📊 모니터링 설정

Railway에서 자동으로 제공:
- **로그 모니터링**: 실시간 로그 스트림
- **메트릭스**: CPU, 메모리, 네트워크 사용량
- **헬스체크**: `/` 엔드포인트 자동 체크
- **알림**: 배포 성공/실패 알림

## ⏰ 자동화 설정

### 🕐 크론잡 설정 (macOS/Linux)

#### 자동 설치

```bash
# 크론잡 자동 설치 스크립트 실행
chmod +x scripts/install_cron.sh
./scripts/install_cron.sh
```

#### 수동 설치

```bash
# 1. 스크립트 권한 설정
chmod +x scripts/cron_collect.sh

# 2. 크론탭 편집
crontab -e

# 3. 다음 줄 추가 (매일 오전 8시 실행)
0 8 * * * /full/path/to/DS_news_web/scripts/cron_collect.sh

# 4. 크론탭 확인
crontab -l
```

#### 로그 확인

```bash
# 크론잡 실행 로그
tail -f logs/cron.log

# 수동 테스트 실행
./scripts/cron_collect.sh
```

### ⚙️ GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway-app/railway-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📝 사용법

### 🖥️ 웹 인터페이스 사용법

#### 1️⃣ 첫 실행

1. **웹 브라우저**에서 `http://localhost:5000` 접속
2. **"수집하기" 버튼** 클릭하여 최신 글 수집
3. **로딩 완료** 후 카드 목록 확인

#### 2️⃣ 글 읽기

1. **카드 클릭** → 상세 모달 열림
2. **번역된 전문** 읽기
3. **"원문 보기"** 토글로 원문 확인
4. **"원문 사이트"** 버튼으로 원본 페이지 이동

#### 3️⃣ 개인화 설정

- **다크 모드**: 헤더의 달/해 아이콘 클릭
- **정렬**: 품질순/최신순/소스순 선택
- **필터**: 전체/Reddit/한국블로그/읽지않은글
- **읽은글 관리**: 자동으로 localStorage에 저장

### 🔧 명령줄 사용법

```bash
# 전체 파이프라인 실행 (수집→번역→요약→저장)
python main.py

# 개별 모듈 테스트
python test_collectors.py  # 수집기 테스트
python test_pipeline.py    # 전체 시스템 테스트

# 웹서버 실행
python app.py              # 개발 모드
gunicorn app:app           # 프로덕션 모드
```

### 📊 데이터 확인

```bash
# 수집된 데이터 확인
cat data/articles.json | jq '.articles | length'  # 글 개수
cat data/articles.json | jq '.date'               # 수집 날짜

# 로그 확인
tail -f logs/app.log       # 앱 로그
tail -f logs/cron.log      # 크론잡 로그
```

## 🔧 개발자 가이드

### 📁 프로젝트 구조

```
DS_news_web/
├── app.py                    # Flask 메인 앱
├── config.py                # 설정 파일
├── main.py                  # 파이프라인 실행기
├── requirements.txt         # Python 패키지 목록
├── railway.toml            # Railway 배포 설정
├── env.example             # 환경변수 예시
├── collectors/             # 데이터 수집 모듈
│   ├── reddit_collector.py
│   ├── korean_blog_collector.py
│   └── content_filter.py
├── processors/             # 데이터 처리 모듈  
│   ├── translator.py
│   ├── summarizer.py
│   └── pipeline.py
├── templates/              # HTML 템플릿
│   └── dashboard.html
├── static/                 # 정적 파일 (CSS, JS)
│   ├── style.css
│   ├── app.js
│   └── favicon.ico
├── scripts/                # 유틸리티 스크립트
│   ├── cron_collect.sh     # 크론잡용 수집 스크립트
│   └── install_cron.sh     # 크론잡 자동 설치
├── data/                   # 데이터 저장소
│   ├── articles.json       # 최신 글 데이터
│   └── articles_YYYY-MM-DD.json  # 날짜별 히스토리
└── logs/                   # 로그 파일
    ├── app.log            # 앱 로그
    └── cron.log           # 크론잡 로그
```

### 🧪 테스트

```bash
# 개별 수집기 테스트
python test_collectors.py

# 전체 파이프라인 테스트  
python test_pipeline.py

# API 연결 테스트
python -c "from processors.summarizer import Summarizer; s=Summarizer(); print(s.test_connection())"
```

### 🔌 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 메인 대시보드 |
| `/api/articles` | GET | 글 목록 API |
| `/api/article/<id>` | GET | 개별 글 상세 |
| `/api/collect` | POST | 수동 수집 트리거 |
| `/api/status` | GET | 시스템 상태 체크 |
| `/api/mark-read` | POST | 읽은 글 표시 |

### 🎨 커스터마이징

#### 새로운 수집 소스 추가

```python
# collectors/new_source_collector.py
class NewSourceCollector:
    def collect_articles(self):
        # 수집 로직 구현
        pass
```

#### 필터링 규칙 수정

```python
# config.py
PRIORITY_KEYWORDS = {
    'your_keyword': 25,  # 새로운 키워드 추가
    '기존키워드': 15
}
```

#### UI 테마 수정

```css
/* static/style.css */
:root {
    --primary-color: #your-color;  /* 메인 색상 변경 */
}
```

## 🤝 기여하기

DS News Aggregator는 오픈소스 프로젝트입니다! 기여를 환영합니다.

### 📋 기여 방법

1. **Fork** 및 **Clone**
   ```bash
   git clone https://github.com/your-username/DS_news_web.git
   cd DS_news_web
   ```

2. **Feature 브랜치 생성**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **변경사항 커밋**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. **Pull Request 생성**

### 🐛 버그 리포트

GitHub Issues를 통해 버그를 신고해주세요:
- **버그 설명**
- **재현 단계**  
- **예상 동작**
- **실제 동작**
- **환경 정보** (OS, Python 버전 등)

### 💡 기능 제안

새로운 기능 아이디어가 있으시면 Issues에 제안해주세요:
- **기능 설명**
- **사용 사례**
- **구현 방법** (선택적)

### 📝 문서 개선

문서 개선도 큰 도움이 됩니다:
- README 오타/내용 수정
- 코드 주석 개선
- 사용법 가이드 추가

## 📜 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.

```
MIT License

Copyright (c) 2024 DS News Aggregator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 연락처

- **GitHub**: [DS_news_web](https://github.com/your-username/DS_news_web)
- **Issues**: [버그신고/기능제안](https://github.com/your-username/DS_news_web/issues)
- **Discussions**: [질문/토론](https://github.com/your-username/DS_news_web/discussions)

---

<div align="center">

**🎉 DS News Aggregator와 함께 최신 DS/ML 트렌드를 놓치지 마세요!**

[![Star this repo](https://img.shields.io/github/stars/your-username/DS_news_web?style=social)](https://github.com/your-username/DS_news_web)
[![Fork this repo](https://img.shields.io/github/forks/your-username/DS_news_web?style=social)](https://github.com/your-username/DS_news_web/fork)

</div>