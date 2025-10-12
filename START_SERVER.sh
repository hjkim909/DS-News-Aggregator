#!/bin/bash

echo "🔧 DS News Aggregator 서버 시작 스크립트"
echo "========================================"

# 1. 포트 충돌 해결
echo ""
echo "1️⃣ 포트 충돌 확인 및 해결..."
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8081 2>/dev/null | xargs kill -9 2>/dev/null
echo "   ✅ 포트 8080, 8081 정리 완료"

# 2. 서버 시작
echo ""
echo "2️⃣ Flask 서버 시작..."
echo "   📍 http://localhost:8080 에서 접속하세요"
echo ""
echo "========================================"
echo "🎯 날짜 필터링 테스트 방법:"
echo "   1. 웹 브라우저 접속"
echo "   2. 상단 통계바에서 '📅 최신 날짜' 드롭다운 클릭"
echo "   3. 다른 날짜 선택 (2025-10-05 또는 2025-09-08)"
echo "   4. 해당 날짜의 글만 표시되는지 확인"
echo ""
echo "🛑 서버 종료: Ctrl+C"
echo "========================================"
echo ""

python app.py

