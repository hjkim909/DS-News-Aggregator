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
DATA_DIR = 'data'
DATA_FILE = 'data/articles.json'

def load_articles_by_date():
    """
    날짜별 글 목록 로드 (사용자 요구사항: 날짜별 1depth 구조)
    Returns:
        dict: {date: {'articles': [...], 'count': int, 'sources': [...]}, ...}
    """
    articles_by_date = {}
    
    try:
        # 현재 파일 로드
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                
            # 새로운 형식인지 확인
            if isinstance(current_data, dict) and 'articles' in current_data:
                date_str = current_data.get('date', 'Unknown')
                articles = current_data['articles']
                articles_by_date[date_str] = {
                    'articles': articles,
                    'count': len(articles),
                    'sources': list(set(article.get('source', 'Unknown') for article in articles))
                }
        
        # 백업 폴더에서 과거 데이터 로드
        backup_dir = 'data/backup'
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.startswith('articles_') and filename.endswith('.json'):
                    file_path = os.path.join(backup_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                            
                        if isinstance(backup_data, dict) and 'articles' in backup_data:
                            date_str = backup_data.get('date', filename.replace('articles_', '').replace('.json', ''))
                            articles = backup_data['articles']
                            
                            if date_str not in articles_by_date:
                                articles_by_date[date_str] = {
                                    'articles': articles,
                                    'count': len(articles),
                                    'sources': list(set(article.get('source', 'Unknown') for article in articles))
                                }
                    except Exception as e:
                        logger.warning(f"백업 파일 로드 실패: {filename} - {e}")
        
        # 날짜별 정렬 (최신 순)
        sorted_dates = sorted(articles_by_date.keys(), reverse=True)
        sorted_articles_by_date = {date: articles_by_date[date] for date in sorted_dates}
        
        total_articles = sum(data['count'] for data in sorted_articles_by_date.values())
        logger.info(f"날짜별 글 로드 완료: {len(sorted_articles_by_date)}일, 총 {total_articles}개 글")
        
        return sorted_articles_by_date
        
    except Exception as e:
        logger.error(f"날짜별 글 데이터 로드 실패: {e}")
        return {}

def load_today_articles():
    """
    오늘 날짜 글 목록 로드 (호환성 유지)
    """
    articles_by_date = load_articles_by_date()
    if articles_by_date:
        # 가장 최근 날짜의 글들 반환
        latest_date = next(iter(articles_by_date))
        latest_data = articles_by_date[latest_date]
        return latest_data['articles'], latest_date
    else:
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
    """메인 대시보드 페이지 - 날짜별 글 구조 (사용자 요구사항 반영)"""
    try:
        # 날짜별로 글 로드
        articles_by_date = load_articles_by_date()
        
        # 전체 통계 계산
        total_articles = 0
        all_sources = set()
        all_tags = []
        
        for date_data in articles_by_date.values():
            total_articles += date_data['count']
            all_sources.update(date_data['sources'])
            
            # 각 날짜의 글에서 태그 추출
            for article in date_data['articles']:
                tags = article.get('tags', [])
                all_tags.extend(tags)
        
        unique_tags = list(set(all_tags))
        
        stats = {
            'total_articles': total_articles,
            'sources_count': len(all_sources),
            'sources': list(all_sources),
            'tags': unique_tags,
            'date_count': len(articles_by_date),
            'dates': list(articles_by_date.keys()),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', 
                             articles_by_date=articles_by_date,
                             stats=stats,
                             is_date_view=True)
                             
    except Exception as e:
        logger.error(f"대시보드 로드 실패: {e}")
        return render_template('dashboard.html', 
                             articles_by_date={},
                             stats={
                                 'total_articles': 0, 
                                 'sources_count': 0, 
                                 'sources': [],
                                 'tags': [],
                                 'date_count': 0,
                                 'dates': [],
                                 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                             },
                             is_date_view=True,
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

@app.route('/api/dates')
def api_dates():
    """사용 가능한 날짜 목록 API"""
    try:
        import glob
        
        # data 디렉토리에서 날짜별 파일 찾기 (articles.json 제외)
        date_files = glob.glob(os.path.join(DATA_DIR, 'articles_*.json'))
        dates = []
        
        for file_path in date_files:
            filename = os.path.basename(file_path)
            
            # articles.json은 제외 (날짜별 파일만 포함)
            if filename == 'articles.json':
                continue
            
            # articles_2025-10-05.json -> 2025-10-05 추출
            date_str = filename.replace('articles_', '').replace('.json', '')
            
            # 날짜 형식 검증 (YYYY-MM-DD)
            if len(date_str) != 10 or date_str.count('-') != 2:
                continue
            
            # 파일 크기와 글 개수 확인
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    article_count = len(data.get('articles', []))
                    dates.append({
                        'date': date_str,
                        'count': article_count,
                        'file': filename
                    })
            except:
                continue
        
        # 날짜 역순 정렬 (최신순)
        dates.sort(key=lambda x: x['date'], reverse=True)
        
        logger.info(f"📅 날짜 목록 조회: {len(dates)}개 날짜")
        
        return jsonify({
            'success': True,
            'dates': dates,
            'total': len(dates)
        })
        
    except Exception as e:
        logger.error(f"날짜 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'dates': []
        }), 500

@app.route('/api/articles/<date>')
def api_articles_by_date(date):
    """특정 날짜의 글 목록 API"""
    try:
        # 파일명 생성
        filename = f'articles_{date}.json'
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': f'{date} 날짜의 데이터가 없습니다.',
                'articles': []
            }), 404
        
        # 파일 로드
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get('articles', [])
        
        return jsonify({
            'success': True,
            'date': date,
            'articles': articles,
            'total': len(articles)
        })
        
    except Exception as e:
        logger.error(f"날짜별 글 조회 실패 ({date}): {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'articles': []
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
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🚀 DS News Aggregator 시작")
    logger.info(f"   - Port: {port}")
    logger.info(f"   - Debug: {debug_mode}")
    logger.info(f"   - Data File: {DATA_FILE}")
    
    # 필요한 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # data/articles.json 파일이 없으면 빈 파일 생성 (초기 실행용)
    if not os.path.exists(DATA_FILE):
        logger.info(f"초기 데이터 파일 생성: {DATA_FILE}")
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'articles': [],
                'stats': {'total': 0, 'sources': []}
            }, f, ensure_ascii=False, indent=2)
    
    # 포트 충돌 확인 (로컬 개발 환경에서만)
    # Railway 같은 프로덕션 환경에서는 PORT 환경변수를 그대로 사용
    if os.getenv('RAILWAY_ENVIRONMENT') is None:  # 로컬 환경에서만 체크
        import socket
        
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        
        if is_port_in_use(port):
            port = 8081
            logger.warning(f"포트 8080이 사용 중입니다. 포트 {port}로 변경합니다.")
    
    # 외부 접근 가능하도록 host='0.0.0.0' 설정
    logger.info(f"🚀 DS News Aggregator 서버 시작")
    logger.info(f"   - 디버그 모드: {debug_mode}")
    logger.info(f"   - 포트: {port}")
    logger.info(f"   - 로컬 접속: http://localhost:{port}")
    logger.info(f"   - 외부 접속: http://<YOUR_IP>:{port}")
    logger.info(f"   - 데이터 파일: {DATA_FILE}")
    
    # 현재 시스템의 IP 주소들 표시
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        ips = []
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip != '127.0.0.1' and not ip.startswith('169.254'):
                        ips.append(ip)
        
        if ips:
            logger.info(f"   - 사용 가능한 외부 IP: {', '.join(ips)}")
        else:
            logger.info(f"   - 외부 IP를 확인할 수 없습니다. 'ifconfig' 명령어로 확인하세요.")
            
    except ImportError:
        # netifaces 라이브러리가 없는 경우, 간단한 방법으로 IP 확인
        try:
            import subprocess
            import re
            
            # macOS/Linux에서 IP 주소 가져오기
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                # inet xxx.xxx.xxx.xxx 형태의 IP 주소 찾기
                ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
                # 로컬호스트와 169.254로 시작하는 IP 제외
                external_ips = [ip for ip in ips if ip != '127.0.0.1' and not ip.startswith('169.254')]
                
                if external_ips:
                    logger.info(f"   - 사용 가능한 외부 IP: {', '.join(external_ips)}")
                else:
                    logger.info(f"   - 터미널에서 'ifconfig'로 IP 주소를 확인하세요.")
            else:
                logger.info(f"   - 터미널에서 'ifconfig'로 IP 주소를 확인하세요.")
                
        except Exception:
            logger.info(f"   - 터미널에서 'ifconfig'로 IP 주소를 확인하세요.")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)