#!/bin/bash

# DS News Aggregator - 크론잡용 자동 수집 스크립트
# 매일 오전 8시 실행: 0 8 * * * /path/to/ds-news-aggregator/scripts/cron_collect.sh

# 설정
PROJECT_DIR="/Users/$(whoami)/DS_news_web"  # 실제 경로로 변경
LOG_FILE="${PROJECT_DIR}/logs/cron.log"
PID_FILE="${PROJECT_DIR}/scripts/collect.pid"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 시작 로그
log "========== 크론잡 수집 시작 =========="

# 중복 실행 방지
if [ -f "$PID_FILE" ]; then
    LAST_PID=$(cat "$PID_FILE")
    if kill -0 "$LAST_PID" 2>/dev/null; then
        log "이미 수집 프로세스가 실행 중입니다 (PID: $LAST_PID)"
        exit 1
    else
        log "기존 PID 파일 정리 (프로세스 종료됨)"
        rm -f "$PID_FILE"
    fi
fi

# 현재 PID 저장
echo $$ > "$PID_FILE"

# 프로젝트 디렉토리로 이동
cd "$PROJECT_DIR" || {
    log "ERROR: 프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR"
    rm -f "$PID_FILE"
    exit 1
}

# Python 가상환경 활성화 (conda/venv 사용시)
# source /opt/anaconda3/bin/activate  # conda 사용시
# source venv/bin/activate  # venv 사용시

# .env 파일 확인
if [ ! -f ".env" ]; then
    log "ERROR: .env 파일이 없습니다. API 키를 설정하세요."
    rm -f "$PID_FILE"
    exit 1
fi

# 수집 실행
log "글 수집 시작..."
python3 main.py >> "$LOG_FILE" 2>&1

# 실행 결과 확인
if [ $? -eq 0 ]; then
    log "✅ 글 수집 성공적으로 완료"
    
    # 수집된 글 수 확인
    if [ -f "data/articles.json" ]; then
        ARTICLE_COUNT=$(python3 -c "import json; data=json.load(open('data/articles.json')); print(len(data.get('articles', [])))" 2>/dev/null || echo "N/A")
        log "📊 수집된 글 수: $ARTICLE_COUNT개"
    fi
else
    log "❌ 글 수집 실패 (종료 코드: $?)"
fi

# PID 파일 정리
rm -f "$PID_FILE"

log "========== 크론잡 수집 완료 =========="
log ""
