#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Collectors Test Script
수집기들을 개별적으로 테스트하는 스크립트
"""

import logging
import json
from datetime import datetime

from config import Config
from collectors.reddit_collector import RedditCollector
from collectors.korean_blog_collector import KoreanBlogCollector
from collectors.content_filter import ContentFilter

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_reddit_collector():
    """Reddit 수집기 테스트"""
    print("\n" + "="*50)
    print("Reddit Collector 테스트")
    print("="*50)
    
    collector = RedditCollector()
    
    if not collector.test_connection():
        print("❌ Reddit API 연결 실패 - API 키를 확인해주세요")
        return
    
    print("✅ Reddit API 연결 성공")
    
    # MachineLearning 서브레딧에서 5개만 테스트 수집
    articles = collector.collect_from_subreddit('MachineLearning', limit=5)
    
    print(f"수집된 글 수: {len(articles)}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   점수: {article['score']:.1f} | 업보트: {article.get('reddit_score', 0)} | 태그: {article.get('tags', [])}")
        print(f"   URL: {article['url'][:100]}...")

def test_korean_blog_collector():
    """한국 블로그 수집기 테스트"""
    print("\n" + "="*50)
    print("Korean Blog Collector 테스트")
    print("="*50)
    
    collector = KoreanBlogCollector()
    
    # 네이버 D2만 테스트 (빠른 테스트를 위해)
    test_source = {
        'name': '네이버 D2',
        'url': 'https://d2.naver.com/news',
        'rss': 'https://d2.naver.com/news.rss',
        'source_id': 'naver_d2'
    }
    
    articles = collector.collect_from_source(test_source)
    
    print(f"수집된 글 수: {len(articles)}")
    
    for i, article in enumerate(articles[:5], 1):  # 상위 5개만 표시
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   점수: {article['score']:.1f} | 소스: {article['source']} | 태그: {article.get('tags', [])}")
        print(f"   URL: {article['url'][:100]}...")

def test_content_filter():
    """컨텐츠 필터 테스트"""
    print("\n" + "="*50)
    print("Content Filter 테스트")
    print("="*50)
    
    # 테스트 데이터 생성
    test_articles = [
        {
            'id': 'test_1',
            'title': '머신러닝을 활용한 데이터 분석 가이드',
            'content': 'LLM과 시계열 분석에 대한 구현 방법을 설명합니다.',
            'score': 85,
            'source': 'naver_d2',
            'url': 'https://example.com/1'
        },
        {
            'id': 'test_2',
            'title': '추천해주세요 - 어떤 알고리즘이 좋을까요?',
            'content': '질문있어요. 도와주세요.',
            'score': 35,  # 제외 패턴으로 점수 감소
            'source': 'reddit',
            'url': 'https://example.com/2'
        },
        {
            'id': 'test_3',
            'title': 'Python을 이용한 딥러닝 구현',
            'content': '신경망 분석 및 비교 연구에 대한 내용입니다.',
            'score': 78,
            'source': 'kakao_tech',
            'url': 'https://example.com/3'
        },
        {
            'id': 'test_4',
            'title': '일반적인 프로그래밍 글',
            'content': '일반적인 개발 내용...',
            'score': 45,  # DS/ML 키워드 부족으로 낮은 점수
            'source': 'ai_times',
            'url': 'https://example.com/4'
        },
        {
            'id': 'test_5',
            'title': 'AI 시계열 예측 모델 구현 방법',
            'content': 'LLM과 데이터 분석을 통한 시계열 예측 가이드...',
            'score': 95,
            'source': 'naver_d2',
            'url': 'https://example.com/5'
        }
    ]
    
    content_filter = ContentFilter()
    
    print(f"원본 글 수: {len(test_articles)}")
    print("점수 분포:")
    for article in test_articles:
        print(f"  {article['title'][:50]}: {article['score']:.1f}점 ({article['source']})")
    
    # 필터링 실행
    filtered_articles = content_filter.get_top_articles(test_articles)
    
    print(f"\n필터링 후 글 수: {len(filtered_articles)}")
    print("선별된 글:")
    for i, article in enumerate(filtered_articles, 1):
        print(f"  {i}. {article['title'][:60]}: {article['score']:.1f}점 ({article['source']})")
    
    # 분석 결과
    analysis = content_filter.analyze_filtering_results(test_articles, filtered_articles)
    print(f"\n필터링 비율: {analysis['filter_ratio']:.1f}%")
    print(f"평균 점수 변화: {analysis['score_stats']['original']['avg']:.1f} → {analysis['score_stats']['filtered']['avg']:.1f}")

def save_test_results():
    """테스트 결과를 파일로 저장"""
    print("\n" + "="*50)
    print("테스트 결과 저장")
    print("="*50)
    
    # Reddit 테스트
    reddit_collector = RedditCollector()
    reddit_articles = []
    
    if reddit_collector.test_connection():
        reddit_articles = reddit_collector.collect_from_subreddit('MachineLearning', limit=3)
    
    # 한국 블로그 테스트  
    korean_collector = KoreanBlogCollector()
    korean_articles = []
    
    test_source = {
        'name': '네이버 D2',
        'url': 'https://d2.naver.com/news', 
        'rss': 'https://d2.naver.com/news.rss',
        'source_id': 'naver_d2'
    }
    
    korean_articles = korean_collector.collect_from_source(test_source)[:3]
    
    # 결합 및 필터링
    all_articles = reddit_articles + korean_articles
    
    if all_articles:
        content_filter = ContentFilter()
        filtered_articles = content_filter.get_top_articles(all_articles)
        
        # 사용자 요구사항 형식으로 저장
        test_data = {
            "date": datetime.now().date().isoformat(),
            "articles": filtered_articles
        }
        
        with open('data/test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 테스트 결과 저장 완료: data/test_results.json")
        print(f"총 {len(filtered_articles)}개 글 저장")
    else:
        print("❌ 테스트할 데이터가 없습니다.")

def main():
    """메인 테스트 함수"""
    config = Config()
    
    print("DS News Aggregator - Collectors Test")
    print(f"테스트 시작 시간: {datetime.now()}")
    print(f"설정:")
    print(f"  - Reddit 서브레딧: {config.REDDIT_SUBREDDITS}")
    print(f"  - 한국 블로그 소스: {len(config.KOREAN_BLOG_SOURCES)}개")
    print(f"  - 최소 점수 임계값: {config.MIN_SCORE_THRESHOLD}")
    print(f"  - 최소 업보트: {config.MIN_UPVOTES}")
    
    # 개별 테스트 실행
    try:
        test_content_filter()  # 의존성이 없는 것부터
        test_korean_blog_collector()
        test_reddit_collector()
        save_test_results()
        
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 중 오류 발생: {e}")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    main()
