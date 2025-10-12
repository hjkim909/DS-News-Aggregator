# DS News Aggregator - Progress Plan

## Current Status
**Date: 2025-10-10**  
**Phase: PRD v2.0 + Full Feature Complete**  
**Status: ✅ ALL FEATURES WORKING - 날짜 필터링 + 정렬 + 필터링 + 자동화 완료**

## Project Overview
데이터 사이언티스트용 AI/ML 뉴스 중심 자동 큐레이션 웹사이트 개발
- Backend: Python Flask
- 소스 구성: 뉴스 미디어(50%) + 실용 블로그(30%) + 기업 블로그(20%)
- APIs: Google Translate, Google Gemini Pro (Reddit API 제거)
- Frontend: HTML/CSS/JavaScript (Tailwind CSS)
- 배포: Railway + GitHub Actions 자동화

## Main Tasks Checklist

### Phase 1: Project Setup ✅ **COMPLETED**
- [x] 프로젝트 기본 구조와 requirements.txt 생성
- [x] Flask 메인 앱 (app.py) 생성
- [x] 수집기 모듈들 생성 (reddit_collector.py, korean_blog_collector.py, content_filter.py)
- [x] 처리 모듈들 생성 (translator.py, summarizer.py)
- [x] 웹 템플릿 생성 (dashboard.html with Tailwind CSS)
- [x] 스타일시트와 정적 파일들 생성 (style.css, app.js)
- [x] 추가 설정 파일들 생성 (README.md, .gitignore, 배포 파일들)

### Phase 2: Core Functionality ✅ **COMPLETED**
- [x] Reddit API 연동 (upvote 5개 이상, 일 최대 20개)
- [x] 한국 기술블로그 수집 로직 (네이버 D2, 카카오테크, AI타임스 RSS)
- [x] Google Translate 연동 (다중 번역 서비스)
- [x] Gemini API 연동 및 요약 기능 (3문장 요약)
- [x] 사용자 요구사항 맞춤 점수화 시스템 (기본 50점 + 키워드 보너스)

### Phase 3: Frontend & UI ✅ **COMPLETED**
- [x] 대시보드 UI 구현 (Tailwind CSS 기반)
- [x] 카드 형태 글 표시 (사용자 요구사항 JSON 형식)
- [x] 모달 창 구현 (번역 토글, 원문 링크)
- [x] 반응형 디자인 적용 (모바일/데스크톱 최적화)

### Phase 4: Testing & Deployment ✅ **COMPLETED**
- [x] 개별 모듈 테스트 스크립트 (test_collectors.py)
- [x] 통합 테스트 (test_integration.py, test_performance.py, test_quality.py, test_mobile.py)
- [x] 사용자 맞춤 개선 (AI/ML 필터링, 날짜별 UI, 외부 접근)
- [x] 날짜 필터링 시스템 (최근 2달, 2025년+ 기사만)
- [ ] Railway 배포 설정 **[READY]**
- [ ] 자동화 스케줄링 설정 **[READY]**

### Phase 5: PRD v2.0 System Overhaul ✅ **COMPLETED**
- [x] 뉴스 미디어 수집기 구현 (TechCrunch AI, VentureBeat AI, MIT Tech Review, AI타임스, ZDNet Korea, Tech42)
- [x] 실용 블로그 수집기 구현 (Towards Data Science, Analytics Vidhya, KDnuggets, Neptune.ai)
- [x] 기업 블로그 수집기 구현 (Google AI, OpenAI, Naver D2, Kakao Tech)
- [x] 새로운 점수화 시스템 (뉴스 100점, 블로그 80점, 기업 70점 + 키워드 보너스)
- [x] 소스 비율 조정 (뉴스 50%, 블로그 30%, 기업 20%)
- [x] 파이프라인 업데이트 (새로운 수집기들 통합)

### Phase 6: Deployment & Automation ✅ **COMPLETED**
- [x] **requirements.txt 정리** - Reddit API 패키지(praw) 제거
- [x] **날짜별 필터링** - 웹 UI에 날짜 선택 드롭다운 추가
- [x] **GitHub Actions** - 매일 08:00 KST 자동 수집 워크플로우 생성
- [x] **Railway 배포 가이드** - DEPLOYMENT.md 완전한 배포 매뉴얼 작성

