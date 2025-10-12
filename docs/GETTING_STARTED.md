# 🚀 시작하기

DS News Aggregator를 설치하고 실행하는 방법입니다.

---

## 📋 목차

1. [필수 요구사항](#필수-요구사항)
2. [설치](#설치)
3. [환경 설정](#환경-설정)
4. [첫 실행](#첫-실행)
5. [문제 해결](#문제-해결)

---

## 필수 요구사항

- **Python 3.8 이상**
- **Git**
- **인터넷 연결** (뉴스 수집 및 API 사용)

---

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/DS_news_web.git
cd DS_news_web
```

### 2. 가상환경 생성 (선택사항)

```bash
python -m venv venv

# 활성화
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 디렉토리 생성

```bash
mkdir -p data logs
```

---

## 환경 설정

### 1. 환경변수 파일 생성

```bash
cp env.example .env
```

### 2. Google Gemini API 키 설정

1. **https://makersuite.google.com/app/apikey** 접속
2. Google 계정 로그인
3. **"Create API key"** 클릭
4. API 키 복사

### 3. .env 파일 편집

```bash
# .env 파일 열기
nano .env
```

다음 내용 입력:

```bash
# Google Gemini API (필수)
GEMINI_API_KEY=AIza...your-actual-key...xyz

# Flask Secret Key (프로덕션용)
SECRET_KEY=your-random-secret-key-here

# Flask 설정 (선택)
FLASK_DEBUG=True
PORT=8080
```

**Secret Key 생성:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 첫 실행

### 1. 뉴스 수집 (처음 한 번)

```bash
python main.py
```

**예상 소요 시간:** 1-2분  
**결과:** `data/articles.json` 파일 생성 (5-10개 뉴스)

### 2. 웹 서버 실행

```bash
# 방법 1: 시작 스크립트 (추천)
./START_SERVER.sh

# 방법 2: 직접 실행
python app.py
```

### 3. 브라우저 접속

**로컬:** http://localhost:8080  
**같은 WiFi:** http://[내_IP]:8080

**내 IP 확인:**
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

---

## 문제 해결

### 오류 1: `ModuleNotFoundError`

```bash
# 해결: 패키지 재설치
pip install -r requirements.txt
```

### 오류 2: `Port 8080 is in use`

```bash
# 해결: 포트 정리
lsof -ti:8080 | xargs kill -9

# 또는 다른 포트 사용
PORT=8081 python app.py
```

### 오류 3: `GEMINI_API_KEY not found`

```bash
# 해결: .env 파일 확인
cat .env

# API 키가 있는지 확인
echo $GEMINI_API_KEY
```

### 오류 4: 뉴스가 0개 수집됨

```bash
# 원인 1: RSS 피드 오류
# 해결: 로그 확인
tail -f logs/app.log

# 원인 2: 키워드 필터링 너무 엄격
# 해결: config.py에서 QUALITY_THRESHOLD 낮추기
QUALITY_THRESHOLD = 60  # 기본값 70
```

### 오류 5: 외부 접속 안됨

**체크리스트:**
- [ ] 같은 WiFi에 연결되어 있나요?
- [ ] 서버가 실행 중인가요? (`lsof -i :8080`)
- [ ] 방화벽이 차단하고 있나요?
- [ ] IP 주소를 정확히 입력했나요?

**해결: 방화벽 확인**
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

---

## 다음 단계

✅ 설치 완료했다면:
- 📖 [사용 가이드](USER_GUIDE.md) - 모든 기능 배우기
- 🚀 [배포 가이드](DEPLOYMENT.md) - Railway에 배포하기
- 🗺️ [로드맵](ROADMAP.md) - 향후 계획 보기

---

## 추가 도움

- **GitHub Issues**: 버그 신고 및 기능 제안
- **문서 오류**: Pull Request 환영합니다

**🎉 설치 완료! 이제 최신 AI/ML 뉴스를 받아보세요!**

