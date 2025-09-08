#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Tech Blog Collector
글로벌 기술 블로그에서 RSS 피드를 통해 데이터 수집
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import requests
import feedparser
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

from config import Config
from collectors.content_filter import ContentFilter

logger = logging.getLogger(__name__)

class TechBlogCollector:
    """기술 블로그 수집기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        기술 블로그 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.content_filter = ContentFilter(config)
        
        # 요청 헤더 (봇 차단 방지)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 세션 생성 (연결 재사용)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 날짜 필터링 설정
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.MAX_ARTICLE_AGE_DAYS)
        
        # DS/ML 관련 키워드 (영어 + 한국어)
        self.ds_keywords = self.config.DS_KEYWORDS + self.config.TECH_KEYWORDS + [
            'transformer', 'bert', 'gpt', 'llm', 'nlp', 'cv', 'ai', 'ml',
            '딥러닝', 'AI', 'ML', '인공지능', '머신러닝', 'NLP', 'CV'
        ]
    
    def _fetch_rss_feed(self, rss_url: str, source_name: str) -> Optional[Any]:
        """RSS 피드를 가져옴"""
        try:
            logger.info(f"{source_name} RSS 피드 파싱 시작: {rss_url}")
            
            # feedparser는 자체적으로 HTTP 요청을 처리하므로 직접 사용
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"{source_name} RSS 피드 파싱 경고: {feed.bozo_exception}")
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                logger.warning(f"{source_name}에서 글을 찾을 수 없습니다.")
                return None
            
            return feed
            
        except Exception as e:
            logger.error(f"{source_name} RSS 피드 파싱 실패: {e}")
            return None
    
    def _extract_content_from_url(self, url: str) -> str:
        """웹페이지에서 본문 내용 추출"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 다양한 본문 선택자 시도
            content_selectors = [
                'article',
                '[role="main"]',
                '.post-content',
                '.entry-content', 
                '.article-content',
                '.content',
                'main',
                '.post-body',
                '#content'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # 텍스트 추출 및 정리
                    text_parts = []
                    for elem in elements:
                        # 스크립트, 스타일 태그 제거
                        for script in elem(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        text = elem.get_text(separator=' ', strip=True)
                        if text and len(text) > 100:  # 의미있는 텍스트만
                            text_parts.append(text)
                    
                    content_text = ' '.join(text_parts)
                    break
            
            # 백업: 전체 body에서 텍스트 추출
            if not content_text:
                body = soup.find('body')
                if body:
                    # 불필요한 태그 제거
                    for tag in body(["script", "style", "nav", "footer", "header", "aside"]):
                        tag.decompose()
                    content_text = body.get_text(separator=' ', strip=True)
            
            # 텍스트 정리
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            
            # 너무 짧으면 제목+요약으로 대체
            if len(content_text) < 200:
                return ""
            
            # 최대 2000자로 제한
            return content_text[:2000] if len(content_text) > 2000 else content_text
            
        except Exception as e:
            logger.warning(f"URL에서 본문 추출 실패 {url}: {e}")
            return ""
    
    def _extract_tags(self, title: str, content: str, source_id: str) -> List[str]:
        """제목과 내용에서 태그 추출"""
        tags = set()
        text = (title + " " + content).lower()
        
        # AI/ML 관련 태그
        ml_tags = {
            'machine learning': 'ML', 'ml': 'ML', '머신러닝': 'ML',
            'deep learning': 'Deep Learning', '딥러닝': 'Deep Learning',
            'neural network': 'Neural Network', '신경망': 'Neural Network',
            'artificial intelligence': 'AI', 'ai': 'AI', '인공지능': 'AI',
            'data science': 'Data Science', '데이터사이언스': 'Data Science',
            'natural language processing': 'NLP', 'nlp': 'NLP', '자연어처리': 'NLP',
            'computer vision': 'Computer Vision', 'cv': 'Computer Vision', '컴퓨터비전': 'Computer Vision',
            'reinforcement learning': 'Reinforcement Learning', '강화학습': 'Reinforcement Learning',
            'time series': 'Time Series', '시계열': 'Time Series',
            'llm': 'LLM', 'large language model': 'LLM', '대형언어모델': 'LLM',
            'transformer': 'Transformer', 'bert': 'BERT', 'gpt': 'GPT'
        }
        
        for keyword, tag in ml_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 기술 스택 태그
        tech_tags = {
            'python': 'Python', 'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'keras': 'Keras', 'scikit-learn': 'Scikit-learn', 'pandas': 'Pandas',
            'numpy': 'NumPy', 'jupyter': 'Jupyter', 'docker': 'Docker',
            'kubernetes': 'Kubernetes', 'aws': 'AWS', 'cloud': 'Cloud',
            'api': 'API', 'rest': 'REST', 'graphql': 'GraphQL'
        }
        
        for keyword, tag in tech_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 소스별 태그
        source_tags = {
            'google_ai': 'Google AI',
            'openai': 'OpenAI', 
            'netflix_tech': 'Netflix',
            'uber_eng': 'Uber',
            'naver_d2': '네이버',
            'kakao_tech': '카카오'
        }
        
        if source_id in source_tags:
            tags.add(source_tags[source_id])
        
        return list(tags)
    
    def _calculate_score(self, title: str, content: str, source_id: str) -> float:
        """글 점수 계산"""
        return self.content_filter.calculate_score(title, content, source_id)
    
    def _has_ds_keywords(self, title: str, content: str) -> bool:
        """DS/ML 관련 키워드가 포함되어 있는지 확인"""
        text = (title + " " + content).lower()
        
        # 키워드 매칭 (더 유연하게)
        for keyword in self.ds_keywords:
            if keyword.lower() in text:
                return True
        
        # 패턴 매칭
        patterns = [
            r'machine\s+learning', r'deep\s+learning', r'neural\s+network',
            r'data\s+science', r'artificial\s+intelligence',
            r'time\s+series', r'computer\s+vision',
            r'natural\s+language', r'reinforcement\s+learning'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def collect_from_source(self, source_config: Dict[str, str], limit: int = 10) -> List[Dict[str, Any]]:
        """특정 소스에서 글 수집"""
        source_name = source_config['name']
        source_id = source_config['source_id']
        rss_url = source_config['rss']
        
        logger.info(f"{source_name}에서 글 수집 시작 (최대 {limit}개)")
        
        # RSS 피드 가져오기
        feed = self._fetch_rss_feed(rss_url, source_name)
        if not feed:
            return []
        
        articles = []
        processed_count = 0
        
        for entry in feed.entries[:limit * 2]:  # 여분으로 더 많이 처리
            try:
                processed_count += 1
                
                # 기본 정보 추출
                title = entry.get('title', '').strip()
                if not title:
                    continue
                
                # URL 정리
                link = entry.get('link', '')
                if not link:
                    continue
                
                # 요약/내용 추출
                summary = entry.get('summary', '') or entry.get('description', '')
                
                # 본문 내용 가져오기 (선택적)
                content = ""
                if summary:
                    content = BeautifulSoup(summary, 'html.parser').get_text(strip=True)
                
                # 추가 본문이 필요한 경우 웹페이지에서 추출
                if len(content) < 300:
                    web_content = self._extract_content_from_url(link)
                    if web_content:
                        content = web_content
                    elif summary:
                        content = BeautifulSoup(summary, 'html.parser').get_text(strip=True)
                
                # DS/ML 키워드 필터링
                if not self._has_ds_keywords(title, content):
                    continue
                
                # 날짜 파싱
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                else:
                    published_time = datetime.now(timezone.utc)
                
                # 날짜 필터링 (사용자 요구사항: 최근 1~2달)
                if published_time.year < self.config.MIN_PUBLISH_YEAR:
                    logger.debug(f"{published_time.year}년 기사 제외: {title[:50]}")
                    continue
                    
                article_age_days = (datetime.now(timezone.utc) - published_time).days
                if article_age_days > self.config.MAX_ARTICLE_AGE_DAYS:
                    logger.debug(f"{article_age_days}일 전 기사 제외: {title[:50]}")
                    continue
                
                # 태그 추출
                tags = self._extract_tags(title, content, source_id)
                
                # 점수 계산
                score = self._calculate_score(title, content, source_id)
                
                # 기사 데이터 구성
                article_data = {
                    'id': f"{source_id}_{int(time.time())}_{processed_count}",
                    'title': title,
                    'title_ko': title,  # 번역은 나중에
                    'content': content[:2000],  # 최대 2000자
                    'content_ko': content[:2000],  # 번역은 나중에
                    'summary': '',  # 요약은 나중에
                    'url': link,
                    'source': source_id,
                    'tags': tags,
                    'score': score,
                    'published': published_time.isoformat(),
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
                
                if score > 0:  # 최소 점수 통과
                    articles.append(article_data)
                
                # 목표 개수 달성시 종료
                if len(articles) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"{source_name} 글 처리 실패: {e}")
                continue
        
        logger.info(f"{source_name}에서 {len(articles)}개 글 수집 완료")
        return articles
    
    def collect_all_sources(self) -> List[Dict[str, Any]]:
        """모든 기술 블로그 소스에서 글 수집"""
        all_articles = []
        
        for source_config in self.config.TECH_BLOG_SOURCES:
            try:
                articles = self.collect_from_source(
                    source_config, 
                    limit=self.config.MAX_ARTICLES_PER_SOURCE // len(self.config.TECH_BLOG_SOURCES)
                )
                all_articles.extend(articles)
                
                # API 제한 방지를 위한 딜레이
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"소스 {source_config['name']} 수집 실패: {e}")
                continue
        
        logger.info(f"기술 블로그에서 총 {len(all_articles)}개 글 수집 완료")
        return all_articles


if __name__ == '__main__':
    # 수집기 테스트
    config = Config()
    collector = TechBlogCollector(config)
    
    print("🧪 기술 블로그 수집기 테스트")
    print("="*50)
    
    # 단일 소스 테스트
    test_source = {
        'name': 'Google AI Blog',
        'rss': 'https://ai.googleblog.com/feeds/posts/default',
        'source_id': 'google_ai'
    }
    
    articles = collector.collect_from_source(test_source, limit=3)
    print(f"\n수집된 글 수: {len(articles)}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   점수: {article['score']:.1f}")
        print(f"   태그: {', '.join(article['tags'])}")
        print(f"   URL: {article['url']}")
    
    print(f"\n✅ 기술 블로그 수집기 테스트 완료")
