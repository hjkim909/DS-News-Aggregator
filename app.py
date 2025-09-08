#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Main Flask Application
데이터 사이언티스트용 개인 뉴스 큐레이션 웹앱 (사용자 요구사항 반영)
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv
import logging

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 데이터 파일 경로
DATA_FILE = 'data/articles.json'

def load_today_articles():
    """
    오늘 날짜 글 목록 로드 (사용자 요구사항: 새로운 JSON 형식)
    형식: {"date": "2024-12-30", "articles": [...]}
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 새로운 형식인지 확인
            if isinstance(data, dict) and 'articles' in data:
                articles = data['articles']
                date_str = data.get('date', 'Unknown')
                logger.info(f"오늘 글 로드: {len(articles)}개 ({date_str})")
                return articles, date_str
            # 기존 형식 호환
            elif isinstance(data, list):
                logger.info(f"기존 형식 글 로드: {len(data)}개")
                return data, datetime.now().date().isoformat()
            else:
                logger.warning("알 수 없는 데이터 형식")
                return [], datetime.now().date().isoformat()
        else:
            logger.info("데이터 파일이 없습니다.")
            return [], datetime.now().date().isoformat()
            
    except Exception as e:
        logger.error(f"글 데이터 로드 실패: {e}")
        return [], datetime.now().date().isoformat()

def find_article_by_id(article_id: str):
    """
    ID로 개별 글 찾기 (사용자 요구사항: /api/article/<id>)
    
    Args:
        article_id: 글 ID
        
    Returns:
        찾은 글 또는 None
    """
    try:
        articles, _ = load_today_articles()
        
        for article in articles:
            if article.get('id') == article_id:
                return article
        
        logger.warning(f"글을 찾을 수 없음: ID={article_id}")
        return None
        
    except Exception as e:
        logger.error(f"글 검색 실패: {e}")
        return None

# 메인 라우트: 오늘 날짜 글 목록 표시
@app.route('/')
def dashboard():
    """메인 대시보드 페이지 (사용자 요구사항 반영)"""
    try:
        articles, date_str = load_today_articles()
        
        # 통계 정보 계산
        total_articles = len(articles)
        sources = list(set(article.get('source', 'Unknown') for article in articles))
        
        # 태그 통계
        all_tags = []
        for article in articles:
            tags = article.get('tags', [])
            all_tags.extend(tags)
        unique_tags = list(set(all_tags))
        
        stats = {
            'total_articles': total_articles,
            'sources_count': len(sources),
            'sources': sources,
            'tags': unique_tags,
            'date': date_str,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', 
                             articles=articles, 
                             stats=stats)
                             
    except Exception as e:
        logger.error(f"대시보드 로드 실패: {e}")
        return render_template('dashboard.html', 
                             articles=[], 
                             stats={
                                 'total_articles': 0, 
                                 'sources_count': 0, 
                                 'sources': [],
                                 'tags': [],
                                 'date': datetime.now().date().isoformat()
                             },
                             error="대시보드를 로드할 수 없습니다.")

# API 라우트: /api/article/<id> 개별 글 상세 정보  
@app.route('/api/article/<article_id>')
def api_article_detail(article_id):
    """개별 글 상세 정보 API (사용자 요구사항)"""
    try:
        article = find_article_by_id(article_id)
        
        if article:
            return jsonify({
                'success': True,
                'article': article
            })
        else:
            return jsonify({
                'success': False,
                'error': '글을 찾을 수 없습니다.',
                'article_id': article_id
            }), 404
            
    except Exception as e:
        logger.error(f"개별 글 API 실패 (ID: {article_id}): {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'article_id': article_id
        }), 500

@app.route('/api/articles')
def api_articles():
    """전체 글 목록 API"""
    try:
        articles, date_str = load_today_articles()
        
        return jsonify({
            'success': True,
            'articles': articles,
            'total': len(articles),
            'date': date_str
        })
        
    except Exception as e:
        logger.error(f"API 글 목록 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'articles': [],
            'total': 0
        }), 500

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """수동 수집 트리거 API"""
    try:
        # 실제 파이프라인 실행
        from processors.pipeline import run_ds_news_pipeline
        
        logger.info("수동 수집 시작")
        stats = run_ds_news_pipeline()
        
        return jsonify({
            'success': True,
            'message': f'수집 완료: {stats.get("final_articles", 0)}개 글',
            'stats': stats
        })
        
    except ImportError:
        logger.warning("파이프라인 모듈을 찾을 수 없음 (개발 중)")
        return jsonify({
            'success': True,
            'message': '수집이 시작되었습니다 (개발 모드)',
            'status': 'development'
        })
        
    except Exception as e:
        logger.error(f"수집 실행 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """시스템 상태 체크 API"""
    try:
        articles, date_str = load_today_articles()
        
        # 최신 글 시간 찾기
        last_article_time = None
        if articles:
            for article in articles:
                try:
                    article_time = datetime.fromisoformat(article.get('published', article.get('created_at', '')))
                    if not last_article_time or article_time > last_article_time:
                        last_article_time = article_time
                except (ValueError, TypeError):
                    continue
        
        status = {
            'server_status': 'online',
            'total_articles': len(articles),
            'current_date': date_str,
            'last_collection': last_article_time.isoformat() if last_article_time else None,
            'data_file_exists': os.path.exists(DATA_FILE),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"상태 체크 실패: {e}")
        return jsonify({
            'server_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/mark-read', methods=['POST'])
def api_mark_read():
    """글 읽음 상태 기록 API (localStorage와 연동)"""
    try:
        data = request.get_json()
        article_id = data.get('article_id')
        
        if not article_id:
            return jsonify({
                'success': False,
                'error': 'article_id가 필요합니다.'
            }), 400
        
        # 실제로는 클라이언트 localStorage에서 관리하므로
        # 서버에서는 단순히 성공 응답만 반환
        return jsonify({
            'success': True,
            'article_id': article_id,
            'message': '읽음 상태가 기록되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"읽음 상태 기록 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 정적 파일 서빙 (사용자 요구사항)
@app.route('/favicon.ico')
def favicon():
    """파비콘 서빙"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 
        'favicon.ico', 
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/static/<path:filename>')
def serve_static(filename):
    """정적 파일 서빙 (CSS, JS, 이미지)"""
    return send_from_directory('static', filename)

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('dashboard.html', 
                         articles=[], 
                         stats={
                             'total_articles': 0, 
                             'sources_count': 0, 
                             'sources': [],
                             'tags': [],
                             'date': datetime.now().date().isoformat()
                         },
                         error="페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"내부 서버 오류: {error}")
    return render_template('dashboard.html', 
                         articles=[], 
                         stats={
                             'total_articles': 0, 
                             'sources_count': 0, 
                             'sources': [],
                             'tags': [],
                             'date': datetime.now().date().isoformat()
                         },
                         error="내부 서버 오류가 발생했습니다."), 500

# 개발용 라우트
@app.route('/debug')
def debug_info():
    """디버그 정보 (개발용)"""
    if not app.debug:
        return "Debug mode is disabled", 403
    
    try:
        articles, date_str = load_today_articles()
        debug_data = {
            'data_file_exists': os.path.exists(DATA_FILE),
            'articles_count': len(articles),
            'current_date': date_str,
            'sample_article': articles[0] if articles else None,
            'environment': {
                'SECRET_KEY': bool(app.config['SECRET_KEY']),
                'DEBUG': app.debug,
                'DATA_FILE': DATA_FILE
            }
        }
        
        return jsonify(debug_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 개발 서버 실행
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 DS News Aggregator 시작")
    logger.info(f"   - Port: {port}")
    logger.info(f"   - Debug: {debug_mode}")
    logger.info(f"   - Data File: {DATA_FILE}")
    
    # 필요한 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # macOS AirPlay 때문에 5000번 포트 충돌시 5001번 사용
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    if is_port_in_use(port):
        port = 5001
        logger.warning(f"포트 5000이 사용 중입니다. 포트 {port}로 변경합니다.")
        logger.info(f"   - 새로운 접속 URL: http://localhost:{port}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)