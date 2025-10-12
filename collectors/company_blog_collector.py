#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Company Blog Collector
기업 기술 블로그에서 RSS 피드를 통해 AI/ML 연구 및 기술 글 수집
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

class CompanyBlogCollector:
    """기업 블로그 수집기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        기업 블로그 수집기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.content_filter = ContentFilter(config)
        
        # 요청 헤더 (기업 사이트 접근 최적화)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 세션 생성
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 날짜 필터링 설정 (최근 60일)
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
        
        # 기업 블로그 소스 설정 (PRD v2.0 기준)
        self.company_sources = {
            "google_ai": {
                "name": "Google AI Blog",
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "score_bonus": 70,
                "tags": ["기업블로그", "연구", "Google"],
                "language": "en"
            },
            "openai_blog": {
                "name": "OpenAI Blog",
                "url": "https://openai.com/blog/rss.xml",
                "score_bonus": 90,  # 높은 품질
                "tags": ["기업블로그", "최신기술", "OpenAI"],
                "language": "en"
            },
            "naver_d2": {
                "name": "NAVER D2",
                "url": "https://d2.naver.com/helloworld.rss",
                "score_bonus": 75,
                "tags": ["기업블로그", "국내", "NAVER"],
                "language": "ko"
            },
            "kakao_tech": {
                "name": "Kakao Tech Blog",
                "url": "https://tech.kakao.com/rss.xml",
                "score_bonus": 75,
                "tags": ["기업블로그", "국내", "Kakao"],
                "language": "ko"
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
    
    def _calculate_score(self, title: str, content: str, source_config: Dict, published_time: datetime) -> float:
        """
        PRD v2.0 점수화 시스템에 따른 점수 계산 (기업 블로그 전용)
        
        Args:
            title: 글 제목
            content: 글 내용
            source_config: 소스 설정
            published_time: 발행 시간
            
        Returns:
            계산된 점수
        """
        # 기본 점수 (기업 블로그는 70점)
        base_score = source_config.get('score_bonus', 70)
        
        # 언어별 키워드 설정
        is_korean = source_config.get('language') == 'ko'
        
        # 연구 발표/논문 키워드 보너스 (+25점) - 기업 블로그 특화
        if is_korean:
            research_keywords = ["연구", "논문", "발표", "공개", "출시", "개발"]
        else:
            research_keywords = ["research", "paper", "introduces", "announces", "releases", "proposes"]
            
        if any(keyword.lower() in title.lower() for keyword in research_keywords):
            base_score += 25
            logger.debug(f"연구 발표 키워드 보너스 +25: {title[:50]}")
        
        # 기술 구현/아키텍처 키워드 보너스 (+20점)
        if is_korean:
            tech_keywords = ["구현", "아키텍처", "시스템", "플랫폼", "프레임워크", "최적화"]
        else:
            tech_keywords = ["implementation", "architecture", "system", "platform", "framework", "optimization"]
            
        if any(keyword.lower() in title.lower() for keyword in tech_keywords):
            base_score += 20
            logger.debug(f"기술 구현 키워드 보너스 +20: {title[:50]}")
        
        # 최신 AI/ML 기술 키워드 보너스 (+15점)
        cutting_edge_keywords = ["gpt", "llm", "transformer", "diffusion", "multimodal", "rlhf",
                               "reinforcement learning", "neural network", "deep learning",
                               "GPT", "LLM", "트랜스포머", "강화학습", "신경망"]
        if any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in cutting_edge_keywords):
            base_score += 15
            logger.debug(f"최신 AI/ML 기술 키워드 보너스 +15: {title[:50]}")
        
        # 오픈소스/도구 키워드 보너스 (+10점)
        if is_korean:
            opensource_keywords = ["오픈소스", "공개", "라이브러리", "도구", "툴킷"]
        else:
            opensource_keywords = ["open source", "library", "toolkit", "framework", "api", "github"]
            
        if any(keyword.lower() in title.lower() for keyword in opensource_keywords):
            base_score += 10
            logger.debug(f"오픈소스/도구 키워드 보너스 +10: {title[:50]}")
        
        # 성능/벤치마크 키워드 보너스 (+10점)
        if is_korean:
            performance_keywords = ["성능", "벤치마크", "평가", "비교", "측정"]
        else:
            performance_keywords = ["performance", "benchmark", "evaluation", "comparison", "metrics"]
            
        if any(keyword.lower() in title.lower() for keyword in performance_keywords):
            base_score += 10
            logger.debug(f"성능/벤치마크 키워드 보너스 +10: {title[:50]}")
        
        # 신선도 보너스 (기업 블로그는 더 관대하게)
        hours_old = (datetime.now(timezone.utc) - published_time).total_seconds() / 3600
        if hours_old < 72:  # 3일
            base_score += 15
            logger.debug(f"3일 이내 신선도 보너스 +15: {title[:50]}")
        elif hours_old < 336:  # 2주일
            base_score += 8
            logger.debug(f"2주일 이내 신선도 보너스 +8: {title[:50]}")
        
        # 기업별 특별 가중치
        company_name = source_config.get('name', '')
        if 'openai' in company_name.lower():
            base_score += 15  # OpenAI는 특별 가중치
            logger.debug(f"OpenAI 특별 가중치 +15: {title[:50]}")
        elif 'google' in company_name.lower():
            base_score += 10  # Google도 높은 가중치
            logger.debug(f"Google 특별 가중치 +10: {title[:50]}")
        
        # 패널티 (기업 블로그는 일반적으로 품질이 높으므로 패널티 적게)
        if is_korean:
            recruiting_keywords = ["채용", "입사", "면접", "구인"]
        else:
            recruiting_keywords = ["hiring", "job", "career", "interview", "join us"]
            
        if any(keyword.lower() in title.lower() for keyword in recruiting_keywords):
            base_score -= 10  # 채용 관련은 가벼운 패널티
            logger.debug(f"채용 관련 패널티 -10: {title[:50]}")
        
        # 내용이 너무 짧으면 패널티
        if len(content) < 300:  # 기업 블로그는 기준을 낮게
            base_score -= 10
            logger.debug(f"짧은 글 패널티 -10: {title[:50]}")
        
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
    
    def collect(self, max_articles_per_source: int = 5) -> List[Dict[str, Any]]:
        """
        기업 블로그에서 글 수집
        
        Args:
            max_articles_per_source: 소스별 최대 수집 글 수
            
        Returns:
            수집된 글 목록
        """
        all_articles = []
        
        logger.info("기업 블로그 수집 시작")
        
        for source_id, source_config in self.company_sources.items():
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
                        
                        # 날짜 필터링 (최근 60일 - 기업 블로그는 더 관대하게)
                        if published_time < self.cutoff_date:
                            continue
                        
                        # 2025년 이전 글 제외
                        if published_time.year < 2025:
                            continue
                        
                        # 본문 내용 추출
                        content = self._extract_content(entry, source_config)
                        
                        # AI/ML/연구 관련 키워드 필터링 (기업 블로그는 좀 더 관대하게)
                        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 
                                     'research', 'neural', 'algorithm', 'model', 'data', 'llm', 'gpt',
                                     '인공지능', 'AI', 'ML', '머신러닝', '딥러닝', '연구', '알고리즘', '모델']
                        
                        title_content_combined = (title + ' ' + content).lower()
                        if not any(keyword.lower() in title_content_combined for keyword in ai_keywords):
                            logger.debug(f"AI/ML/연구 키워드 없음으로 제외: {title[:50]}")
                            continue
                        
                        # 점수 계산
                        score = self._calculate_score(title, content, source_config, published_time)
                        
                        # 최소 점수 필터링 (기업 블로그는 65점 이상)
                        if score < 65:
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
                            'needs_translation': source_config.get('language') == 'en'  # 영어 글만 번역 필요
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
        
        logger.info(f"기업 블로그 수집 완료: 총 {len(all_articles)}개 글")
        return all_articles

if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    collector = CompanyBlogCollector()
    articles = collector.collect(max_articles_per_source=2)
    
    print(f"\n총 {len(articles)}개 기업 블로그 글 수집됨")
    for article in articles[:3]:  # 상위 3개만 출력
        print(f"- {article['source']}: {article['title'][:60]} (점수: {article['score']})")