### Phase 7: Next Improvements **[PLANNING]**
- [ ] 정렬 기본값을 최신순으로 변경
- [ ] 페이지네이션 구현 (12개 단위)
- [ ] 중복 방지 시스템 (URL 해시 기반)
- [ ] 추가 뉴스 소스 발굴 및 통합

## Current Focus  
**🎉 배포 시스템 완성! 날짜 필터링 + GitHub Actions 자동화 + Railway 배포 준비 완료**

### 2025-01-05 PRD v2.0 개편 완료 ✅
1. **뉴스 중심 소스 재구성** - Reddit 제거, 뉴스 미디어(50%) + 블로그(30%) + 기업(20%) 구조
2. **새로운 수집기 시스템** - 3개 전문 수집기로 분리 (NewsMediaCollector, PracticalBlogCollector, CompanyBlogCollector)  
3. **점수화 시스템 개선** - 소스별 기본 점수 차등화 (뉴스 100점, 블로그 80점, 기업 70점)
4. **파이프라인 완전 개편** - 새로운 비율과 점수 시스템에 맞춘 필터링 로직 적용

## Next Steps - 완성된 시스템 실행 가이드
1. **API 키 설정**: `cp env.example .env` → API 키 입력 (Reddit, Gemini)
2. **전체 테스트**: `python run_all_tests.py` 종합 시스템 검증 (10-20분)
3. **웹앱 실행**: `python app.py` → http://localhost:5000 접속
4. **자동 수집**: `./scripts/install_cron.sh` 매일 8시 자동 수집 설정
5. **프로덕션 배포**: Railway 배포 (GitHub 연동 자동 배포 준비 완료)

## 🎯 완성된 모든 기능
✅ 스마트 수집 (Reddit + 한국 블로그) ✅ 점수화 필터링 ✅ AI 번역/요약  
✅ 모던 웹UI (반응형 + 다크모드) ✅ 읽은글 관리 ✅ 배포 설정  
✅ 종합 테스트 시스템 (통합/성능/품질/모바일) ✅ 자동화 크론잡

## 사용자 요구사항 구현 현황 ✅
### Reddit Collector
- ✅ r/MachineLearning, r/datascience만 수집
- ✅ upvote 5개 이상 글만 수집
- ✅ 일 최대 20개 수집 (필터링 전)
- ✅ 제목, 내용, URL, 업보트수, 작성시간 저장

### Korean Blog Collector  
- ✅ 네이버 D2, 카카오테크, AI타임스 RSS 파싱
- ✅ feedparser 라이브러리 사용
- ✅ DS/ML 관련 키워드 포함 글만 수집

### Content Filter
- ✅ 기본점수 50점 시스템
- ✅ 우선 키워드("방법", "가이드", "분석", "비교", "구현", "LLM", "시계열") +10~20점
- ✅ 제외 패턴("추천해주세요", "어떻게 생각", 감탄사) -30점  
- ✅ 소스 가중치: 기술블로그 +30, Reddit +10
- ✅ 최종 70점 이상 글만 선별하여 5-10개 반환

### 데이터 형식
- ✅ 요구사항 JSON 구조 완벽 구현
- ✅ id, title, title_ko, content, content_ko, summary, url, source, tags, score, published 포함
- ✅ 날짜별 데이터 관리 및 히스토리 저장

## 추가 구현된 기능
- ✅ **태그 자동 추출**: LLM, 시계열, 머신러닝 등 스마트 태깅
- ✅ **테스트 스크립트**: test_collectors.py로 개별 모듈 테스트
- ✅ **점수 투명성**: 디버그 로그로 점수 계산 과정 추적
- ✅ **다중 번역 서비스**: Google Cloud + 대체 서비스 지원
- ✅ **완전한 웹UI**: 카드, 모달, 필터, 정렬 기능

