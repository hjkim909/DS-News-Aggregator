#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Medium Collector
Medium 계열 플랫폼에서 RSS 피드를 통해 데이터 수집
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

class MediumCollector:
    """Medium 계열 수집기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        Medium 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.content_filter = ContentFilter(config)
        
        # 요청 헤더 (Medium은 봇 차단이 있어서 실제 브라우저 흉내)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # 세션 생성
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 날짜 필터링 설정
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.MAX_ARTICLE_AGE_DAYS)
        
        # Medium 특화 키워드 (데이터 사이언스, ML, AI 중심)
        self.medium_keywords = [
            # AI/ML 핵심
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'data science', 'data analysis',
            'natural language processing', 'computer vision', 'reinforcement learning',
            
            # 최신 트렌드
            'llm', 'large language model', 'gpt', 'bert', 'transformer',
            'chatgpt', 'openai', 'generative ai', 'stable diffusion',
            
            # 기술 스택
            'python', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'numpy', 'jupyter', 'keras', 'hugging face',
            
            # 데이터 관련
            'big data', 'data engineering', 'data visualization', 'analytics',
            'time series', 'predictive modeling', 'feature engineering',
            
            # 응용 분야
            'recommendation system', 'fraud detection', 'image recognition',
            'speech recognition', 'autonomous', 'fintech', 'biotech'
        ]
    
    def _fetch_medium_rss(self, rss_url: str, source_name: str) -> Optional[Any]:
        """Medium RSS 피드를 가져옴 (특별 처리)"""
        try:
            logger.info(f"{source_name} Medium RSS 피드 파싱 시작: {rss_url}")
            
            # Medium RSS는 때때로 User-Agent가 중요함
            response = self.session.get(rss_url, timeout=15)
            response.raise_for_status()
            
            # feedparser로 파싱
            feed = feedparser.parse(response.text)
            
            if feed.bozo:
                logger.warning(f"{source_name} RSS 피드 파싱 경고: {feed.bozo_exception}")
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                logger.warning(f"{source_name}에서 글을 찾을 수 없습니다.")
                return None
            
            logger.info(f"{source_name}에서 {len(feed.entries)}개 글 발견")
            return feed
            
        except Exception as e:
            logger.error(f"{source_name} RSS 피드 파싱 실패: {e}")
            return None
    
    def _extract_medium_content(self, url: str) -> str:
        """Medium 글에서 본문 추출 (Medium 특화)"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Medium 특화 본문 선택자
            medium_selectors = [
                'article',
                '[data-testid="storyContent"]',
                '.postArticle-content',
                '.section-content',
                '.graf',  # Medium의 문단 클래스
                '[data-selectable-paragraph]'
            ]
            
            content_parts = []
            
            for selector in medium_selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        # Medium 특화 정리
                        for unwanted in elem(['script', 'style', 'figure', 'figcaption', 'nav', 'footer']):
                            unwanted.decompose()
                        
                        text = elem.get_text(separator=' ', strip=True)
                        if text and len(text) > 50:
                            content_parts.append(text)
                    
                    if content_parts:
                        break
            
            # 텍스트 정리
            if content_parts:
                content_text = ' '.join(content_parts)
                content_text = re.sub(r'\s+', ' ', content_text).strip()
                
                # Medium은 보통 긴 글이므로 더 많이 허용
                return content_text[:3000] if len(content_text) > 3000 else content_text
            
            return ""
            
        except Exception as e:
            logger.warning(f"Medium URL에서 본문 추출 실패 {url}: {e}")
            return ""
    
    def _extract_medium_tags(self, title: str, content: str, source_id: str) -> List[str]:
        """Medium 글에서 태그 추출"""
        tags = set()
        text = (title + " " + content).lower()
        
        # AI/ML 전문 태그
        ai_ml_tags = {
            'artificial intelligence': 'AI',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'neural network': 'Neural Networks',
            'data science': 'Data Science',
            'natural language processing': 'NLP',
            'computer vision': 'Computer Vision',
            'reinforcement learning': 'Reinforcement Learning',
            'time series': 'Time Series',
            'generative ai': 'Generative AI',
            'large language model': 'LLM',
            'transformer': 'Transformers'
        }
        
        for keyword, tag in ai_ml_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 최신 AI 모델/도구
        model_tags = {
            'gpt': 'GPT', 'chatgpt': 'ChatGPT', 'bert': 'BERT',
            'llama': 'LLaMA', 'stable diffusion': 'Stable Diffusion',
            'midjourney': 'Midjourney', 'openai': 'OpenAI',
            'anthropic': 'Anthropic', 'claude': 'Claude'
        }
        
        for keyword, tag in model_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 기술 스택
        tech_stack_tags = {
            'python': 'Python', 'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'scikit-learn': 'Scikit-learn', 'pandas': 'Pandas', 'numpy': 'NumPy',
            'jupyter': 'Jupyter', 'keras': 'Keras', 'hugging face': 'Hugging Face',
            'streamlit': 'Streamlit', 'plotly': 'Plotly', 'matplotlib': 'Matplotlib'
        }
        
        for keyword, tag in tech_stack_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # Medium 소스별 태그
        source_tags = {
            'towards_ds': 'Towards Data Science',
            'better_prog': 'Better Programming',
            'the_startup': 'The Startup'
        }
        
        if source_id in source_tags:
            tags.add(source_tags[source_id])
        
        return list(tags)
    
    def _calculate_medium_score(self, title: str, content: str, source_id: str) -> float:
        """Medium 글 특화 점수 계산"""
        score = self.content_filter.calculate_score(title, content, source_id)
        
        # Medium 특화 보너스
        text = (title + " " + content).lower()
        
        # 튜토리얼/가이드 보너스
        tutorial_keywords = ['tutorial', 'guide', 'how to', 'step by step', 'beginner', 'complete guide']
        for keyword in tutorial_keywords:
            if keyword in text:
                score += 10
                break
        
        # 실무 경험 보너스
        experience_keywords = ['production', 'real world', 'case study', 'lessons learned', 'best practices']
        for keyword in experience_keywords:
            if keyword in text:
                score += 15
                break
        
        # 최신 기술 보너스
        latest_tech = ['2024', '2023', 'latest', 'new', 'recent', 'state-of-the-art', 'cutting-edge']
        for keyword in latest_tech:
            if keyword in text:
                score += 5
                break
        
        return score
    
    def _has_medium_keywords(self, title: str, content: str) -> bool:
        """Medium 전용 키워드 필터링"""
        text = (title + " " + content).lower()
        
        # 핵심 키워드 매칭
        for keyword in self.medium_keywords:
            if keyword in text:
                return True
        
        # 패턴 기반 매칭
        patterns = [
            r'machine\s+learning', r'deep\s+learning', r'data\s+science',
            r'artificial\s+intelligence', r'neural\s+network', r'time\s+series',
            r'natural\s+language', r'computer\s+vision', r'large\s+language\s+model'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def collect_from_medium_source(self, source_config: Dict[str, str], limit: int = 8) -> List[Dict[str, Any]]:
        """Medium 소스에서 글 수집"""
        source_name = source_config['name']
        source_id = source_config['source_id']
        rss_url = source_config['rss']
        
        logger.info(f"{source_name}에서 글 수집 시작 (최대 {limit}개)")
        
        # RSS 피드 가져오기
        feed = self._fetch_medium_rss(rss_url, source_name)
        if not feed:
            return []
        
        articles = []
        processed_count = 0
        
        # Medium은 보통 고품질 글이 많으므로 더 많이 처리
        for entry in feed.entries[:limit * 3]:
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
                
                # Medium URL 정리 (파라미터 제거)
                if '?' in link:
                    link = link.split('?')[0]
                
                # 요약/내용 추출
                summary = entry.get('summary', '') or entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                
                if summary:
                    content = BeautifulSoup(summary, 'html.parser').get_text(strip=True)
                else:
                    content = ""
                
                # Medium은 RSS에 충분한 내용이 있으므로 웹 스크래핑은 선택적
                if len(content) < 500:  # 내용이 부족할 때만
                    web_content = self._extract_medium_content(link)
                    if web_content:
                        content = web_content
                
                # Medium 전용 키워드 필터링
                if not self._has_medium_keywords(title, content):
                    continue
                
                # 날짜 파싱
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
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
                tags = self._extract_medium_tags(title, content, source_id)
                
                # Medium 특화 점수 계산
                score = self._calculate_medium_score(title, content, source_id)
                
                # 작성자 정보 (가능하면)
                author = entry.get('author', 'Unknown')
                
                # 기사 데이터 구성
                article_data = {
                    'id': f"{source_id}_{int(time.time())}_{processed_count}",
                    'title': title,
                    'title_ko': title,  # 번역은 나중에
                    'content': content[:2500],  # Medium은 조금 더 길게
                    'content_ko': content[:2500],  # 번역은 나중에
                    'summary': '',  # 요약은 나중에
                    'url': link,
                    'source': source_id,
                    'tags': tags,
                    'score': score,
                    'published': published_time.isoformat(),
                    'author': author,
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
                
                if score > 0:  # 최소 점수 통과
                    articles.append(article_data)
                
                # 목표 개수 달성시 종료
                if len(articles) >= limit:
                    break
                
                # Medium API 제한 방지
                time.sleep(1)
                    
            except Exception as e:
                logger.error(f"{source_name} 글 처리 실패: {e}")
                continue
        
        logger.info(f"{source_name}에서 {len(articles)}개 글 수집 완료")
        return articles
    
    def collect_all_medium_sources(self) -> List[Dict[str, Any]]:
        """모든 Medium 소스에서 글 수집"""
        all_articles = []
        
        for source_config in self.config.MEDIUM_SOURCES:
            try:
                articles = self.collect_from_medium_source(
                    source_config, 
                    limit=max(2, self.config.MAX_ARTICLES_PER_SOURCE // len(self.config.MEDIUM_SOURCES))
                )
                all_articles.extend(articles)
                
                # Medium API 제한 방지를 위한 딜레이
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Medium 소스 {source_config['name']} 수집 실패: {e}")
                continue
        
        logger.info(f"Medium에서 총 {len(all_articles)}개 글 수집 완료")
        return all_articles


if __name__ == '__main__':
    # 수집기 테스트
    config = Config()
    collector = MediumCollector(config)
    
    print("🧪 Medium 수집기 테스트")
    print("="*50)
    
    # Towards Data Science 테스트
    test_source = {
        'name': 'Towards Data Science',
        'rss': 'https://towardsdatascience.com/feed',
        'source_id': 'towards_ds'
    }
    
    articles = collector.collect_from_medium_source(test_source, limit=3)
    print(f"\n수집된 글 수: {len(articles)}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   점수: {article['score']:.1f}")
        print(f"   태그: {', '.join(article['tags'])}")
        print(f"   작성자: {article.get('author', 'Unknown')}")
        print(f"   URL: {article['url']}")
    
    print(f"\n✅ Medium 수집기 테스트 완료")
