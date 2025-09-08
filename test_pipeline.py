#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Pipeline Test Script
전체 파이프라인을 테스트하는 스크립트
"""

import logging
import os
from datetime import datetime

from config import Config
from processors.pipeline import DSNewsPipeline, run_ds_news_pipeline
from processors.translator import Translator
from processors.summarizer import Summarizer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_api_connections():
    """API 연결 상태 체크"""
    print("\n" + "="*50)
    print("API 연결 상태 체크")
    print("="*50)
    
    config = Config()
    
    # 환경 변수 체크
    env_status = {
        'REDDIT_CLIENT_ID': bool(config.REDDIT_CLIENT_ID),
        'REDDIT_CLIENT_SECRET': bool(config.REDDIT_CLIENT_SECRET),
        'GEMINI_API_KEY': bool(config.GEMINI_API_KEY)
    }
    
    print("환경 변수 상태:")
    for key, status in env_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {key}: {'설정됨' if status else '설정 필요'}")
    
    # API 연결 테스트
    print("\nAPI 연결 테스트:")
    
    # Reddit API 테스트
    try:
        from collectors.reddit_collector import RedditCollector
        reddit_collector = RedditCollector(config)
        reddit_status = reddit_collector.test_connection()
        print(f"  {'✅' if reddit_status else '❌'} Reddit API: {'연결됨' if reddit_status else '연결 실패'}")
    except Exception as e:
        print(f"  ❌ Reddit API: 오류 - {e}")
    
    # Gemini API 테스트
    try:
        summarizer = Summarizer(config)
        gemini_status = summarizer.test_connection()
        print(f"  {'✅' if gemini_status else '❌'} Gemini API: {'연결됨' if gemini_status else '연결 실패'}")
    except Exception as e:
        print(f"  ❌ Gemini API: 오류 - {e}")
    
    # googletrans 테스트
    try:
        translator = Translator(config)
        translator_stats = translator.get_translation_stats()
        translator_status = translator_stats['googletrans_available']
        print(f"  {'✅' if translator_status else '❌'} googletrans: {'사용 가능' if translator_status else '사용 불가'}")
    except Exception as e:
        print(f"  ❌ googletrans: 오류 - {e}")
    
    return all([env_status['REDDIT_CLIENT_ID'], env_status['REDDIT_CLIENT_SECRET']])

def test_individual_components():
    """개별 컴포넌트 테스트"""
    print("\n" + "="*50)
    print("개별 컴포넌트 테스트")
    print("="*50)
    
    config = Config()
    
    # 번역 테스트
    print("📝 번역기 테스트:")
    translator = Translator(config)
    
    test_cases = [
        "Machine Learning is transforming data analysis.",  # 영문 -> 번역
        "머신러닝이 데이터 분석을 변화시키고 있습니다.",  # 한국어 -> 스킵
        "A" * 2500  # 긴 텍스트 -> 1000자 제한
    ]
    
    for i, text in enumerate(test_cases, 1):
        result = translator.translate_text(text)
        print(f"  {i}. 번역 {'성공' if result['success'] else '실패'}: "
              f"필요={result['translation_needed']}, "
              f"언어={result['source_language']}")
    
    # 요약 테스트
    print("\n📄 요약기 테스트:")
    summarizer = Summarizer(config)
    
    test_title = "머신러닝을 활용한 데이터 분석 방법"
    test_content = "머신러닝은 현대 데이터 분석의 핵심 기술입니다. 다양한 알고리즘을 통해 패턴을 발견할 수 있습니다. 특히 딥러닝 기술의 발전으로 더 정교한 분석이 가능해졌습니다."
    
    summary_result = summarizer.summarize_text(test_title, test_content)
    print(f"  요약 {'성공' if summary_result['success'] else '실패'}: "
          f"{summary_result['sentences_count']}문장, "
          f"서비스={summary_result['service']}")
    
    if summary_result['success']:
        print(f"  요약: {summary_result['summary'][:100]}...")

def test_mini_pipeline():
    """미니 파이프라인 테스트 (소량 데이터)"""
    print("\n" + "="*50)
    print("미니 파이프라인 테스트")
    print("="*50)
    
    try:
        pipeline = DSNewsPipeline()
        
        # 1단계: 소량 수집 (테스트용)
        print("1️⃣ 소량 글 수집 중...")
        reddit_articles = pipeline.reddit_collector.collect_from_subreddit('MachineLearning', limit=3)
        korean_articles = pipeline.korean_blog_collector.collect_from_source({
            'name': '네이버 D2',
            'url': 'https://d2.naver.com/news',
            'rss': 'https://d2.naver.com/news.rss',
            'source_id': 'naver_d2'
        })[:2]  # 상위 2개만
        
        all_articles = reddit_articles + korean_articles
        print(f"   수집된 글: {len(all_articles)}개")
        
        if not all_articles:
            print("   ❌ 수집된 글이 없습니다. API 키를 확인하세요.")
            return False
        
        # 2단계: 필터링
        print("2️⃣ 필터링 중...")
        filtered = pipeline.step2_filter_articles(all_articles)
        print(f"   필터링 후: {len(filtered)}개")
        
        if not filtered:
            print("   ❌ 필터링 후 남은 글이 없습니다.")
            return False
        
        # 3단계: 번역 (1개만)
        print("3️⃣ 번역 중...")
        if filtered:
            test_article = filtered[0]
            translated = pipeline.translator.translate_article(test_article)
            print(f"   번역 {'성공' if translated.get('translation_success', False) else '실패'}")
        
        # 4단계: 요약 (1개만)
        print("4️⃣ 요약 중...")
        if filtered:
            summarized = pipeline.summarizer.summarize_article(translated)
            print(f"   요약 {'성공' if summarized.get('summarization_success', False) else '실패'}")
            
            if summarized.get('summary'):
                print(f"   요약: {summarized['summary'][:80]}...")
        
        # 5단계: 저장
        print("5️⃣ 저장 중...")
        save_success = pipeline.step5_save_articles(filtered[:2])  # 상위 2개만 저장
        print(f"   저장 {'성공' if save_success else '실패'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 미니 파이프라인 실패: {e}")
        return False

def test_full_pipeline():
    """전체 파이프라인 테스트"""
    print("\n" + "="*50)
    print("전체 파이프라인 테스트")
    print("="*50)
    
    try:
        stats = run_ds_news_pipeline()
        
        print("파이프라인 실행 결과:")
        print(f"  📊 전체 소요 시간: {stats.get('total_duration_str', 'N/A')}")
        print(f"  📈 수집된 글: {stats['original_articles']}개")
        print(f"  🔍 필터링된 글: {stats['filtered_articles']}개")
        print(f"  🌐 번역된 글: {stats['translated_articles']}개")
        print(f"  📄 요약된 글: {stats['summarized_articles']}개")
        print(f"  💾 저장된 글: {stats['final_articles']}개")
        
        if stats['errors']:
            print(f"  ⚠️  오류 {len(stats['errors'])}개:")
            for error in stats['errors'][:3]:  # 상위 3개만 표시
                print(f"    - {error}")
        
        # 성공 여부 판단
        success = stats['final_articles'] > 0
        print(f"\n{'✅ 전체 파이프라인 성공!' if success else '❌ 전체 파이프라인 실패'}")
        
        return success
        
    except Exception as e:
        print(f"❌ 전체 파이프라인 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 DS News Aggregator - Pipeline Test")
    print(f"테스트 시작 시간: {datetime.now()}")
    
    # 데이터 디렉토리 확인
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 1. API 연결 상태 체크
    api_ready = check_api_connections()
    
    # 2. 개별 컴포넌트 테스트
    test_individual_components()
    
    if api_ready:
        # 3. 미니 파이프라인 테스트
        mini_success = test_mini_pipeline()
        
        if mini_success:
            # 4. 전체 파이프라인 테스트 (옵션)
            print("\n전체 파이프라인을 실행하시겠습니까? (y/n): ", end="")
            try:
                choice = input().lower().strip()
                if choice in ['y', 'yes']:
                    test_full_pipeline()
                else:
                    print("전체 파이프라인 테스트를 건너뜁니다.")
            except KeyboardInterrupt:
                print("\n테스트가 중단되었습니다.")
    else:
        print("\n❌ API 키가 설정되지 않아 파이프라인 테스트를 건너뜁니다.")
        print("📋 설정 방법:")
        print("1. env_example.txt 파일 내용을 확인")
        print("2. .env 파일을 생성하고 실제 API 키로 교체")
        print("3. 다시 테스트 실행")
    
    print(f"\n🏁 테스트 종료: {datetime.now()}")

if __name__ == "__main__":
    main()
