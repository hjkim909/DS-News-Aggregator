#!/bin/bash

# DS News Aggregator - 크론잡 자동 설치 스크립트
# 매일 오전 8시 자동 수집 설정

# 색상 코드
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}DS News Aggregator - 크론잡 설치${NC}"
echo "========================================"

# 현재 프로젝트 경로 확인
CURRENT_DIR=$(pwd)
if [[ ! -f "$CURRENT_DIR/app.py" ]]; then
    echo -e "${RED}ERROR: 프로젝트 루트 디렉토리에서 실행하세요${NC}"
    echo "현재 위치: $CURRENT_DIR"
    exit 1
fi

echo -e "프로젝트 경로: ${YELLOW}$CURRENT_DIR${NC}"

# cron_collect.sh 스크립트 권한 설정
chmod +x scripts/cron_collect.sh
echo "✅ 크론 스크립트 실행 권한 설정 완료"

# 로그 디렉토리 생성
mkdir -p logs
echo "✅ 로그 디렉토리 생성 완료"

# 크론 스크립트에서 경로 업데이트
sed -i.bak "s|PROJECT_DIR=\".*\"|PROJECT_DIR=\"$CURRENT_DIR\"|g" scripts/cron_collect.sh
echo "✅ 크론 스크립트 경로 업데이트 완료"

# 현재 크론잡 백업
crontab -l > cron_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null
echo "✅ 기존 크론잡 백업 완료"

# 새로운 크론잡 설정
CRON_JOB="0 8 * * * $CURRENT_DIR/scripts/cron_collect.sh"

# 크론잡에 추가 (중복 제거)
(crontab -l 2>/dev/null | grep -v "cron_collect.sh"; echo "$CRON_JOB") | crontab -

echo "✅ 크론잡 설치 완료!"
echo ""
echo -e "${GREEN}설치된 크론잡:${NC}"
echo -e "${YELLOW}$CRON_JOB${NC}"
echo ""
echo "📅 실행 시간: 매일 오전 8시"
echo "📝 로그 위치: $CURRENT_DIR/logs/cron.log"
echo ""

# 크론잡 확인
echo -e "${GREEN}현재 설치된 크론잡:${NC}"
crontab -l | grep -E "(cron_collect|DS_news)" || echo "크론잡이 설정되지 않았습니다."
echo ""

# 테스트 실행 옵션
echo -e "${YELLOW}테스트 실행하시겠습니까? (y/n):${NC}"
read -r answer
if [[ $answer =~ ^[Yy]$ ]]; then
    echo "테스트 실행 중..."
    ./scripts/cron_collect.sh
    echo ""
    echo "테스트 실행 완료. 로그를 확인하세요:"
    echo "tail -f logs/cron.log"
fi

echo ""
echo -e "${GREEN}🎉 크론잡 설치가 완료되었습니다!${NC}"
echo ""
echo "📋 관리 명령어:"
echo "  크론잡 확인: crontab -l"
echo "  크론잡 제거: crontab -e (해당 줄 삭제)"
echo "  로그 확인: tail -f logs/cron.log"
echo "  수동 실행: ./scripts/cron_collect.sh"
