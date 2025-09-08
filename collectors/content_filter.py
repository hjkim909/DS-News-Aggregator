#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Content Filter
사용자 요구사항에 맞는 콘텐츠 필터링 시스템
기본 50점 + 우선 키워드 +10~20점 + 소스 가중치 - 제외 패턴 -30점
최종 70점 이상만 선별하여 5-10개 반환
"""

import re
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter
from difflib import SequenceMatcher
from config import Config

logger = logging.getLogger(__name__)

class ContentFilter:
    """사용자 요구사항에 맞는 콘텐츠 필터링 클래스"""
    
    def __init__(self, config: Config = None):
        """
        콘텐츠 필터 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
    
    def calculate_score(self, title: str, content: str, source_id: str) -> float:
        """
        사용자 요구사항에 맞는 점수 계산
        기본 50점 + 우선 키워드 보너스 + 소스 가중치 - 제외 패턴 패널티
        
        Args:
            title: 글 제목
            content: 글 내용  
            source_id: 소스 식별자
            
        Returns:
            계산된 점수
        """
        score = self.config.BASE_SCORE  # 기본 50점
        
        # 전체 텍스트 (제목 + 내용)
        full_text = (title + " " + content).lower()
        
        # 1. 우선 키워드 보너스 (+10~20점)
        for keyword, bonus in self.config.PRIORITY_KEYWORDS.items():
            if keyword.lower() in full_text:
                score += bonus
                logger.debug(f"우선 키워드 '{keyword}' 보너스: +{bonus}점")
        
        # 2. 제외 패턴 패널티 (-30점)
        for pattern in self.config.EXCLUDE_PATTERNS:
            if pattern.lower() in full_text:
                score -= 30
                logger.debug(f"제외 패턴 '{pattern}' 패널티: -30점")
        
        # 3. 소스 가중치 적용
        source_weight = self.config.SOURCE_WEIGHTS.get(source_id, 0)
        score += source_weight
        logger.debug(f"소스 '{source_id}' 가중치: +{source_weight}점")
        
        return max(0, score)  # 최소 0점
    
    def _is_duplicate(self, article1: Dict[str, Any], article2: Dict[str, Any], 
                     similarity_threshold: float = 0.8) -> bool:
        """
        두 글이 중복인지 확인
        
        Args:
            article1: 첫 번째 글
            article2: 두 번째 글
            similarity_threshold: 유사도 임계값
            
        Returns:
            중복 여부
        """
        # URL이 같으면 중복
        if article1.get('url') == article2.get('url'):
            return True
        
        # 제목 유사도 검사
        title1 = article1.get('title', '').lower()
        title2 = article2.get('title', '').lower()
        
        # 텍스트 정규화
        title1 = re.sub(r'[^\w\s가-힣]', '', title1)
        title2 = re.sub(r'[^\w\s가-힣]', '', title2)
        
        similarity = SequenceMatcher(None, title1, title2).ratio()
        
        return similarity >= similarity_threshold
    
    def _has_ds_ml_keywords(self, article: Dict[str, Any]) -> bool:
        """
        DS/ML 관련 키워드가 있는지 확인 (한국 블로그용)
        
        Args:
            article: 검사할 글
            
        Returns:
            DS/ML 키워드 포함 여부
        """
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        full_text = title + ' ' + content
        
        # DS/ML 키워드 리스트
        ds_ml_keywords = self.config.DS_KEYWORDS + [
            # 추가 키워드
            '인공지능', 'AI', '데이터', '분석', '예측', '모델링',
            '딥러닝', '머신러닝', '기계학습', '신경망', '알고리즘'
        ]
        
        for keyword in ds_ml_keywords:
            if keyword.lower() in full_text:
                return True
        
        return False
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 글 제거
        
        Args:
            articles: 글 목록
            
        Returns:
            중복이 제거된 글 목록
        """
        if not articles:
            return []
        
        unique_articles = []
        
        for article in articles:
            is_duplicate = False
            
            for existing_article in unique_articles:
                if self._is_duplicate(article, existing_article):
                    # 더 높은 점수의 글을 유지
                    if article.get('score', 0) > existing_article.get('score', 0):
                        unique_articles.remove(existing_article)
                        unique_articles.append(article)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        logger.info(f"중복 제거: {len(articles)} → {len(unique_articles)}개")
        return unique_articles
    
    def filter_by_score_threshold(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        점수 임계값(70점 이상)으로 필터링
        
        Args:
            articles: 필터링할 글 목록
            
        Returns:
            임계값 이상의 글 목록
        """
        threshold = self.config.MIN_SCORE_THRESHOLD  # 70점
        
        filtered = [
            article for article in articles 
            if article.get('score', 0) >= threshold
        ]
        
        logger.info(f"점수 필터링: {len(articles)} → {len(filtered)}개 (임계값: {threshold}점)")
        return filtered
    
    def filter_korean_blogs_by_keywords(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        한국 블로그 글에서 DS/ML 키워드 포함 글만 필터링
        
        Args:
            articles: 필터링할 글 목록
            
        Returns:
            키워드 필터링된 글 목록
        """
        korean_blog_sources = ['naver_d2', 'kakao_tech', 'ai_times']
        
        filtered = []
        for article in articles:
            source = article.get('source', '')
            
            # 한국 블로그가 아니면 통과
            if source not in korean_blog_sources:
                filtered.append(article)
            # 한국 블로그면 DS/ML 키워드 체크
            elif self._has_ds_ml_keywords(article):
                filtered.append(article)
            else:
                logger.debug(f"DS/ML 키워드 부족으로 제외: {article.get('title', '')[:50]}")
        
        logger.info(f"한국 블로그 키워드 필터링: {len(articles)} → {len(filtered)}개")
        return filtered
    
    def get_top_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        사용자 요구사항에 맞는 최종 필터링
        70점 이상, 중복 제거 후 5-10개 반환
        
        Args:
            articles: 글 목록
            
        Returns:
            최종 선별된 글 목록
        """
        if not articles:
            return []
        
        logger.info(f"===== 콘텐츠 필터링 시작: {len(articles)}개 글 =====")
        
        # 1단계: 한국 블로그 키워드 필터링
        filtered_articles = self.filter_korean_blogs_by_keywords(articles)
        
        # 2단계: 점수 임계값 필터링 (70점 이상)
        filtered_articles = self.filter_by_score_threshold(filtered_articles)
        
        # 3단계: 중복 제거
        filtered_articles = self.remove_duplicates(filtered_articles)
        
        # 4단계: 점수순 정렬
        filtered_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 5단계: 최종 개수 제한 (5-10개)
        final_count = min(len(filtered_articles), self.config.FINAL_ARTICLE_COUNT)
        filtered_articles = filtered_articles[:final_count]
        
        logger.info(f"===== 필터링 완료: 최종 {len(filtered_articles)}개 글 선별 =====")
        
        # 결과 요약
        if filtered_articles:
            avg_score = sum(article.get('score', 0) for article in filtered_articles) / len(filtered_articles)
            sources = Counter(article.get('source', 'unknown') for article in filtered_articles)
            
            logger.info(f"평균 점수: {avg_score:.1f}")
            logger.info(f"소스별 분포: {dict(sources)}")
        
        return filtered_articles
    
    def analyze_filtering_results(self, original_articles: List[Dict[str, Any]], 
                                 filtered_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        필터링 결과 분석
        
        Args:
            original_articles: 원본 글 목록
            filtered_articles: 필터링된 글 목록
            
        Returns:
            분석 결과
        """
        if not original_articles:
            return {'error': '분석할 글이 없습니다.'}
        
        # 통계 계산
        original_scores = [article.get('score', 0) for article in original_articles]
        filtered_scores = [article.get('score', 0) for article in filtered_articles]
        
        original_sources = Counter(article.get('source', 'unknown') for article in original_articles)
        filtered_sources = Counter(article.get('source', 'unknown') for article in filtered_articles)
        
        analysis = {
            'original_count': len(original_articles),
            'filtered_count': len(filtered_articles),
            'filter_ratio': len(filtered_articles) / len(original_articles) * 100,
            'score_stats': {
                'original': {
                    'min': min(original_scores) if original_scores else 0,
                    'max': max(original_scores) if original_scores else 0,
                    'avg': sum(original_scores) / len(original_scores) if original_scores else 0
                },
                'filtered': {
                    'min': min(filtered_scores) if filtered_scores else 0,
                    'max': max(filtered_scores) if filtered_scores else 0,
                    'avg': sum(filtered_scores) / len(filtered_scores) if filtered_scores else 0
                }
            },
            'source_distribution': {
                'original': dict(original_sources),
                'filtered': dict(filtered_sources)
            },
            'threshold': self.config.MIN_SCORE_THRESHOLD
        }
        
        return analysis


# 유틸리티 함수
def filter_articles(articles: List[Dict[str, Any]], config: Config = None) -> List[Dict[str, Any]]:
    """
    글 필터링 편의 함수
    
    Args:
        articles: 필터링할 글 목록
        config: 설정 객체
        
    Returns:
        필터링된 글 목록
    """
    content_filter = ContentFilter(config)
    return content_filter.get_top_articles(articles)


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 데이터
    test_articles = [
        {
            'id': 'test_1',
            'title': '머신러닝을 활용한 데이터 분석 가이드',
            'content': 'LLM과 시계열 분석에 대한 구현 방법...',
            'score': 85,
            'source': 'naver_d2'
        },
        {
            'id': 'test_2', 
            'title': '추천해주세요 - 어떤 알고리즘이 좋을까요?',
            'content': '질문있어요...',
            'score': 40,
            'source': 'reddit'
        },
        {
            'id': 'test_3',
            'title': 'Python을 이용한 딥러닝 구현',
            'content': '신경망 분석 및 비교...',
            'score': 75,
            'source': 'kakao_tech'
        }
    ]
    
    content_filter = ContentFilter()
    
    filtered = content_filter.get_top_articles(test_articles)
    analysis = content_filter.analyze_filtering_results(test_articles, filtered)
    
    print(f"필터링 결과: {len(filtered)}개 글")
    print(f"분석 결과: {analysis}")
    
    for article in filtered:
        print(f"- {article['title'][:50]} (점수: {article['score']}, 소스: {article['source']})")