# 🌐 외부 접속 가이드

DS News Aggregator를 외부(다른 기기, 인터넷)에서 접속하는 방법입니다.

---

## 📋 목차

1. [로컬 네트워크 접속 (같은 WiFi)](#로컬-네트워크-접속)
2. [인터넷 접속 (외부 네트워크)](#인터넷-접속)
3. [Railway 클라우드 배포](#railway-클라우드-배포)
4. [ngrok 터널링](#ngrok-터널링)
5. [트러블슈팅](#트러블슈팅)

---

## 1️⃣ 로컬 네트워크 접속 (같은 WiFi) 

### 가장 간단한 방법! 추천 ⭐️

같은 WiFi에 연결된 다른 기기(핸드폰, 태블릿, 다른 컴퓨터)에서 접속하는 방법입니다.

### Step 1: 서버 실행 확인

```bash
# DS News Aggregator 서버가 이미 실행 중이어야 합니다
./START_SERVER.sh
```

서버가 시작되면 다음과 같은 로그가 표시됩니다:

```
🚀 DS News Aggregator 서버 시작
   - 디버그 모드: True
   - 포트: 8080
   - 로컬 접속: http://localhost:8080
   - 외부 접속: http://<YOUR_IP>:8080
   - 데이터 파일: data/articles.json
   - 사용 가능한 외부 IP: 192.168.0.31  ← 이 IP 확인!
```

### Step 2: 내 컴퓨터의 IP 주소 확인

#### macOS/Linux:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

출력 예시:
```
inet 192.168.0.31 netmask 0xffffff00 broadcast 192.168.0.255
```

➡️ **IP 주소: 192.168.0.31**

#### Windows:
```cmd
ipconfig
```

출력에서 "IPv4 주소" 확인:
```
IPv4 주소. . . . . . . . : 192.168.0.31
```

### Step 3: 다른 기기에서 접속

**접속 주소:** `http://[내_IP주소]:8080`

예시:
- http://192.168.0.31:8080
- http://192.168.1.100:8080

### Step 4: 방화벽 확인 (접속 안 될 경우)

#### macOS:
```bash
# 방화벽 상태 확인
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 방화벽에서 Python 허용
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python
```

#### Windows:
1. **제어판** → **Windows Defender 방화벽**
2. **고급 설정** → **인바운드 규칙** → **새 규칙**
3. **포트** 선택 → **TCP 8080** 추가

---

## 2️⃣ 인터넷 접속 (외부 네트워크)

외부 인터넷에서 접속하려면 공인 IP와 포트포워딩이 필요합니다.

### ⚠️ 주의사항
- 보안 위험이 있으므로 **프로덕션 배포(Railway 등)** 권장
- 개발/테스트 목적으로만 사용

### Step 1: 공인 IP 확인

```bash
curl ifconfig.me
```

출력 예시: `203.123.45.67` (이것이 당신의 공인 IP)

### Step 2: 포트포워딩 설정

#### 공유기 관리자 페이지 접속
- **일반적인 주소**: http://192.168.0.1 또는 http://192.168.1.1
- **로그인**: 공유기 설명서 참고 (보통 admin/admin)

#### 포트포워딩 규칙 추가
```
외부 포트: 8080
내부 IP: 192.168.0.31 (내 컴퓨터 IP)
내부 포트: 8080
프로토콜: TCP
```

### Step 3: 외부에서 접속

**접속 주소:** `http://[공인IP]:8080`

예시: http://203.123.45.67:8080

### ⚠️ 보안 강화 (필수!)

```bash
# .env 파일에 비밀번호 추가
ADMIN_PASSWORD=your-strong-password-here
```

```python
# app.py에 기본 인증 추가
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == os.getenv('ADMIN_PASSWORD'):
        return username
    return None

@app.route('/')
@auth.login_required
def index():
    # ... 기존 코드
```

---

## 3️⃣ Railway 클라우드 배포 ⭐️ **가장 추천!**

### 장점
- ✅ 무료 플랜 제공 (500시간/월)
- ✅ HTTPS 자동 적용 (보안)
- ✅ 공인 도메인 제공
- ✅ 24/7 가동
- ✅ 설정 간단

### 배포 방법

자세한 내용은 **`DEPLOYMENT.md`** 파일을 참고하세요!

#### 간단 요약:

```bash
# 1. Railway 계정 생성
https://railway.app

# 2. GitHub에 코드 푸시
git add .
git commit -m "Deploy to Railway"
git push origin main

# 3. Railway에서 GitHub 저장소 연결
New Project → Deploy from GitHub → DS_news_web 선택

# 4. 환경변수 설정
Railway Dashboard → Variables
- GEMINI_API_KEY=your-key
- SECRET_KEY=random-string

# 5. 자동 배포 완료!
```

**접속 주소:** `https://your-app-name.up.railway.app`

---

## 4️⃣ ngrok 터널링 (임시 접속용)

개발 중 빠르게 외부에서 테스트하고 싶을 때 사용합니다.

### Step 1: ngrok 설치

```bash
# macOS
brew install ngrok

# 또는 다운로드
https://ngrok.com/download
```

### Step 2: ngrok 실행

```bash
# 터미널 1: Flask 서버 실행
./START_SERVER.sh

# 터미널 2: ngrok 실행
ngrok http 8080
```

### Step 3: 접속

ngrok이 제공하는 URL로 접속:

```
Forwarding  https://abc123.ngrok.io -> http://localhost:8080
```

**접속 주소:** https://abc123.ngrok.io

### ⚠️ 주의사항
- 무료 플랜: 2시간 세션 제한
- ngrok 종료시 URL 변경됨
- 임시 테스트 용도로만 사용

---

## 5️⃣ 트러블슈팅

### 문제 1: "연결할 수 없음" 오류

**해결 방법:**

1. **서버가 실행 중인지 확인**
   ```bash
   lsof -i :8080
   ```

2. **방화벽 확인**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # 방화벽 끄기 (테스트용)
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```

3. **IP 주소 확인**
   ```bash
   ifconfig | grep "inet "
   ```

### 문제 2: "ERR_CONNECTION_REFUSED"

**원인:** 서버가 외부 접속을 허용하지 않음

**해결:**
```python
# app.py 확인 (이미 설정되어 있음)
app.run(host='0.0.0.0', port=8080)  # 0.0.0.0 = 모든 IP 허용
```

### 문제 3: "Timeout" 오류

**원인:** 공유기 포트포워딩 문제

**해결:**
1. 공유기 설정 다시 확인
2. UPnP 활성화 (공유기 설정)
3. DMZ 호스트 설정 (비추천, 보안 위험)

### 문제 4: 핸드폰에서 접속 안됨

**체크리스트:**
- [ ] 핸드폰이 같은 WiFi에 연결되어 있나요?
- [ ] IP 주소를 정확히 입력했나요?
- [ ] 서버가 실행 중인가요?
- [ ] 방화벽이 꺼져있나요?

---

## 📊 접속 방법 비교표

| 방법 | 난이도 | 비용 | 보안 | 추천도 | 용도 |
|------|--------|------|------|--------|------|
| **로컬 네트워크** | ⭐ 쉬움 | 무료 | ⭐⭐⭐ 안전 | ⭐⭐⭐⭐⭐ | 가정/사무실 내부 |
| **포트포워딩** | ⭐⭐⭐ 어려움 | 무료 | ⭐ 위험 | ⭐⭐ | 비추천 |
| **Railway** | ⭐⭐ 보통 | 무료/유료 | ⭐⭐⭐⭐⭐ 안전 | ⭐⭐⭐⭐⭐ | **프로덕션** |
| **ngrok** | ⭐ 쉬움 | 무료/유료 | ⭐⭐⭐ 보통 | ⭐⭐⭐ | 임시 테스트 |

---

## 🎯 추천 시나리오

### 시나리오 1: 집에서 핸드폰으로 확인하고 싶어요
➡️ **로컬 네트워크 접속** (1단계)

### 시나리오 2: 친구에게 보여주고 싶어요 (다른 네트워크)
➡️ **ngrok 터널링** (4단계)

### 시나리오 3: 어디서나 접속하고 싶어요 (프로덕션)
➡️ **Railway 배포** (3단계) ⭐️ **가장 추천!**

### 시나리오 4: 회사에서 접속하고 싶어요
➡️ **VPN** + **로컬 네트워크 접속**

---

## 🔒 보안 권장사항

1. **절대 하지 마세요:**
   - ❌ 비밀번호 없이 공개 인터넷 노출
   - ❌ 개발 서버를 프로덕션으로 사용
   - ❌ API 키를 코드에 하드코딩

2. **꼭 하세요:**
   - ✅ Railway 같은 클라우드 플랫폼 사용
   - ✅ HTTPS 적용
   - ✅ 환경변수로 민감 정보 관리
   - ✅ 기본 인증 또는 OAuth 추가

---

## 📞 도움이 필요하신가요?

- **로컬 네트워크 문제**: 공유기 IP 대역 확인 (192.168.x.x 또는 10.0.x.x)
- **Railway 배포 문제**: `DEPLOYMENT.md` 참고
- **방화벽 문제**: 시스템 설정 → 보안 및 개인정보보호

---

**🎉 외부 접속 설정 완료! 어디서나 DS News를 확인하세요!**

