#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Reddit Collector
Reddit API를 통한 DS/ML 관련 글 수집
"""

import praw
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time
import re
from config import Config

logger = logging.getLogger(__name__)

class RedditCollector:
    """Reddit에서 DS/ML 관련 글을 수집하는 클래스"""
    
    def __init__(self, config: Config = None):
        """
        Reddit 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.reddit = None
        self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Reddit API 클라이언트 초기화"""
        try:
            if not all([
                self.config.REDDIT_CLIENT_ID,
                self.config.REDDIT_CLIENT_SECRET,
                self.config.REDDIT_USER_AGENT
            ]):
                logger.warning("Reddit API 설정이 완전하지 않습니다. 일부 기능이 제한될 수 있습니다.")
                return
                
            self.reddit = praw.Reddit(
                client_id=self.config.REDDIT_CLIENT_ID,
                client_secret=self.config.REDDIT_CLIENT_SECRET,
                user_agent=self.config.REDDIT_USER_AGENT,
                ratelimit_seconds=600  # 10분간 요청 제한
            )
            
            # 연결 테스트
            self.reddit.user.me()
            logger.info("Reddit API 연결 성공")
            
        except Exception as e:
            logger.error(f"Reddit API 초기화 실패: {e}")
            self.reddit = None
    
    def _calculate_score(self, submission) -> float:
        """
        사용자 요구사항에 맞는 점수 계산 시스템
        기본 50점 + 우선 키워드 +10~20점 + 소스 가중치 +10점 - 제외 패턴 -30점
        
        Args:
            submission: Reddit submission 객체
            
        Returns:
            계산된 점수
        """
        try:
            title_lower = submission.title.lower()
            selftext_lower = (submission.selftext or '').lower()
            full_text = title_lower + ' ' + selftext_lower
            
            # 기본 점수
            score = self.config.BASE_SCORE
            
            # 우선 키워드 점수 (+10~20점)
            for keyword, bonus in self.config.PRIORITY_KEYWORDS.items():
                if keyword.lower() in full_text:
                    score += bonus
                    logger.debug(f"우선 키워드 '{keyword}' 발견: +{bonus}점")
            
            # 소스 가중치 (Reddit: +10점)
            score += self.config.SOURCE_WEIGHTS.get('reddit', 0)
            
            # 제외 패턴 체크 (-30점)
            for pattern in self.config.EXCLUDE_PATTERNS:
                if pattern.lower() in full_text:
                    score -= 30
                    logger.debug(f"제외 패턴 '{pattern}' 발견: -30점")
            
            # Reddit 메트릭 보너스 (소폭)
            score += min(submission.score * 0.1, 10)  # 업보트 보너스 (최대 10점)
            score += min(submission.num_comments * 0.05, 5)  # 댓글 보너스 (최대 5점)
            
            # 품질 패널티
            if len(submission.title) < 10:
                score -= 10
            
            if submission.selftext in ['[removed]', '[deleted]']:
                score = 0  # 삭제된 글은 0점
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"점수 계산 실패: {e}")
            return 0.0
    
    def _extract_tags(self, text: str) -> List[str]:
        """
        텍스트에서 태그 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 태그 리스트
        """
        try:
            tags = []
            text_lower = text.lower()
            
            # 주요 태그 키워드 맵핑
            tag_keywords = {
                'LLM': ['llm', 'large language model', 'gpt', 'bert', 'transformer'],
                '시계열': ['time series', 'timeseries', 'temporal', 'forecasting'],
                '머신러닝': ['machine learning', 'ml', 'supervised', 'unsupervised'],
                '딥러닝': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm'],
                '데이터분석': ['data analysis', 'analytics', 'visualization', 'pandas'],
                '통계': ['statistics', 'statistical', 'hypothesis', 'regression'],
                '자연어처리': ['nlp', 'natural language processing', 'text mining'],
                '컴퓨터비전': ['computer vision', 'cv', 'image', 'opencv'],
                'Python': ['python', 'pandas', 'numpy', 'scikit-learn'],
                'R': [' r ', 'rstudio', 'tidyverse']
            }
            
            for tag, keywords in tag_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if tag not in tags:
                            tags.append(tag)
                        break
            
            return tags[:5]  # 최대 5개 태그
            
        except Exception as e:
            logger.error(f"태그 추출 실패: {e}")
            return []
    
    def _extract_submission_data(self, submission) -> Dict[str, Any]:
        """
        Reddit submission에서 필요한 데이터 추출
        
        Args:
            submission: Reddit submission 객체
            
        Returns:
            추출된 데이터 딕셔너리
        """
        try:
            created_utc = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
            
            # 본문 텍스트 정리
            selftext = submission.selftext or ''
            if selftext in ['[removed]', '[deleted]']:
                selftext = ''
            
            # 이미지/비디오 링크 확인
            is_media = any(ext in submission.url.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm'])
            
            data = {
                'id': f"reddit_{submission.id}",
                'title': submission.title,
                'title_ko': '',  # 번역 후 채워짐
                'content': selftext,
                'content_ko': '',  # 번역 후 채워짐
                'summary': '',  # 요약 후 채워짐
                'url': submission.url,
                'source': 'reddit',  # 요구사항에 맞는 소스 형식
                'tags': self._extract_tags(submission.title + ' ' + selftext),  # 태그 추출
                'score': self._calculate_score(submission),  # 사용자 요구사항 점수 시스템
                'published': created_utc.isoformat(),
                # 추가 메타데이터 (기존 정보 유지)
                'reddit_score': submission.score,
                'num_comments': submission.num_comments,
                'upvote_ratio': submission.upvote_ratio,
                'subreddit': f"r/{submission.subreddit.display_name}",
                'author': str(submission.author) if submission.author else '[deleted]',
                'is_self': submission.is_self,
                'flair': submission.link_flair_text,
                'language': 'en',  # Reddit은 주로 영어
                'needs_translation': True,
                'collected_at': datetime.now(timezone.utc).isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return None
    
    def collect_from_subreddit(self, subreddit_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        특정 서브레딧에서 글 수집 (upvote 5개 이상만)
        
        Args:
            subreddit_name: 서브레딧 이름
            limit: 수집할 글 수 제한
            
        Returns:
            수집된 글 목록
        """
        if not self.reddit:
            logger.error("Reddit API가 초기화되지 않았습니다.")
            return []
        
        limit = limit or self.config.MAX_ARTICLES_PER_SOURCE
        articles = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"r/{subreddit_name}에서 글 수집 시작 (upvote {self.config.MIN_UPVOTES}개 이상, 최대 {limit}개)")
            
            # 핫한 글과 새로운 글을 더 많이 수집 (필터링으로 줄어들 것을 고려)
            submissions = list(subreddit.hot(limit=limit)) + list(subreddit.new(limit=limit))
            
            for submission in submissions:
                try:
                    # 요청 제한 대응
                    time.sleep(0.1)
                    
                    # upvote 5개 이상 조건 체크
                    if submission.score < self.config.MIN_UPVOTES:
                        continue
                    
                    data = self._extract_submission_data(submission)
                    if data and data['score'] > 0:
                        articles.append(data)
                    
                    # 목표 개수 달성시 종료
                    if len(articles) >= limit:
                        break
                    
                except Exception as e:
                        logger.error(f"글 처리 실패 (ID: {submission.id}): {e}")
                        continue
            
            # 품질 점수로 정렬
            articles.sort(key=lambda x: x['score'], reverse=True)
            logger.info(f"r/{subreddit_name}에서 {len(articles)}개 글 수집 완료 (upvote {self.config.MIN_UPVOTES}개 이상)")
            
            return articles[:limit]
            
        except Exception as e:
            logger.error(f"r/{subreddit_name} 수집 실패: {e}")
            return []
    
    def collect_all_subreddits(self) -> List[Dict[str, Any]]:
        """
        모든 설정된 서브레딧에서 글 수집
        
        Returns:
            모든 서브레딧에서 수집된 글 목록
        """
        if not self.reddit:
            logger.error("Reddit API가 초기화되지 않았습니다.")
            return []
        
        all_articles = []
        
        for subreddit_name in self.config.REDDIT_SUBREDDITS:
            try:
                articles = self.collect_from_subreddit(subreddit_name)
                all_articles.extend(articles)
                
                # API 요청 제한 대응
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"서브레딧 r/{subreddit_name} 수집 중 오류: {e}")
                continue
        
        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_articles = []
        
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # 최종 품질 점수로 정렬
        unique_articles.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Reddit에서 총 {len(unique_articles)}개 유니크 글 수집 완료")
        return unique_articles
    
    def test_connection(self) -> bool:
        """
        Reddit API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        if not self.reddit:
            return False
        
        try:
            # 간단한 요청으로 연결 테스트
            subreddit = self.reddit.subreddit('test')
            list(subreddit.hot(limit=1))
            return True
            
        except Exception as e:
            logger.error(f"Reddit 연결 테스트 실패: {e}")
            return False


# 유틸리티 함수
def collect_reddit_articles(config: Config = None) -> List[Dict[str, Any]]:
    """
    Reddit에서 글 수집하는 편의 함수
    
    Args:
        config: 설정 객체
        
    Returns:
        수집된 글 목록
    """
    collector = RedditCollector(config)
    return collector.collect_all_subreddits()


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    collector = RedditCollector()
    if collector.test_connection():
        articles = collector.collect_from_subreddit('MachineLearning', limit=5)
        print(f"수집된 글 수: {len(articles)}")
        
        for article in articles[:3]:
            print(f"- {article['title'][:100]}... (점수: {article['score']:.2f})")
    else:
        print("Reddit API 연결 실패")