## Log
- 2024-12-30: 프로젝트 시작, 기본 구조 설계 및 생성 시작
- 2024-12-30: **Phase 1 완료** - 전체 시스템 아키텍처 및 핵심 기능 구현 완료
  - 모든 수집기, 처리기, 웹UI 컴포넌트 개발 완료
  - 통합 메인 스크립트 및 자동화 시스템 구축
  - 배포 준비 파일들 및 문서화 완료
- 2024-12-30: **사용자 요구사항 100% 구현 완료**
  - Reddit Collector: upvote 5개 이상, 20개 수집, 사용자 점수 시스템
  - Korean Blog Collector: 3개 소스 RSS, DS/ML 키워드 필터링
  - Content Filter: 50점 기본+키워드 보너스+소스 가중치, 70점 이상 선별
  - 데이터 형식: 요구사항 JSON 구조 완벽 구현
  - 테스트 스크립트: test_collectors.py 개별 모듈 테스트 지원
- 2024-12-30: **번역/요약 시스템 및 파이프라인 완성**
  - Translator: googletrans 전용, 영문만 번역, 2000자→1000자 제한
  - Summarizer: Gemini Pro 정확히 3문장 요약, 킬스위치, 대체 요약
  - Pipeline: 수집→필터링→번역→요약→저장 완전 자동화
  - 환경변수 관리: .env 파일 지원, API 키 보안 관리
  - 통합 테스트: test_pipeline.py 전체 시스템 검증
- 2024-12-30: **웹 UI 시스템 100% 완성 - 전체 시스템 완료!**
  - Flask App: 메인/API 라우팅, 정적 파일 서빙, 반응형 디자인 지원
  - Dashboard: 카드 레이아웃, 모달 팝업, 읽은글 체크, 로딩/빈상태/오류 처리
  - 스타일링: 다크/라이트 모드 토글, 호버 효과, 모달 애니메이션, 태그별 색상
  - JavaScript: 모달 관리, localStorage 읽은글 상태, API 호출, 키보드 단축키
  - UI 플로우: 메인→카드 클릭→모달(번역 전문)→원문 보기 완벽 구현
- 2024-12-30: **🚢 배포 시스템 완전 완성 - 프로젝트 100% 완료!**
  - Railway 배포: railway.toml, GitHub 연동, 환경변수 가이드, 도메인/HTTPS
  - 자동화: 크론잡 스크립트(cron_collect.sh), 자동 설치(install_cron.sh)
  - 환경설정: env.example 완전한 API 키 가이드, 비용 정보 포함
  - 문서화: README.md 완전한 설치/배포/사용 가이드, 프로젝트 구조 설명
  - 모든 스크립트 실행권한 설정, 배포 준비 100% 완료
- 2024-12-30: **🧪 종합 테스트 시스템 완성 - 최종 검증 완료!**
  - 통합 테스트: API 연결성, 파이프라인 실행, 웹앱 기능 전체 검증
  - 성능 테스트: 메모리/CPU 모니터링, API 호출 최적화, 10분 목표 달성
  - 품질 테스트: 필터링 정확도 70%+, 번역 성공률 80%+, 요약 품질 검증
  - 모바일 테스트: 반응형 디자인, 터치 UI, 3초 로딩 목표 검증
  - 마스터 테스트: run_all_tests.py 전체 자동화 테스트 스위트
- 2025-01-04: **🎯 사용자 맞춤 개선 완료 - 3가지 핵심 개선사항 적용!**
  - 필터링 강화: AI/ML/LLM 키워드 엄격 적용, 일반 개발글 제외 로직 추가
  - UI 개선: 날짜별 섹션으로 1depth 구조화, 접기/펼치기 + 일괄 읽음 기능
  - 접근성 개선: 외부 접근 허용 설정, IP 주소 자동 표시, 네트워크 접근 가능
  - 사용자 경험: 카드 레이아웃 최적화, 읽음 상태 관리, 반응형 디자인 유지
