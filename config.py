#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Configuration Module
환경 변수와 설정 관리
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Config:
    """기본 설정 클래스"""
    
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Reddit API 설정 (사용 중지 - 고민상담글 많음)
    # REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
    # REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
    # REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'DSNewsAggregator/1.0')
    
    # Reddit 서브레딧 설정 (사용 중지)
    # REDDIT_SUBREDDITS = [
    #     'MachineLearning',
    #     'datascience'
    # ]
    
    # Google Cloud 설정
    GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Gemini API 설정
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Google Translate 설정
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'ko')
    
    # 고품질 기술 블로그 소스 설정
    TECH_BLOG_SOURCES = [
        # 글로벌 AI/ML 블로그
        {
            'name': 'Google AI Blog',
            'url': 'https://ai.googleblog.com',
            'rss': 'https://ai.googleblog.com/feeds/posts/default',
            'source_id': 'google_ai'
        },
        {
            'name': 'OpenAI Blog',
            'url': 'https://openai.com/blog',
            'rss': 'https://openai.com/blog/rss.xml',
            'source_id': 'openai'
        },
        # 기술 회사 블로그
        {
            'name': 'Netflix Tech Blog',
            'url': 'https://netflixtechblog.com',
            'rss': 'https://netflixtechblog.com/feed',
            'source_id': 'netflix_tech'
        },
        {
            'name': 'Uber Engineering',
            'url': 'https://eng.uber.com',
            'rss': 'https://eng.uber.com/rss/',
            'source_id': 'uber_eng'
        },
        # 한국 기술 블로그 (유지)
        {
            'name': '네이버 D2',
            'url': 'https://d2.naver.com/news',
            'rss': 'https://d2.naver.com/news.rss',
            'source_id': 'naver_d2'
        },
        {
            'name': '카카오테크',
            'url': 'https://tech.kakao.com/blog',
            'rss': 'https://tech.kakao.com/rss.xml',
            'source_id': 'kakao_tech'
        }
    ]
    
    # Medium 계열 소스
    MEDIUM_SOURCES = [
        {
            'name': 'Towards Data Science',
            'url': 'https://towardsdatascience.com',
            'rss': 'https://towardsdatascience.com/feed',
            'source_id': 'towards_ds'
        },
        {
            'name': 'Better Programming',
            'url': 'https://betterprogramming.pub',
            'rss': 'https://betterprogramming.pub/feed',
            'source_id': 'better_prog'
        },
        {
            'name': 'The Startup',
            'url': 'https://medium.com/swlh',
            'rss': 'https://medium.com/feed/swlh',
            'source_id': 'the_startup'
        }
    ]
    
    # Hacker News 설정 (별도 API 사용)
    HACKER_NEWS_CONFIG = {
        'name': 'Hacker News',
        'base_url': 'https://hacker-news.firebaseio.com/v0',
        'web_url': 'https://news.ycombinator.com',
        'source_id': 'hackernews'
    }
    
    # 수집 설정
    COLLECTION_INTERVAL_HOURS = int(os.getenv('COLLECTION_INTERVAL_HOURS', 6))
    MAX_ARTICLES_PER_SOURCE = int(os.getenv('MAX_ARTICLES_PER_SOURCE', 20))  # 요구사항: 일 최대 20개
    SUMMARY_MAX_SENTENCES = int(os.getenv('SUMMARY_MAX_SENTENCES', 3))
    
    # 필터링 설정
    DS_KEYWORDS = [
        'machine learning', 'data science', 'artificial intelligence', 'deep learning',
        'neural network', 'statistics', 'data analysis', 'big data', 'analytics',
        'python data', 'r programming', 'pandas', 'numpy', 'scikit-learn',
        'tensorflow', 'pytorch', 'keras', 'jupyter', 'visualization',
        '머신러닝', '딥러닝', '데이터사이언스', '인공지능', '통계학',
        '데이터분석', '빅데이터', '분석', '시각화', '예측모델'
    ]
    
    TECH_KEYWORDS = [
        'python', 'programming', 'development', 'software', 'coding',
        'algorithm', 'backend', 'frontend', 'database', 'cloud',
        '프로그래밍', '개발', '소프트웨어', '코딩', '알고리즘',
        '백엔드', '프론트엔드', '데이터베이스', '클라우드'
    ]
    
    # 사용자 요구사항에 맞는 점수화 시스템
    BASE_SCORE = 50  # 기본 점수
    
    # 우선 키워드 (+10~20점)
    PRIORITY_KEYWORDS = {
        '방법': 15, '가이드': 20, '분석': 15, '비교': 15, '구현': 20,
        'LLM': 20, '시계열': 15, 'method': 15, 'guide': 20, 'analysis': 15,
        'comparison': 15, 'implementation': 20, 'time series': 15
    }
    
    # 제외 패턴 (-30점)
    EXCLUDE_PATTERNS = [
        '추천해주세요', '어떻게 생각', '감탄사', 'recommend', 'what do you think'
    ]
    
    # 소스 가중치 (업데이트됨)
    SOURCE_WEIGHTS = {
        # 최고 품질 AI/ML 소스
        'google_ai': 40,        # Google AI Blog +40점
        'openai': 40,           # OpenAI Blog +40점
        
        # 고품질 기술 회사 블로그
        'netflix_tech': 35,     # Netflix Tech +35점
        'uber_eng': 35,         # Uber Engineering +35점
        
        # Medium 계열 (높은 품질)
        'towards_ds': 35,       # Towards Data Science +35점
        'better_prog': 30,      # Better Programming +30점
        'the_startup': 25,      # The Startup +25점
        
        # 한국 기술블로그
        'naver_d2': 30,         # 네이버 D2 +30점
        'kakao_tech': 30,       # 카카오테크 +30점
        
        # Hacker News (큐레이션됨)
        'hackernews': 20        # Hacker News +20점
    }
    
    # 최소 통과 점수
    MIN_SCORE_THRESHOLD = 70    # 70점 이상만 선별
    FINAL_ARTICLE_COUNT = 10    # 최종 5-10개 (최대 10개로 설정)
    
    # Reddit 업보트 최소 기준
    MIN_UPVOTES = 5             # upvote 5개 이상만
    
    # 파일 경로
    DATA_DIR = 'data'
    ARTICLES_FILE = os.path.join(DATA_DIR, 'articles.json')
    LOG_DIR = 'logs'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # API 제한 설정
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    # UI 설정
    ARTICLES_PER_PAGE = 20
    RECENT_DAYS = 7


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # 프로덕션에서는 더 엄격한 설정
    REQUEST_TIMEOUT = 20
    MAX_ARTICLES_PER_SOURCE = 5


class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    DEBUG = True
    
    # 테스트용 더미 데이터
    ARTICLES_FILE = 'data/test_articles.json'


# 환경별 설정 매핑
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """현재 환경에 맞는 설정 반환"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
