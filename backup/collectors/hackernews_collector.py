#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Hacker News Collector
Hacker News API를 통해 데이터 수집
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import re

from config import Config
from collectors.content_filter import ContentFilter

logger = logging.getLogger(__name__)

class HackerNewsCollector:
    """Hacker News 수집기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        Hacker News 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.content_filter = ContentFilter(config)
        
        # Hacker News API 설정
        self.base_api_url = self.config.HACKER_NEWS_CONFIG['base_url']
        self.web_base_url = self.config.HACKER_NEWS_CONFIG['web_url']
        
        # 요청 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        
        # 세션 생성
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Hacker News에서 찾을 DS/ML 키워드
        self.hn_keywords = [
            # AI/ML 핵심
            'machine learning', 'ml', 'deep learning', 'neural network',
            'artificial intelligence', 'ai', 'data science', 'data analysis',
            
            # 최신 트렌드  
            'llm', 'gpt', 'chatgpt', 'openai', 'anthropic', 'claude',
            'transformer', 'bert', 'stable diffusion', 'generative ai',
            
            # 기술/도구
            'tensorflow', 'pytorch', 'scikit-learn', 'jupyter', 'pandas',
            'python data', 'r programming', 'kaggle', 'colab',
            
            # 응용분야
            'computer vision', 'nlp', 'natural language', 'recommendation',
            'time series', 'forecasting', 'autonomous', 'robotics',
            
            # 업계/회사
            'deepmind', 'google ai', 'facebook ai', 'microsoft ai',
            'nvidia', 'tesla', 'uber ai', 'netflix data'
        ]
    
    def _get_top_story_ids(self, story_type: str = 'topstories', limit: int = 100) -> List[int]:
        """상위 스토리 ID 목록 가져오기"""
        try:
            url = f"{self.base_api_url}/{story_type}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()
            return story_ids[:limit] if story_ids else []
            
        except Exception as e:
            logger.error(f"Hacker News {story_type} ID 목록 가져오기 실패: {e}")
            return []
    
    def _get_story_details(self, story_id: int) -> Optional[Dict[str, Any]]:
        """특정 스토리의 상세 정보 가져오기"""
        try:
            url = f"{self.base_api_url}/item/{story_id}.json"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            story_data = response.json()
            
            # 기본 검증
            if not story_data or story_data.get('type') != 'story':
                return None
            
            if story_data.get('deleted') or story_data.get('dead'):
                return None
                
            return story_data
            
        except Exception as e:
            logger.warning(f"스토리 ID {story_id} 상세 정보 가져오기 실패: {e}")
            return None
    
    def _extract_content_from_url(self, url: str) -> str:
        """링크된 웹페이지에서 본문 추출"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출 선택자
            content_selectors = [
                'article', 'main', '[role="main"]',
                '.content', '.post-content', '.entry-content',
                '.article-content', '#content', '.post-body'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        # 불필요한 태그 제거
                        for unwanted in elem(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                            unwanted.decompose()
                        
                        text = elem.get_text(separator=' ', strip=True)
                        if text and len(text) > 100:
                            content_text = text
                            break
                    if content_text:
                        break
            
            # 백업: body에서 추출
            if not content_text:
                body = soup.find('body')
                if body:
                    for tag in body(['script', 'style', 'nav', 'footer', 'header']):
                        tag.decompose()
                    content_text = body.get_text(separator=' ', strip=True)
            
            # 텍스트 정리
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            
            # 최대 1500자로 제한 (Hacker News는 보통 짧은 글 위주)
            return content_text[:1500] if len(content_text) > 1500 else content_text
            
        except Exception as e:
            logger.warning(f"URL에서 본문 추출 실패 {url}: {e}")
            return ""
    
    def _extract_hn_tags(self, title: str, content: str, url: str = "") -> List[str]:
        """Hacker News 글에서 태그 추출"""
        tags = set(['Hacker News'])  # 기본 태그
        text = (title + " " + content + " " + url).lower()
        
        # AI/ML 관련 태그
        ai_tags = {
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning', 
            'artificial intelligence': 'AI',
            'data science': 'Data Science',
            'neural network': 'Neural Networks',
            'computer vision': 'Computer Vision',
            'natural language': 'NLP',
            'time series': 'Time Series'
        }
        
        for keyword, tag in ai_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 최신 AI 모델/서비스
        model_tags = {
            'gpt': 'GPT', 'chatgpt': 'ChatGPT', 'openai': 'OpenAI',
            'claude': 'Claude', 'anthropic': 'Anthropic',
            'llm': 'LLM', 'transformer': 'Transformers',
            'stable diffusion': 'Stable Diffusion',
            'midjourney': 'Midjourney'
        }
        
        for keyword, tag in model_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 기술 회사
        company_tags = {
            'google': 'Google', 'deepmind': 'DeepMind',
            'microsoft': 'Microsoft', 'facebook': 'Meta', 'meta': 'Meta',
            'apple': 'Apple', 'nvidia': 'NVIDIA', 'tesla': 'Tesla',
            'uber': 'Uber', 'netflix': 'Netflix'
        }
        
        for keyword, tag in company_tags.items():
            if keyword in text:
                tags.add(tag)
        
        # 기술 스택
        tech_tags = {
            'python': 'Python', 'javascript': 'JavaScript', 'rust': 'Rust',
            'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
            'docker': 'Docker', 'kubernetes': 'Kubernetes'
        }
        
        for keyword, tag in tech_tags.items():
            if keyword in text:
                tags.add(tag)
        
        return list(tags)
    
    def _calculate_hn_score(self, title: str, content: str, score: int, comments: int, url: str = "") -> float:
        """Hacker News 글 특화 점수 계산"""
        base_score = self.content_filter.calculate_score(title, content, 'hackernews')
        
        # Hacker News 특화 보너스
        
        # 점수(업보트) 보너스: 높은 점수일수록 품질이 좋음
        if score >= 100:
            base_score += 20
        elif score >= 50:
            base_score += 15
        elif score >= 20:
            base_score += 10
        elif score >= 10:
            base_score += 5
        
        # 댓글 수 보너스: 활발한 토론이 있는 글
        if comments >= 50:
            base_score += 15
        elif comments >= 20:
            base_score += 10
        elif comments >= 10:
            base_score += 5
        
        text = (title + " " + content + " " + url).lower()
        
        # 특별 도메인 보너스
        premium_domains = [
            'arxiv.org', 'nature.com', 'science.org', 'ieee.org',
            'acm.org', 'mit.edu', 'stanford.edu', 'berkeley.edu',
            'deepmind.com', 'openai.com', 'anthropic.com',
            'blog.google', 'research.google', 'ai.googleblog.com'
        ]
        
        for domain in premium_domains:
            if domain in url:
                base_score += 15
                break
        
        # 연구/논문 키워드 보너스
        research_keywords = ['paper', 'research', 'study', 'analysis', 'arxiv', 'doi']
        for keyword in research_keywords:
            if keyword in text:
                base_score += 10
                break
        
        return base_score
    
    def _has_hn_keywords(self, title: str, content: str, url: str = "") -> bool:
        """Hacker News DS/ML 키워드 필터링"""
        text = (title + " " + content + " " + url).lower()
        
        # 키워드 매칭
        for keyword in self.hn_keywords:
            if keyword in text:
                return True
        
        # URL 기반 매칭 (특별 도메인)
        ai_domains = [
            'arxiv.org', 'ai.googleblog.com', 'openai.com', 'deepmind.com',
            'research.google', 'ai.facebook.com', 'microsoft.com/ai',
            'nvidia.com/ai', 'anthropic.com'
        ]
        
        for domain in ai_domains:
            if domain in url:
                return True
        
        return False
    
    def collect_from_hackernews(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Hacker News에서 글 수집"""
        logger.info(f"Hacker News에서 글 수집 시작 (최대 {limit}개)")
        
        # 1. 상위 스토리 ID 가져오기 (더 많이 가져와서 필터링)
        story_ids = self._get_top_story_ids('topstories', limit * 10)
        if not story_ids:
            logger.warning("Hacker News 스토리 ID를 가져올 수 없습니다.")
            return []
        
        articles = []
        processed_count = 0
        
        for story_id in story_ids:
            try:
                processed_count += 1
                
                # 2. 스토리 상세 정보 가져오기
                story_data = self._get_story_details(story_id)
                if not story_data:
                    continue
                
                # 기본 정보 추출
                title = story_data.get('title', '').strip()
                if not title:
                    continue
                
                url = story_data.get('url', '')
                hn_score = story_data.get('score', 0)
                comments_count = story_data.get('descendants', 0)
                timestamp = story_data.get('time', time.time())
                author = story_data.get('by', 'anonymous')
                
                # 본문이 있는 경우 (Ask HN, Show HN 등)
                text_content = story_data.get('text', '')
                if text_content:
                    # HTML 태그 제거
                    content = BeautifulSoup(text_content, 'html.parser').get_text(strip=True)
                else:
                    content = ""
                
                # 외부 링크가 있으면 본문 추출 시도
                if url and not content:
                    web_content = self._extract_content_from_url(url)
                    if web_content:
                        content = web_content
                
                # DS/ML 키워드 필터링
                if not self._has_hn_keywords(title, content, url):
                    continue
                
                # 최소 품질 필터링 (점수가 너무 낮으면 제외)
                if hn_score < 5:
                    continue
                
                # 날짜 변환
                published_time = datetime.fromtimestamp(timestamp, timezone.utc)
                
                # 태그 추출
                tags = self._extract_hn_tags(title, content, url)
                
                # 점수 계산
                final_score = self._calculate_hn_score(title, content, hn_score, comments_count, url)
                
                # HN 웹 URL 생성
                hn_url = f"{self.web_base_url}/item?id={story_id}"
                
                # 기사 데이터 구성
                article_data = {
                    'id': f"hackernews_{story_id}_{int(time.time())}",
                    'title': title,
                    'title_ko': title,  # 번역은 나중에
                    'content': content[:1500] if content else title,  # HN은 보통 짧음
                    'content_ko': content[:1500] if content else title,  # 번역은 나중에
                    'summary': '',  # 요약은 나중에
                    'url': url if url else hn_url,  # 원본 링크 또는 HN 링크
                    'hn_url': hn_url,  # HN 토론 링크
                    'source': 'hackernews',
                    'tags': tags,
                    'score': final_score,
                    'hn_score': hn_score,  # 원래 HN 점수
                    'comments': comments_count,
                    'published': published_time.isoformat(),
                    'author': author,
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
                
                if final_score > 0:  # 최소 점수 통과
                    articles.append(article_data)
                
                # 목표 개수 달성시 종료
                if len(articles) >= limit:
                    break
                
                # API 제한 방지
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Hacker News 스토리 {story_id} 처리 실패: {e}")
                continue
        
        logger.info(f"Hacker News에서 {len(articles)}개 글 수집 완료")
        return articles


if __name__ == '__main__':
    # 수집기 테스트
    config = Config()
    collector = HackerNewsCollector(config)
    
    print("🧪 Hacker News 수집기 테스트")
    print("="*50)
    
    articles = collector.collect_from_hackernews(limit=5)
    print(f"\n수집된 글 수: {len(articles)}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   최종 점수: {article['score']:.1f}")
        print(f"   HN 점수: {article['hn_score']} | 댓글: {article['comments']}개")
        print(f"   태그: {', '.join(article['tags'])}")
        print(f"   작성자: {article['author']}")
        print(f"   URL: {article['url']}")
        print(f"   HN 토론: {article['hn_url']}")
    
    print(f"\n✅ Hacker News 수집기 테스트 완료")