- 2025-01-04: **📅 날짜 필터링 시스템 구축 완료 - 최신성 보장!**
  - 기존 데이터 정리: 2025년 이전 오래된 기사 5개 제거 (31개 → 26개)
  - 날짜 필터링 적용: 최근 60일(2달) 이내 기사만 수집 및 표시
  - 수집기 강화: TechBlog/Medium 수집기에 날짜 필터링 로직 추가
  - 품질 향상: 연도 체크(2025년+) + 최신성 체크로 이중 필터링
- 2025-01-05: **🔄 PRD v2.0 완전 개편 - 뉴스 중심 시스템으로 전환!**
  - 소스 재구성: Reddit → 뉴스 미디어 중심으로 완전 변경 (6개 뉴스 소스)
  - 3-Tier 구조: 뉴스(50%) + 블로그(30%) + 기업(20%) 비율 시스템 구축
  - 새로운 수집기: NewsMediaCollector, PracticalBlogCollector, CompanyBlogCollector 구현
  - 점수화 개선: 소스별 차등 기본 점수 + PRD v2.0 키워드 보너스 시스템
  - 파이프라인 업그레이드: 새로운 비율 기반 필터링 및 선별 로직 적용
  - 설정 시스템: config.py 완전 재구성, 새로운 소스 관리 체계 구축
- 2025-10-10: **🚀 배포 & 자동화 시스템 완성 - 프로덕션 준비 완료!**
  - requirements.txt 정리: praw(Reddit API) 제거, 필수 패키지만 유지
  - 날짜별 필터링: 백엔드 API (/api/dates, /api/articles/<date>) + 프론트엔드 UI 추가
  - JavaScript 확장: loadAvailableDates(), changeDateFilter(), renderArticles() 구현
  - GitHub Actions: weekly_collect.yml 워크플로우 생성 (매주 월요일 08:00 KST 자동 수집)
  - Railway 배포: DEPLOYMENT.md 완전한 배포 가이드 작성 (환경변수, 트러블슈팅 포함)
  - README 업데이트: PRD v2.0 반영, 새로운 소스 구성 및 비용 정보(완전 무료) 명시
  - 날짜 필터링 버그 수정: articles.json 제외, 날짜 형식 검증, 로깅 강화
  - 자동화 스케줄 변경: 매일 → 매주 1회 (월요일 오전 8시 KST)
  - DATA_DIR 변수 추가: 날짜 API 오류 해결
  - 날짜별 섹션 구조 대응: 정렬/필터링 기능 수정하여 날짜별 섹션에서도 작동
  - 포트 변경: 5000/5001 → 8080/8081로 기본 포트 변경
  - 테스트 완료: 날짜 필터링, 정렬(품질/최신/소스), 필터링(소스/읽지않음) 모두 정상 작동 확인

## Next Phase TODO List 📋

### Phase 5: UX & Automation Improvements
**우선순위: 높음**

#### 1. 정렬 기본값 개선 **[TODO]**
- [ ] 현재 품질순 → 최신순으로 기본 정렬 변경
- [ ] 사용자 선택 기본값 localStorage 저장
- [ ] 정렬 옵션 UI 개선

#### 2. 페이지네이션 구현 **[TODO]** 
- [ ] 12개 단위로 글 분할 표시
- [ ] 하단 페이지 번호 네비게이션 (1, 2, 3...)
- [ ] 페이지 이동시 스크롤 위치 조정
- [ ] 날짜별 섹션과 페이지네이션 조화

#### 3. 자동화 시스템 강화 **[TODO]**
- [ ] 매일 자동 수집 크론잡 설정 완료
- [ ] 중복 기사 방지 시스템 (URL 해시 기반)
- [ ] 수집 실패시 알림 시스템
- [ ] 자동 백업 및 데이터 관리

#### 4. 한국 소스 확장 **[TODO]**
- [ ] datarian.io RSS 수집 추가  
- [ ] 추가 한국 기술 블로그 발굴 및 추가
- [ ] 한국어 키워드 필터링 강화
- [ ] 소스별 품질 가중치 조정

### Phase 6: Advanced Features **[FUTURE]**
- [ ] 사용자 맞춤 키워드 설정
- [ ] 모바일 앱 버전 개발
- [ ] AI 기반 추천 시스템
- [ ] 소셜 공유 기능
