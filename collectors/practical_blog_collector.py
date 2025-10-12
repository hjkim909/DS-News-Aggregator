#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Practical Blog Collector
실용 블로그/꿀팁 플랫폼에서 RSS 피드를 통해 데이터 수집
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

class PracticalBlogCollector:
    """실용 블로그 수집기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        실용 블로그 수집기 초기화
        
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
        
        # 날짜 필터링 설정 (최근 60일)
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
        
        # 실용 블로그 소스 설정 (PRD v2.0 기준)
        self.blog_sources = {
            "towards_data_science": {
                "name": "Towards Data Science",
                "url": "https://towardsdatascience.com/feed",
                "score_bonus": 80,
                "tags": ["블로그", "튜토리얼", "실용"],
                "language": "en",
                "clap_filter": True  # Medium claps 필터링
            },
            "analytics_vidhya": {
                "name": "Analytics Vidhya",
                "url": "https://www.analyticsvidhya.com/blog/feed/",
                "score_bonus": 75,
                "tags": ["블로그", "실습", "교육"],
                "language": "en",
                "clap_filter": False
            },
            "kdnuggets": {
                "name": "KDnuggets",
                "url": "https://www.kdnuggets.com/feed",
                "score_bonus": 75,
                "tags": ["블로그", "리소스", "뉴스"],
                "language": "en",
                "clap_filter": False
            },
            "neptune_ai": {
                "name": "Neptune.ai Blog",
                "url": "https://neptune.ai/blog/rss.xml",
                "score_bonus": 80,
                "tags": ["블로그", "MLOps", "꿀팁"],
                "language": "en",
                "clap_filter": False
            }
        }
    
    def _fetch_rss_feed(self, rss_url: str, source_name: str) -> Optional[Any]:
        """
        RSS 피드 가져오기
        
        Args:
            rss_url: RSS 피드 URL
            source_name: 소스명 (로깅용)
            
        Returns:
            feedparser 결과 객체 또는 None
        """
        try:
            logger.info(f"{source_name}에서 RSS 피드 가져오는 중: {rss_url}")
            
            # 타임아웃과 재시도 설정
            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()
            
            # feedparser로 파싱
            feed = feedparser.parse(response.content)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.warning(f"{source_name} RSS 파싱 경고: {feed.bozo_exception}")
                
            logger.info(f"{source_name}에서 {len(feed.entries)}개 항목 발견")
            return feed
            
        except requests.exceptions.RequestException as e:
            logger.error(f"{source_name} RSS 가져오기 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"{source_name} RSS 처리 중 오류: {e}")
            return None
    
    def _extract_content(self, entry: Any, source_config: Dict) -> str:
        """
        RSS 항목에서 본문 내용 추출
        
        Args:
            entry: feedparser 항목
            source_config: 소스 설정
            
        Returns:
            추출된 본문 내용
        """
        content = ""
        
        # summary 또는 content에서 추출
        if hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # HTML 태그 제거
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
            # 공백 정리
            content = re.sub(r'\s+', ' ', content)
            
        return content[:2000]  # 최대 2000자로 제한
    
    def _extract_medium_claps(self, entry: Any) -> int:
        """Medium 글의 clap 수 추출 (Towards Data Science용)"""
        try:
            # Medium RSS에서 clap 정보는 보통 content나 summary에 포함
            content = self._extract_content(entry, {})
            
            # clap 패턴 검색 (다양한 형식 지원)
            clap_patterns = [
                r'(\d+)\s*clap',
                r'clap[s]?\s*[\(\[](\d+)[\)\]]',
                r'👏\s*(\d+)',
                r'(\d+)\s*👏'
            ]
            
            for pattern in clap_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            return 0
            
        except Exception as e:
            logger.debug(f"Clap 추출 중 오류: {e}")
            return 0
    
    def _calculate_score(self, title: str, content: str, source_config: Dict, 
                        published_time: datetime, claps: int = 0) -> float:
        """
        PRD v2.0 점수화 시스템에 따른 점수 계산 (블로그 전용)
        
        Args:
            title: 글 제목
            content: 글 내용
            source_config: 소스 설정
            published_time: 발행 시간
            claps: Medium clap 수
            
        Returns:
            계산된 점수
        """
        # 기본 점수 (블로그는 80점)
        base_score = source_config.get('score_bonus', 80)
        
        # Medium clap 보너스 (Towards Data Science 전용)
        if source_config.get('clap_filter') and claps >= 100:
            base_score += 20
            logger.debug(f"Medium clap 보너스 +20 ({claps} claps): {title[:50]}")
        
        # 실용 가이드 키워드 보너스 (+20점)
        guide_keywords = ["how to", "guide", "tutorial", "walkthrough", "step-by-step", 
                         "implementation", "practical", "hands-on"]
        if any(keyword.lower() in title.lower() for keyword in guide_keywords):
            base_score += 20
            logger.debug(f"실용 가이드 키워드 보너스 +20: {title[:50]}")
        
        # 실무 사례 키워드 보너스 (+15점)
        case_keywords = ["case study", "experience", "lessons learned", "how we", 
                        "real-world", "production", "in practice"]
        if any(keyword.lower() in title.lower() for keyword in case_keywords):
            base_score += 15
            logger.debug(f"실무 사례 키워드 보너스 +15: {title[:50]}")
        
        # LLM 관련 키워드 보너스 (+10점)
        llm_keywords = ["llm", "gpt", "transformer", "language model", "claude", "gemini", 
                       "chatgpt", "openai", "bert", "t5"]
        if any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in llm_keywords):
            base_score += 10
            logger.debug(f"LLM 키워드 보너스 +10: {title[:50]}")
        
        # 시계열 관련 키워드 보너스 (+10점)
        timeseries_keywords = ["time series", "forecasting", "prediction", "forecast", "arima", "lstm"]
        if any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in timeseries_keywords):
            base_score += 10
            logger.debug(f"시계열 키워드 보너스 +10: {title[:50]}")
        
        # MLOps 키워드 보너스 (+10점)
        mlops_keywords = ["mlops", "ml ops", "deployment", "monitoring", "pipeline", "kubernetes", 
                         "docker", "model serving", "experiment tracking"]
        if any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in mlops_keywords):
            base_score += 10
            logger.debug(f"MLOps 키워드 보너스 +10: {title[:50]}")
        
        # 신선도 보너스
        hours_old = (datetime.now(timezone.utc) - published_time).total_seconds() / 3600
        if hours_old < 24:
            base_score += 10
            logger.debug(f"24시간 이내 신선도 보너스 +10: {title[:50]}")
        elif hours_old < 168:  # 1주일
            base_score += 5
            logger.debug(f"1주일 이내 신선도 보너스 +5: {title[:50]}")
        
        # 패널티
        opinion_keywords = ["opinion", "thoughts on", "my take", "commentary", "i think", "personal"]
        if any(keyword.lower() in title.lower() for keyword in opinion_keywords):
            base_score -= 20
            logger.debug(f"의견 기사 패널티 -20: {title[:50]}")
        
        question_keywords = ["what do you think", "recommendations?", "suggestions?", 
                           "help me", "which should i", "what should i"]
        if any(keyword.lower() in title.lower() for keyword in question_keywords):
            base_score -= 30
            logger.debug(f"단순 질문 패널티 -30: {title[:50]}")
        
        # 내용이 너무 짧으면 패널티
        if len(content) < 500:
            base_score -= 15
            logger.debug(f"짧은 글 패널티 -15: {title[:50]}")
        
        return base_score
    
    def _parse_published_time(self, entry: Any) -> datetime:
        """RSS 항목에서 발행 시간 파싱"""
        published_time = datetime.now(timezone.utc)
        
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'published'):
            try:
                # 다양한 날짜 형식 처리
                import dateutil.parser
                published_time = dateutil.parser.parse(entry.published)
                if published_time.tzinfo is None:
                    published_time = published_time.replace(tzinfo=timezone.utc)
            except:
                pass
                
        return published_time
    
    def collect(self, max_articles_per_source: int = 8) -> List[Dict[str, Any]]:
        """
        실용 블로그에서 글 수집
        
        Args:
            max_articles_per_source: 소스별 최대 수집 글 수
            
        Returns:
            수집된 글 목록
        """
        all_articles = []
        
        logger.info("실용 블로그 수집 시작")
        
        for source_id, source_config in self.blog_sources.items():
            try:
                logger.info(f"{source_config['name']} 수집 중...")
                
                # RSS 피드 가져오기
                feed = self._fetch_rss_feed(source_config['url'], source_config['name'])
                if not feed or not hasattr(feed, 'entries'):
                    continue
                
                source_articles = []
                
                for entry in feed.entries:
                    try:
                        # 기본 정보 추출
                        title = entry.get('title', '').strip()
                        if not title:
                            continue
                            
                        url = entry.get('link', '').strip()
                        if not url:
                            continue
                        
                        # 발행 시간 파싱
                        published_time = self._parse_published_time(entry)
                        
                        # 날짜 필터링 (최근 60일)
                        if published_time < self.cutoff_date:
                            continue
                        
                        # 2025년 이전 글 제외
                        if published_time.year < 2025:
                            continue
                        
                        # 본문 내용 추출
                        content = self._extract_content(entry, source_config)
                        
                        # Medium clap 수 추출 (필요시)
                        claps = 0
                        if source_config.get('clap_filter'):
                            claps = self._extract_medium_claps(entry)
                            # clap이 너무 적으면 제외 (Towards Data Science)
                            if claps < 50 and claps > 0:
                                logger.debug(f"clap 부족으로 제외 ({claps} claps): {title[:50]}")
                                continue
                        
                        # AI/ML/DS 관련 키워드 필터링
                        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 
                                     'data science', 'llm', 'gpt', 'neural network', 'python', 'tensorflow',
                                     'pytorch', 'pandas', 'sklearn', 'nlp', 'computer vision', 'statistics']
                        
                        title_content_combined = (title + ' ' + content).lower()
                        if not any(keyword.lower() in title_content_combined for keyword in ai_keywords):
                            logger.debug(f"AI/ML/DS 키워드 없음으로 제외: {title[:50]}")
                            continue
                        
                        # 점수 계산
                        score = self._calculate_score(title, content, source_config, published_time, claps)
                        
                        # 최소 점수 필터링 (블로그는 70점 이상)
                        if score < 70:
                            logger.debug(f"점수 부족으로 제외 ({score}점): {title[:50]}")
                            continue
                        
                        # 글 정보 구성
                        article = {
                            'id': f"{source_id}_{hash(url) % 1000000}",
                            'title': title,
                            'content': content,
                            'url': url,
                            'source': source_config['name'],
                            'source_id': source_id,
                            'tags': source_config['tags'].copy(),
                            'score': score,
                            'published': published_time.isoformat(),
                            'collected_at': datetime.now(timezone.utc).isoformat(),
                            'claps': claps if claps > 0 else None,
                            'needs_translation': source_config.get('language', 'en') == 'en'  # 영어 글만 번역 필요
                        }
                        
                        source_articles.append(article)
                        logger.info(f"수집 성공 ({score}점): {title[:80]}")
                        
                    except Exception as e:
                        logger.error(f"글 처리 중 오류: {e}")
                        continue
                
                # 점수순 정렬 후 상위 N개 선택
                source_articles.sort(key=lambda x: x['score'], reverse=True)
                selected_articles = source_articles[:max_articles_per_source]
                
                all_articles.extend(selected_articles)
                logger.info(f"{source_config['name']}: {len(selected_articles)}개 글 선택")
                
                # API 호출 간격 (Rate Limiting 방지)
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"{source_config['name']} 수집 중 오류: {e}")
                continue
        
        logger.info(f"실용 블로그 수집 완료: 총 {len(all_articles)}개 글")
        return all_articles

if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    collector = PracticalBlogCollector()
    articles = collector.collect(max_articles_per_source=3)
    
    print(f"\n총 {len(articles)}개 블로그 글 수집됨")
    for article in articles[:3]:  # 상위 3개만 출력
        print(f"- {article['source']}: {article['title'][:60]} (점수: {article['score']})")
