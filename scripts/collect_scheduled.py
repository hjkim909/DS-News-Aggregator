#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Scheduled Collection Script
자동화된 글 수집을 위한 스케줄 스크립트
"""

import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import NewsAggregator
from config import get_config

def setup_logging():
    """로깅 설정"""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'scheduled.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """메인 실행 함수"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"===== 스케줄된 수집 시작: {datetime.now()} =====")
    
    try:
        # 작업 디렉토리 변경
        os.chdir(project_root)
        
        # 설정 로드
        config = get_config()
        
        # 뉴스 수집기 초기화 및 실행
        aggregator = NewsAggregator(config)
        stats = aggregator.run_full_collection()
        
        # 결과 로깅
        logger.info("===== 수집 완료 =====")
        logger.info(f"수집된 글: {stats['total_collected']}개")
        logger.info(f"필터링된 글: {stats['filtered_articles']}개")
        logger.info(f"번역된 글: {stats['translated_articles']}개")
        logger.info(f"요약된 글: {stats['summarized_articles']}개")
        
        if stats.get('duration_str'):
            logger.info(f"소요 시간: {stats['duration_str']}")
        
        if stats['errors']:
            logger.warning(f"오류 {len(stats['errors'])}개 발생:")
            for error in stats['errors']:
                logger.warning(f"  - {error}")
        
        # 성공 상태 코드
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"스케줄된 수집 실패: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
