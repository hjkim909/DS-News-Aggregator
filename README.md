# 🤖 DS News Aggregator

> **데이터 사이언티스트를 위한 AI/ML 뉴스 중심 자동 큐레이션 시스템**

매주 최신 AI/ML 뉴스를 자동 수집하고, AI로 번역/요약하여 카드 형태로 제공합니다.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 주요 기능

- 📰 **뉴스 중심 수집** (50%): TechCrunch, MIT Tech Review, WIRED, Tech42
- 📚 **실용 블로그** (30%): Towards Data Science, Analytics Vidhya, KDnuggets
- 🏢 **기업 블로그** (20%): OpenAI, Google AI, NAVER D2, Kakao Tech
- 🌐 **AI 번역/요약**: Google Translate + Gemini Pro
- 🔍 **스마트 필터링**: 날짜/정렬/소스별 필터 + 읽은 글 관리
- 🎨 **모던 UI**: 반응형 디자인 + 다크 모드
- ⚡ **자동화**: GitHub Actions (매주 월요일 자동 수집)

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 클론
git clone https://github.com/your-username/DS_news_web.git
cd DS_news_web

# 의존성 설치
pip install -r requirements.txt

# 디렉토리 생성
mkdir -p data logs
```

### 2. 환경 설정

```bash
# .env 파일 생성
cp env.example .env

# API 키 설정 (nano .env)
GEMINI_API_KEY=your-key-here
```

**Google Gemini API 키 발급**: https://makersuite.google.com/app/apikey

### 3. 실행

```bash
# 뉴스 수집 (처음 한 번)
python main.py

# 서버 시작
./START_SERVER.sh

# 접속
http://localhost:8080
```

**🎉 완료! 브라우저에서 확인하세요.**

---

## 📖 문서

### 🔰 시작하기
- **[설치 가이드](docs/GETTING_STARTED.md)** - 상세한 설치 및 설정 방법
- **[사용 가이드](docs/USER_GUIDE.md)** - 모든 기능 사용법

### 🚀 배포하기
- **[배포 가이드](docs/DEPLOYMENT.md)** - Railway 클라우드 배포
- **외부 접속** - 같은 WiFi 또는 인터넷에서 접속

### 🗺️ 계획
- **[로드맵](docs/ROADMAP.md)** - 현재 상황 + 향후 계획

---

## 💡 특징

### 소스 구성 (PRD v2.0)

```
📰 뉴스 미디어 (50%) → 3-5개/주
├─ TechCrunch AI (해외)
├─ MIT Tech Review (해외)
├─ WIRED AI (해외)
└─ Tech42 (국내)

📚 실용 블로그 (30%) → 2-3개/주
├─ Towards Data Science
├─ Analytics Vidhya
├─ KDnuggets
└─ Neptune.ai

🏢 기업 블로그 (20%) → 1-2개/주
├─ OpenAI Blog
├─ Google AI
├─ NAVER D2
└─ Kakao Tech
```

### 점수화 시스템

```python
점수 = 소스별 기본점수 (뉴스 100, 블로그 80, 기업 70)
     + 키워드 보너스 (뉴스속보 +30, 가이드 +20, LLM +10)
     + 신선도 보너스 (24시간 이내 +10)
     - 패널티 (의견기사 -20, 단순질문 -30)
```

**70점 이상**만 선별하여 **5-10개/주** 제공

---

## 🌐 외부 접속

### 같은 WiFi에서

```bash
# 내 IP 확인
ifconfig | grep "inet " | grep -v 127.0.0.1

# 다른 기기에서 접속
http://[내_IP]:8080
# 예: http://192.168.0.31:8080
```

### 인터넷 어디서나

**Railway 배포** (추천):
- 무료 플랜 사용 가능
- HTTPS 자동 적용
- 공인 도메인 제공

자세한 내용은 **[배포 가이드](docs/DEPLOYMENT.md)** 참고

---

## 🛠️ 기술 스택

**Backend**
- Python 3.8+, Flask 3.0
- feedparser (RSS 파싱)
- googletrans (번역)
- google-generativeai (요약)

**Frontend**
- Tailwind CSS
- Vanilla JavaScript
- Font Awesome

**배포**
- Railway (클라우드)
- GitHub Actions (자동화)
- Gunicorn (WSGI)

---

## 📊 통계

```
소스:          12개
주간 수집:      5-10개
번역 성공률:    95%+
자동 수집:      매주 월요일 08:00 KST
총 비용:        ₩0 (완전 무료!)
```

---

## 🗺️ 로드맵

### ✅ Phase 6 완료 (현재)
- 날짜별 필터링
- 정렬/필터 기능
- GitHub Actions 자동화
- Railway 배포 준비

### 🚧 Phase 7 계획 (다음)
- [ ] 중복 방지 시스템 (2-3시간)
- [ ] 추가 뉴스 소스 11개 (3-4시간)
- [ ] 검색 기능 (4-5시간)

자세한 내용은 **[로드맵](docs/ROADMAP.md)** 참고

---

## 🤝 기여하기

기여를 환영합니다!

1. **Fork** 저장소
2. **Feature 브랜치** 생성
3. **구현 및 테스트**
4. **Pull Request** 생성

### 기여 아이디어
- 🐛 버그 수정
- ✨ 새로운 기능
- 📝 문서 개선
- 🌐 새로운 뉴스 소스

---

## 📜 라이선스

MIT License - 자유롭게 사용하세요.

---

## 📞 연락처

- **GitHub**: https://github.com/your-username/DS_news_web
- **Issues**: 버그 신고 및 기능 제안
- **Discussions**: 질문 및 토론

---

<div align="center">

**🎉 DS News Aggregator와 함께 최신 AI/ML 트렌드를 놓치지 마세요!**

Made with ❤️ for Data Scientists

</div>
