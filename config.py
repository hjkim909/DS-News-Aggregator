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
    HOST = os.getenv('HOST', '0.0.0.0')  # 외부 접근 허용
    
    # PRD v2.0: 새로운 소스 구성 (뉴스 50% + 블로그 30% + 기업 20%)
    
    # 뉴스 미디어 소스 비율 설정 (50%)
    NEWS_MEDIA_RATIO = 0.50
    NEWS_MEDIA_MAX_ARTICLES = 6  # 뉴스 3-5개 목표
    
    # 실용 블로그 소스 비율 설정 (30%)
    PRACTICAL_BLOG_RATIO = 0.30
    PRACTICAL_BLOG_MAX_ARTICLES = 4  # 블로그 2-3개 목표
    
    # 기업 블로그 소스 비율 설정 (20%)
    COMPANY_BLOG_RATIO = 0.20
    COMPANY_BLOG_MAX_ARTICLES = 3  # 기업 1-2개 목표
    
    # Google Cloud 설정
    GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Gemini API 설정
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Google Translate 설정
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'ko')
    
    # PRD v2.0 - 뉴스 미디어 소스 설정 (50%) - 작동 확인된 소스만
    NEWS_MEDIA_SOURCES = [
        # 해외 AI 전문 뉴스
        {
            'name': 'TechCrunch AI',
            'url': 'https://techcrunch.com/category/artificial-intelligence/',
            'rss': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'source_id': 'techcrunch_ai',
            'score_bonus': 100,
            'tags': ['뉴스', '해외', 'AI']
        },
        {
            'name': 'MIT Technology Review',
            'url': 'https://www.technologyreview.com/topic/artificial-intelligence/',
            'rss': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
            'source_id': 'mit_tech_review',
            'score_bonus': 110,
            'tags': ['뉴스', '해외', '심층', 'AI']
        },
        {
            'name': 'WIRED AI',
            'url': 'https://www.wired.com/tag/artificial-intelligence/',
            'rss': 'https://www.wired.com/feed/tag/ai/latest/rss',
            'source_id': 'wired_ai',
            'score_bonus': 105,
            'tags': ['뉴스', '해외', 'AI', '기술']
        },
        # 국내 기술 뉴스
        {
            'name': 'Tech42',
            'url': 'https://tech42.co.kr',
            'rss': 'https://tech42.co.kr/feed/',
            'source_id': 'tech42',
            'score_bonus': 85,
            'tags': ['뉴스', '국내', '스타트업', 'AI']
        }
    ]
    
    # PRD v2.0 - 실용 블로그 소스 설정 (30%)
    PRACTICAL_BLOG_SOURCES = [
        {
            'name': 'Towards Data Science',
            'url': 'https://towardsdatascience.com',
            'rss': 'https://towardsdatascience.com/feed',
            'source_id': 'towards_data_science',
            'score_bonus': 80,
            'tags': ['블로그', '튜토리얼', '실용'],
            'clap_filter': True
        },
        {
            'name': 'Analytics Vidhya',
            'url': 'https://www.analyticsvidhya.com',
            'rss': 'https://www.analyticsvidhya.com/blog/feed/',
            'source_id': 'analytics_vidhya',
            'score_bonus': 75,
            'tags': ['블로그', '실습', '교육']
        },
        {
            'name': 'KDnuggets',
            'url': 'https://www.kdnuggets.com',
            'rss': 'https://www.kdnuggets.com/feed',
            'source_id': 'kdnuggets',
            'score_bonus': 75,
            'tags': ['블로그', '리소스', '뉴스']
        },
        {
            'name': 'Distill',
            'url': 'https://distill.pub',
            'rss': 'https://distill.pub/rss.xml',
            'source_id': 'distill',
            'score_bonus': 90,
            'tags': ['블로그', '연구', 'ML시각화']
        },
        {
            'name': 'Hugging Face Blog',
            'url': 'https://huggingface.co/blog',
            'rss': 'https://huggingface.co/blog/feed.xml',
            'source_id': 'huggingface_blog',
            'score_bonus': 85,
            'tags': ['블로그', 'Transformers', 'LLM']
        }
    ]
    
    # PRD v2.0 - 기업 블로그 소스 설정 (20%)
    COMPANY_BLOG_SOURCES = [
        {
            'name': 'Google Developers Blog',
            'url': 'https://developers.googleblog.com',
            'rss': 'https://developers.googleblog.com/feeds/posts/default',
            'source_id': 'google_developers',
            'score_bonus': 70,
            'tags': ['기업블로그', '개발', 'Google']
        },
        {
            'name': 'AWS Machine Learning Blog',
            'url': 'https://aws.amazon.com/blogs/machine-learning',
            'rss': 'https://aws.amazon.com/blogs/machine-learning/feed/',
            'source_id': 'aws_ml',
            'score_bonus': 75,
            'tags': ['기업블로그', 'ML', '클라우드']
        },
        {
            'name': 'Microsoft AI Blog',
            'url': 'https://blogs.microsoft.com/ai',
            'rss': 'https://blogs.microsoft.com/ai/feed/',
            'source_id': 'microsoft_ai',
            'score_bonus': 75,
            'tags': ['기업블로그', 'AI', 'Microsoft']
        },
        {
            'name': 'OpenAI Blog',
            'url': 'https://openai.com/blog',
            'rss': 'https://openai.com/blog/rss.xml',
            'source_id': 'openai_blog',
            'score_bonus': 90,
            'tags': ['기업블로그', '최신기술', 'OpenAI']
        },
        {
            'name': 'NVIDIA Technical Blog',
            'url': 'https://developer.nvidia.com/blog',
            'rss': 'https://developer.nvidia.com/blog/feed/',
            'source_id': 'nvidia_blog',
            'score_bonus': 75,
            'tags': ['기업블로그', 'GPU', 'AI가속']
        }
    ]
    
    # 수집 설정
    COLLECTION_INTERVAL_HOURS = int(os.getenv('COLLECTION_INTERVAL_HOURS', 6))
    MAX_ARTICLES_PER_SOURCE = int(os.getenv('MAX_ARTICLES_PER_SOURCE', 20))  # 요구사항: 일 최대 20개
    SUMMARY_MAX_SENTENCES = int(os.getenv('SUMMARY_MAX_SENTENCES', 3))
    
    # 날짜 필터링 설정 (사용자 요구사항: 최근 1~2달만)
    MAX_ARTICLE_AGE_DAYS = int(os.getenv('MAX_ARTICLE_AGE_DAYS', 60))  # 기본 60일 (2달)
    MIN_PUBLISH_YEAR = int(os.getenv('MIN_PUBLISH_YEAR', 2025))  # 2025년 이후만
    
    # 필터링 설정 - ML/DS/LLM/AI 주제로 강화
    DS_KEYWORDS = [
        # 핵심 AI/ML 키워드
        'machine learning', 'deep learning', 'artificial intelligence', 'neural network',
        'data science', 'data analysis', 'statistics', 'statistical learning',
        
        # LLM 관련
        'llm', 'large language model', 'gpt', 'bert', 'transformer', 'chatgpt',
        'generative ai', 'natural language processing', 'nlp', 'language model',
        
        # 구체적 AI/ML 기술
        'computer vision', 'reinforcement learning', 'supervised learning', 'unsupervised learning',
        'classification', 'regression', 'clustering', 'dimensionality reduction',
        'feature engineering', 'model training', 'hyperparameter', 'optimization',
        
        # AI/ML 라이브러리 및 도구
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'huggingface', 'openai api', 'langchain', 'vector database',
        
        # 데이터 관련
        'big data', 'data mining', 'predictive analytics', 'time series',
        'data visualization', 'business intelligence', 'etl', 'data pipeline',
        
        # 한국어 키워드
        '머신러닝', '딥러닝', '인공지능', '데이터사이언스', '데이터분석',
        'LLM', '대형언어모델', '생성형AI', '자연어처리', '컴퓨터비전',
        '강화학습', '지도학습', '비지도학습', '분류', '회귀', '클러스터링',
        '특성공학', '모델훈련', '하이퍼파라미터', '최적화', '시계열',
        '빅데이터', '데이터마이닝', '예측분석', '데이터시각화', '비즈니스인텔리전스'
    ]
    
    # 제외할 일반 기술 키워드 (AI/ML이 아닌 순수 개발 내용)
    EXCLUDED_TECH_KEYWORDS = [
        'web development', 'frontend', 'backend', 'javascript', 'react', 'vue', 'angular',
        'css', 'html', 'mobile app', 'ios', 'android', 'swift', 'kotlin',
        'database design', 'sql optimization', 'devops', 'kubernetes', 'docker',
        'microservices', 'api design', 'system design', 'networking',
        '웹개발', '프론트엔드', '백엔드', '모바일앱', '데이터베이스설계',
        '시스템설계', '네트워킹', '쿠버네티스', '도커', '마이크로서비스'
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
    
    # PRD v2.0 새로운 점수화 시스템
    # 뉴스 미디어: 100점 기본, 블로그: 80점 기본, 기업: 70점 기본
    SOURCE_BASE_SCORES = {
        # 뉴스 미디어 (100점 기본) - 작동 확인된 소스만
        'techcrunch_ai': 100,
        'mit_tech_review': 110,  # 높은 품질
        'wired_ai': 105,
        'tech42': 85,
        
        # 실용 블로그 (80점 기본)
        'towards_data_science': 80,
        'analytics_vidhya': 75,
        'kdnuggets': 75,
        'distill': 90,
        'huggingface_blog': 85,
        
        # 기업 블로그 (70점 기본)
        'google_developers': 70,
        'aws_ml': 75,
        'microsoft_ai': 75,
        'openai_blog': 90,  # OpenAI 특별 가중치
        'nvidia_blog': 75
    }
    
    # 최소 통과 점수
    MIN_SCORE_THRESHOLD = 70    # 70점 이상만 선별
    FINAL_ARTICLE_COUNT = 20    # 최종 5-10개 (최대 10개로 설정)
    
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
