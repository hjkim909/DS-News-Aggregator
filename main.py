#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Main Collection Script
모든 수집기와 처리기를 통합한 메인 스크립트
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import argparse

# 로컬 모듈 임포트
from config import Config
from collectors.tech_blog_collector import TechBlogCollector
from collectors.medium_collector import MediumCollector
from collectors.hackernews_collector import HackerNewsCollector
from collectors.content_filter import ContentFilter
from processors.translator import Translator
from processors.summarizer import Summarizer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NewsAggregator:
    """뉴스 수집 및 처리 메인 클래스"""
    
    def __init__(self, config: Config = None):
        """
        뉴스 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        
        # 수집기들 초기화
        self.tech_blog_collector = TechBlogCollector(self.config)
        self.medium_collector = MediumCollector(self.config)
        self.hackernews_collector = HackerNewsCollector(self.config)
        self.content_filter = ContentFilter(self.config)
        
        # 처리기들 초기화
        self.translator = Translator(self.config)
        self.summarizer = Summarizer(self.config)
        
        # 상태 추적
        self.collection_stats = {
            'start_time': None,
            'end_time': None,
            'total_collected': 0,
            'tech_blog_articles': 0,
            'medium_articles': 0,
            'hackernews_articles': 0,
            'filtered_articles': 0,
            'translated_articles': 0,
            'summarized_articles': 0,
            'errors': []
        }
    
    def collect_all_articles(self) -> List[Dict[str, Any]]:
        """
        모든 소스에서 글 수집
        
        Returns:
            수집된 모든 글 목록
        """
        logger.info("===== 글 수집 시작 =====")
        self.collection_stats['start_time'] = datetime.now(timezone.utc)
        
        all_articles = []
        
        # 글로벌 기술 블로그에서 수집
        try:
            logger.info("글로벌 기술 블로그에서 글 수집 중...")
            tech_articles = self.tech_blog_collector.collect_all_sources()
            self.collection_stats['tech_blog_articles'] = len(tech_articles)
            all_articles.extend(tech_articles)
            logger.info(f"기술 블로그 수집 완료: {len(tech_articles)}개")
            
        except Exception as e:
            error_msg = f"기술 블로그 수집 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
        
        # Medium에서 수집
        try:
            logger.info("Medium 플랫폼에서 글 수집 중...")
            medium_articles = self.medium_collector.collect_all_medium_sources()
            self.collection_stats['medium_articles'] = len(medium_articles)
            all_articles.extend(medium_articles)
            logger.info(f"Medium 수집 완료: {len(medium_articles)}개")
            
        except Exception as e:
            error_msg = f"Medium 수집 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
        
        # Hacker News에서 수집
        try:
            logger.info("Hacker News에서 글 수집 중...")
            hn_articles = self.hackernews_collector.collect_from_hackernews()
            self.collection_stats['hackernews_articles'] = len(hn_articles)
            all_articles.extend(hn_articles)
            logger.info(f"Hacker News 수집 완료: {len(hn_articles)}개")
            
        except Exception as e:
            error_msg = f"Hacker News 수집 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
        
        self.collection_stats['total_collected'] = len(all_articles)
        logger.info(f"총 수집된 글: {len(all_articles)}개")
        
        return all_articles
    
    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        글 필터링 및 품질 평가
        
        Args:
            articles: 필터링할 글 목록
            
        Returns:
            필터링된 글 목록
        """
        if not articles:
            return []
        
        logger.info("===== 글 필터링 시작 =====")
        
        try:
            filtered_articles = self.content_filter.get_top_articles(
                articles, 
                limit=self.config.ARTICLES_PER_PAGE * 3  # 여유분 포함
            )
            
            self.collection_stats['filtered_articles'] = len(filtered_articles)
            logger.info(f"필터링 완료: {len(filtered_articles)}개 글 선별")
            
            # 품질 분석
            analysis = self.content_filter.analyze_content_quality(filtered_articles)
            logger.info(f"품질 분석: {analysis}")
            
            return filtered_articles
            
        except Exception as e:
            error_msg = f"글 필터링 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return articles
    
    def translate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        글 번역
        
        Args:
            articles: 번역할 글 목록
            
        Returns:
            번역된 글 목록
        """
        if not articles:
            return []
        
        logger.info("===== 글 번역 시작 =====")
        
        try:
            # 번역이 필요한 글만 필터링
            articles_to_translate = [
                article for article in articles 
                if article.get('needs_translation', False)
            ]
            
            if not articles_to_translate:
                logger.info("번역이 필요한 글이 없습니다.")
                return articles
            
            logger.info(f"{len(articles_to_translate)}개 글 번역 시작...")
            
            translated_articles = []
            for article in articles:
                if article.get('needs_translation', False):
                    translated = self.translator.translate_article(article)
                    translated_articles.append(translated)
                    
                    # API 제한 대응
                    time.sleep(0.5)
                else:
                    translated_articles.append(article)
            
            self.collection_stats['translated_articles'] = len(articles_to_translate)
            logger.info(f"번역 완료: {len(articles_to_translate)}개 글")
            
            return translated_articles
            
        except Exception as e:
            error_msg = f"글 번역 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return articles
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        글 요약
        
        Args:
            articles: 요약할 글 목록
            
        Returns:
            요약된 글 목록
        """
        if not articles:
            return []
        
        logger.info("===== 글 요약 시작 =====")
        
        try:
            logger.info(f"{len(articles)}개 글 요약 시작...")
            
            summarized_articles = []
            for i, article in enumerate(articles):
                try:
                    summarized = self.summarizer.summarize_article(article)
                    summarized_articles.append(summarized)
                    
                    # 진행 상황 로그
                    if (i + 1) % 5 == 0:
                        logger.info(f"요약 진행: {i + 1}/{len(articles)}")
                    
                    # API 제한 대응
                    time.sleep(1.5)
                    
                except Exception as e:
                    logger.error(f"개별 글 요약 실패 (인덱스 {i}): {e}")
                    # 요약 실패해도 원본은 포함
                    article['summary'] = article.get('title', '')
                    summarized_articles.append(article)
            
            self.collection_stats['summarized_articles'] = len(summarized_articles)
            logger.info(f"요약 완료: {len(summarized_articles)}개 글")
            
            return summarized_articles
            
        except Exception as e:
            error_msg = f"글 요약 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return articles
    
    def save_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """
        사용자 요구사항에 맞는 JSON 형식으로 글 목록 저장
        
        Args:
            articles: 저장할 글 목록
            
        Returns:
            저장 성공 여부
        """
        try:
            # 데이터 디렉토리 생성
            os.makedirs(os.path.dirname(self.config.ARTICLES_FILE), exist_ok=True)
            
            # 사용자 요구사항에 맞는 데이터 구조로 변환
            today = datetime.now(timezone.utc).date().isoformat()
            
            formatted_data = {
                "date": today,
                "articles": []
            }
            
            # 기존 데이터 로드 (날짜별로 관리)
            existing_data = {}
            if os.path.exists(self.config.ARTICLES_FILE):
                try:
                    with open(self.config.ARTICLES_FILE, 'r', encoding='utf-8') as f:
                        file_content = json.load(f)
                        
                    # 기존 형식이 사용자 요구사항 형식인지 확인
                    if isinstance(file_content, dict) and 'date' in file_content:
                        existing_data[file_content['date']] = file_content['articles']
                    elif isinstance(file_content, list):
                        # 기존 형식을 새 형식으로 변환
                        for article in file_content:
                            article_date = article.get('published', article.get('created_at', today))[:10]
                            if article_date not in existing_data:
                                existing_data[article_date] = []
                            existing_data[article_date].append(article)
                            
                except Exception as e:
                    logger.warning(f"기존 데이터 로드 실패: {e}")
            
            # URL 기준으로 중복 제거
            seen_urls = set()
            today_articles = []
            
            # 오늘 새 글들 추가
            for article in articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    today_articles.append(article)
            
            # 기존 오늘 글 중 중복되지 않는 것들 추가
            if today in existing_data:
                for article in existing_data[today]:
                    url = article.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        today_articles.append(article)
            
            # 점수순으로 정렬
            today_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # 오늘 데이터 업데이트
            formatted_data['articles'] = today_articles
            
            # 저장 (오늘 데이터만 저장)
            with open(self.config.ARTICLES_FILE, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            
            # 히스토리 파일 저장 (선택적)
            history_file = os.path.join(self.config.DATA_DIR, f'articles_{today}.json')
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"글 저장 완료: {len(today_articles)}개 (오늘: {today})")
            logger.info(f"히스토리 파일 저장: {history_file}")
            return True
            
        except Exception as e:
            error_msg = f"글 저장 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return False
    
    def run_full_collection(self) -> Dict[str, Any]:
        """
        전체 수집 프로세스 실행
        
        Returns:
            수집 결과 통계
        """
        logger.info("===== DS News Aggregator 시작 =====")
        
        try:
            # 1단계: 글 수집
            all_articles = self.collect_all_articles()
            
            if not all_articles:
                logger.warning("수집된 글이 없습니다.")
                return self.get_collection_stats()
            
            # 2단계: 필터링 및 품질 평가
            filtered_articles = self.filter_articles(all_articles)
            
            # 3단계: 번역
            translated_articles = self.translate_articles(filtered_articles)
            
            # 4단계: 요약
            summarized_articles = self.summarize_articles(translated_articles)
            
            # 5단계: 저장
            self.save_articles(summarized_articles)
            
            self.collection_stats['end_time'] = datetime.now(timezone.utc)
            
            logger.info("===== 수집 프로세스 완료 =====")
            
        except Exception as e:
            error_msg = f"수집 프로세스 전체 실패: {e}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
        
        return self.get_collection_stats()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        수집 통계 반환
        
        Returns:
            수집 통계 딕셔너리
        """
        stats = self.collection_stats.copy()
        
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['duration_seconds'] = duration.total_seconds()
            stats['duration_str'] = str(duration).split('.')[0]  # 초 단위까지만
        
        return stats


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='DS News Aggregator')
    parser.add_argument('--config', default='development', 
                       choices=['development', 'production', 'testing'],
                       help='설정 환경')
    parser.add_argument('--collect-only', action='store_true',
                       help='수집만 실행 (번역/요약 제외)')
    parser.add_argument('--translate-only', action='store_true',
                       help='기존 글들만 번역')
    parser.add_argument('--summarize-only', action='store_true',
                       help='기존 글들만 요약')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='상세 로그 출력')
    
    args = parser.parse_args()
    
    # 로그 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 설정 로드
    config = Config()
    
    # 로그 디렉토리 생성
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    # 뉴스 수집기 초기화
    aggregator = NewsAggregator(config)
    
    try:
        if args.collect_only:
            # 수집만 실행
            articles = aggregator.collect_all_articles()
            filtered = aggregator.filter_articles(articles)
            aggregator.save_articles(filtered)
            
        elif args.translate_only:
            # 기존 글들 번역
            with open(config.ARTICLES_FILE, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            translated = aggregator.translate_articles(articles)
            aggregator.save_articles(translated)
            
        elif args.summarize_only:
            # 기존 글들 요약
            with open(config.ARTICLES_FILE, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            summarized = aggregator.summarize_articles(articles)
            aggregator.save_articles(summarized)
            
        else:
            # 전체 프로세스 실행
            stats = aggregator.run_full_collection()
            
            # 결과 출력
            print("\n===== 수집 결과 =====")
            print(f"수집된 글: {stats['total_collected']}개")
            print(f"- Reddit: {stats['reddit_articles']}개")
            print(f"- 한국 블로그: {stats['korean_blog_articles']}개")
            print(f"필터링된 글: {stats['filtered_articles']}개")
            print(f"번역된 글: {stats['translated_articles']}개")
            print(f"요약된 글: {stats['summarized_articles']}개")
            
            if stats.get('duration_str'):
                print(f"소요 시간: {stats['duration_str']}")
            
            if stats['errors']:
                print(f"오류 {len(stats['errors'])}개:")
                for error in stats['errors']:
                    print(f"  - {error}")
    
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
