#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Korean Blog Collector
한국 기술 블로그에서 DS/ML 관련 글 수집
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time
import re
from urllib.parse import urljoin, urlparse
from config import Config

logger = logging.getLogger(__name__)

class KoreanBlogCollector:
    """한국 기술 블로그에서 DS/ML 관련 글을 수집하는 클래스"""
    
    def __init__(self, config: Config = None):
        """
        한국 블로그 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def _calculate_score(self, title: str, content: str = '', source_id: str = '') -> float:
        """
        사용자 요구사항에 맞는 점수 계산 시스템
        기본 50점 + 우선 키워드 +10~20점 + 소스 가중치 +30점 - 제외 패턴 -30점
        
        Args:
            title: 글 제목
            content: 글 내용
            source_id: 소스 ID (naver_d2, kakao_tech, ai_times)
            
        Returns:
            계산된 점수
        """
        try:
            title_lower = title.lower()
            content_lower = content.lower()
            full_text = title_lower + ' ' + content_lower
            
            # 기본 점수
            score = self.config.BASE_SCORE
            
            # 우선 키워드 점수 (+10~20점)
            for keyword, bonus in self.config.PRIORITY_KEYWORDS.items():
                if keyword.lower() in full_text:
                    score += bonus
                    logger.debug(f"우선 키워드 '{keyword}' 발견: +{bonus}점")
            
            # 소스 가중치 (기술블로그: +30점)
            score += self.config.SOURCE_WEIGHTS.get(source_id, 30)  # 기본값 30점
            
            # 제외 패턴 체크 (-30점)
            for pattern in self.config.EXCLUDE_PATTERNS:
                if pattern.lower() in full_text:
                    score -= 30
                    logger.debug(f"제외 패턴 '{pattern}' 발견: -30점")
            
            # DS/ML 키워드 추가 보너스
            ds_bonus = 0
            for keyword in self.config.DS_KEYWORDS:
                if keyword.lower() in full_text:
                    ds_bonus += 5
            score += min(ds_bonus, 15)  # 최대 15점 보너스
            
            # 품질 보너스
            if 10 <= len(title) <= 100:
                score += 5
            
            if len(content) > 300:
                score += 5
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"점수 계산 실패: {e}")
            return 0.0
    
    def _extract_tags(self, text: str) -> List[str]:
        """
        텍스트에서 태그 추출 (한국어 포함)
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 태그 리스트
        """
        try:
            tags = []
            text_lower = text.lower()
            
            # 한국어/영어 태그 키워드 맵핑
            tag_keywords = {
                'LLM': ['llm', 'large language model', 'gpt', 'bert', 'transformer', '대형언어모델'],
                '시계열': ['time series', 'timeseries', 'temporal', 'forecasting', '시계열', '예측'],
                '머신러닝': ['machine learning', 'ml', 'supervised', 'unsupervised', '머신러닝', '기계학습'],
                '딥러닝': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm', '딥러닝', '신경망'],
                '데이터분석': ['data analysis', 'analytics', 'visualization', '데이터분석', '데이터시각화'],
                '통계': ['statistics', 'statistical', 'regression', '통계', '통계학', '회귀'],
                '자연어처리': ['nlp', 'natural language processing', 'text mining', '자연어처리', '텍스트마이닝'],
                '컴퓨터비전': ['computer vision', 'cv', 'image', 'opencv', '컴퓨터비전', '이미지처리'],
                'Python': ['python', 'pandas', 'numpy', 'scikit-learn', '파이썬'],
                'AI': ['artificial intelligence', 'ai', '인공지능', 'AI'],
                '클라우드': ['cloud', 'aws', 'azure', 'gcp', '클라우드'],
                '빅데이터': ['big data', 'bigdata', '빅데이터', '대용량데이터']
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
    
    def _extract_content_from_url(self, url: str) -> str:
        """
        URL에서 본문 내용 추출
        
        Args:
            url: 글 URL
            
        Returns:
            추출된 본문 내용
        """
        try:
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 사이트별 본문 추출 로직
            content = ''
            
            # 공통 본문 태그 시도
            content_selectors = [
                'article', '.post-content', '.entry-content', 
                '.content', '.post-body', 'main',
                '[role="main"]', '.markdown-body'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join(elem.get_text(strip=True) for elem in elements)
                    break
            
            # 본문이 없으면 p 태그들 수집
            if not content:
                p_tags = soup.find_all('p')
                content = ' '.join(p.get_text(strip=True) for p in p_tags)
            
            # 내용 정리
            content = re.sub(r'\s+', ' ', content).strip()
            return content[:2000]  # 처음 2000자만
            
        except Exception as e:
            logger.error(f"본문 추출 실패 ({url}): {e}")
            return ''
    
    def _parse_rss_feed(self, rss_url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        RSS 피드 파싱
        
        Args:
            rss_url: RSS 피드 URL
            source_name: 소스 이름
            
        Returns:
            파싱된 글 목록
        """
        try:
            logger.info(f"{source_name} RSS 피드 파싱 시작: {rss_url}")
            
            # feedparser 사용
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"{source_name} RSS 피드 파싱 경고: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries[:self.config.MAX_ARTICLES_PER_SOURCE]:
                try:
                    # 날짜 파싱
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    else:
                        published = datetime.now(timezone.utc)
                    
                    # 본문 추출
                    content = ''
                    if hasattr(entry, 'summary'):
                        content = BeautifulSoup(entry.summary, 'html.parser').get_text()
                    elif hasattr(entry, 'content'):
                        content = BeautifulSoup(entry.content[0].value, 'html.parser').get_text()
                    
                    # URL 정규화
                    url = entry.link
                    if not url.startswith('http'):
                        url = urljoin(rss_url, url)
                    
                    data = {
                        'id': f"{source.get('source_id', 'blog')}_{hash(url)}",
                        'title': entry.title,
                        'title_ko': entry.title,  # 이미 한국어
                        'content': content,
                        'content_ko': content,  # 이미 한국어
                        'summary': '',  # 요약 후 채워짐
                        'url': url,
                        'source': source.get('source_id', 'korean_blog'),  # naver_d2, kakao_tech, ai_times
                        'tags': self._extract_tags(entry.title + ' ' + content),
                        'score': self._calculate_score(entry.title, content, source.get('source_id')),
                        'published': published.isoformat(),
                        # 추가 메타데이터
                        'author': getattr(entry, 'author', ''),
                        'language': 'ko',
                        'needs_translation': False,
                        'collected_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    if data['score'] > 0:
                        articles.append(data)
                    
                    time.sleep(0.5)  # 요청 간격
                    
                except Exception as e:
                    logger.error(f"RSS 엔트리 처리 실패: {e}")
                    continue
            
            logger.info(f"{source_name}에서 {len(articles)}개 글 수집 완료")
            return articles
            
        except Exception as e:
            logger.error(f"{source_name} RSS 수집 실패: {e}")
            return []
    
    def _scrape_website(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        웹사이트 직접 스크래핑 (RSS가 없는 경우)
        
        Args:
            source: 소스 정보
            
        Returns:
            스크래핑된 글 목록
        """
        try:
            url = source['url']
            source_name = source['name']
            
            logger.info(f"{source_name} 웹사이트 스크래핑 시작: {url}")
            
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # 사이트별 맞춤 스크래핑 로직
            if 'samsungsds.com' in url:
                articles = self._scrape_samsung_sds(soup, source_name, url)
            else:
                # 일반적인 스크래핑 로직
                articles = self._generic_scrape(soup, source_name, url)
            
            logger.info(f"{source_name}에서 {len(articles)}개 글 수집 완료")
            return articles
            
        except Exception as e:
            logger.error(f"{source_name} 스크래핑 실패: {e}")
            return []
    
    def _scrape_samsung_sds(self, soup: BeautifulSoup, source_name: str, base_url: str) -> List[Dict[str, Any]]:
        """삼성SDS 인사이트 페이지 스크래핑"""
        articles = []
        
        try:
            # 삼성SDS 특화 셀렉터 (실제 사이트 구조에 따라 조정 필요)
            article_elements = soup.select('.insight-item, .post-item, .card-item')
            
            for element in article_elements[:self.config.MAX_ARTICLES_PER_SOURCE]:
                try:
                    title_elem = element.select_one('h3 a, .title a, a.title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    
                    if not href.startswith('http'):
                        href = urljoin(base_url, href)
                    
                    # 간단한 본문 추출
                    content = ''
                    content_elem = element.select_one('.summary, .excerpt, .description')
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                    
                    data = {
                        'id': f"korean_blog_{hash(href)}",
                        'title': title,
                        'content': content,
                        'url': href,
                        'original_url': href,
                        'source': source_name,
                        'source_type': 'korean_blog',
                        'author': '',
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'language': 'ko',
                        'needs_translation': False,
                        'quality_score': self._calculate_score(title, content),
                        'collected_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    if data['quality_score'] > 0:
                        articles.append(data)
                
                except Exception as e:
                    logger.error(f"삼성SDS 글 처리 실패: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"삼성SDS 스크래핑 실패: {e}")
        
        return articles
    
    def _generic_scrape(self, soup: BeautifulSoup, source_name: str, base_url: str) -> List[Dict[str, Any]]:
        """일반적인 웹사이트 스크래핑"""
        articles = []
        
        try:
            # 일반적인 글 링크 셀렉터들
            selectors = [
                'article a', '.post a', '.entry a',
                '.blog-post a', '.news-item a', 'h2 a', 'h3 a',
                '.title a', '.headline a'
            ]
            
            links = []
            for selector in selectors:
                links.extend(soup.select(selector))
                if len(links) >= self.config.MAX_ARTICLES_PER_SOURCE * 2:
                    break
            
            seen_urls = set()
            
            for link in links[:self.config.MAX_ARTICLES_PER_SOURCE * 2]:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if not title or not href or len(title) < 5:
                        continue
                    
                    if not href.startswith('http'):
                        href = urljoin(base_url, href)
                    
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    
                    # 간단한 품질 필터
                    quality_score = self._calculate_score(title)
                    if quality_score <= 0:
                        continue
                    
                    data = {
                        'id': f"korean_blog_{hash(href)}",
                        'title': title,
                        'content': '',  # 나중에 필요시 추출
                        'url': href,
                        'original_url': href,
                        'source': source_name,
                        'source_type': 'korean_blog',
                        'author': '',
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'language': 'ko',
                        'needs_translation': False,
                        'quality_score': quality_score,
                        'collected_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    articles.append(data)
                    
                    if len(articles) >= self.config.MAX_ARTICLES_PER_SOURCE:
                        break
                
                except Exception as e:
                    logger.error(f"링크 처리 실패: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"일반 스크래핑 실패: {e}")
        
        return articles
    
    def collect_from_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        특정 소스에서 글 수집
        
        Args:
            source: 소스 정보 (name, url, rss)
            
        Returns:
            수집된 글 목록
        """
        source_name = source['name']
        rss_url = source.get('rss')
        
        try:
            if rss_url:
                # RSS 피드 우선 시도
                articles = self._parse_rss_feed(rss_url, source_name)
            else:
                # RSS가 없으면 웹 스크래핑
                articles = self._scrape_website(source)
            
            # 품질 점수로 정렬
            articles.sort(key=lambda x: x['quality_score'], reverse=True)
            
            return articles
            
        except Exception as e:
            logger.error(f"{source_name} 수집 실패: {e}")
            return []
    
    def collect_all_sources(self) -> List[Dict[str, Any]]:
        """
        모든 한국 블로그 소스에서 글 수집
        
        Returns:
            모든 소스에서 수집된 글 목록
        """
        all_articles = []
        
        for source in self.config.KOREAN_BLOG_SOURCES:
            try:
                articles = self.collect_from_source(source)
                all_articles.extend(articles)
                
                # 요청 간격
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"소스 {source['name']} 수집 중 오류: {e}")
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
        unique_articles.sort(key=lambda x: x['quality_score'], reverse=True)
        
        logger.info(f"한국 블로그에서 총 {len(unique_articles)}개 유니크 글 수집 완료")
        return unique_articles


# 유틸리티 함수
def collect_korean_blog_articles(config: Config = None) -> List[Dict[str, Any]]:
    """
    한국 기술 블로그에서 글 수집하는 편의 함수
    
    Args:
        config: 설정 객체
        
    Returns:
        수집된 글 목록
    """
    collector = KoreanBlogCollector(config)
    return collector.collect_all_sources()


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    collector = KoreanBlogCollector()
    
    # 테스트: 네이버 D2만 수집
    test_source = {
        'name': '네이버 D2',
        'url': 'https://d2.naver.com/news',
        'rss': 'https://d2.naver.com/news.rss'
    }
    
    articles = collector.collect_from_source(test_source)
    print(f"수집된 글 수: {len(articles)}")
    
    for article in articles[:3]:
        print(f"- {article['title'][:50]}... (점수: {article['quality_score']:.2f})")
