#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Summarizer
Google Gemini API를 사용한 글 요약 서비스 (사용자 요구사항 반영)
"""

import os
import logging
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Google Generative AI (Gemini)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)

class Summarizer:
    """Google Gemini Pro API를 사용한 요약 생성기 클래스 (3문장 요약, 킬스위치 포함)"""
    
    def __init__(self, config: Config = None):
        """
        요약기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.gemini_model = None
        self.summary_cache = {}
        
        # API 오류율 추적 및 킬스위치 (사용자 요구사항)
        self.api_error_count = 0
        self.api_total_requests = 0
        self.killswitch_threshold = 0.5  # 50% 이상 실패시 킬스위치
        self.killswitch_active = False
        
        # Gemini API 초기화
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Gemini API 초기화"""
        if not GEMINI_AVAILABLE:
            logger.error("Google Generative AI 라이브러리가 설치되지 않았습니다.")
            return
        
        if not self.config.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
            return
        
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            
            # Gemini 모델 초기화
            model_name = self.config.GEMINI_MODEL
            self.gemini_model = genai.GenerativeModel(model_name)
            
            logger.info(f"Gemini API 초기화 성공 - 모델: {model_name}")
            
        except Exception as e:
            logger.error(f"Gemini API 초기화 실패: {e}")
            self.gemini_model = None
    
    def _create_summary_prompt(self, title: str, content: str) -> str:
        """
        사용자 요구사항에 맞는 프롬프트 생성
        
        Args:
            title: 글 제목
            content: 글 내용
            
        Returns:
            생성된 프롬프트
        """
        # 사용자 요구사항: "다음 기술 글을 정확히 3문장으로 요약해주세요. 핵심 내용과 결론을 포함하되 한국어로 답변하세요:"
        prompt = f"""다음 기술 글을 정확히 3문장으로 요약해주세요. 핵심 내용과 결론을 포함하되 한국어로 답변하세요:

제목: {title}

내용: {content}

요약 (정확히 3문장):"""
        
        return prompt
    
    def _extract_fallback_summary(self, title: str, content: str) -> str:
        """
        요약 실패시 첫 2문장을 대체 요약으로 사용 (사용자 요구사항)
        
        Args:
            title: 글 제목
            content: 글 내용
            
        Returns:
            대체 요약 (첫 2문장)
        """
        try:
            if not content:
                return title
            
            # 문장 분리 (한국어와 영어 모두 고려)
            sentences = re.split(r'[.!?]\s+|[。！？]\s*', content)
            
            # 의미있는 문장들 필터링
            meaningful_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10 and not sentence.lower().startswith(('the', 'a', 'an', 'this', 'that')):
                    meaningful_sentences.append(sentence)
            
            # 첫 2문장 선택
            if len(meaningful_sentences) >= 2:
                fallback_summary = meaningful_sentences[0] + '. ' + meaningful_sentences[1] + '.'
            elif len(meaningful_sentences) == 1:
                fallback_summary = meaningful_sentences[0] + '. ' + title + '에 대한 추가 정보는 원문을 참조하세요.'
            else:
                fallback_summary = f"{title}. 자세한 내용은 원문을 참조하세요."
            
            return fallback_summary
            
        except Exception as e:
            logger.error(f"대체 요약 생성 실패: {e}")
            return f"{title} - 요약을 생성할 수 없습니다."
    
    def _check_killswitch(self):
        """
        API 오류율 체크 및 킬스위치 확인
        
        Returns:
            킬스위치 활성화 여부
        """
        if self.api_total_requests > 10:  # 최소 10회 요청 후부터 체크
            error_rate = self.api_error_count / self.api_total_requests
            
            if error_rate >= self.killswitch_threshold:
                if not self.killswitch_active:
                    self.killswitch_active = True
                    logger.error(f"킬스위치 활성화: API 오류율 {error_rate:.2%} (임계값: {self.killswitch_threshold:.2%})")
                return True
        
        return self.killswitch_active
    
    def summarize_text(self, title: str, content: str) -> Dict[str, Any]:
        """
        텍스트 요약 (정확히 3문장)
        
        Args:
            title: 글 제목
            content: 글 내용
            
        Returns:
            요약 결과
        """
        if not content or not content.strip():
            return {
                'original_title': title,
                'original_content': content,
                'summary': title,
                'sentences_count': 1,
                'service': 'fallback',
                'success': False,
                'error': '내용이 비어있습니다.',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        
        # 캐시 확인
        cache_key = f"{hash(title + content)}_3sentences"
        if cache_key in self.summary_cache:
            logger.debug("캐시에서 요약 반환")
            return self.summary_cache[cache_key]
        
        # 킬스위치 체크
        if self._check_killswitch():
            logger.warning("킬스위치가 활성화되어 대체 요약 사용")
            fallback_summary = self._extract_fallback_summary(title, content)
            
            result = {
                'original_title': title,
                'original_content': content,
                'summary': fallback_summary,
                'sentences_count': 2,  # 대체 요약은 보통 2문장
                'service': 'fallback_killswitch',
                'success': False,
                'error': '킬스위치 활성화',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.summary_cache[cache_key] = result
            return result
        
        # 콘텐츠 길이 체크
        if len(content) < 50:
            logger.debug("내용이 너무 짧아 요약 생략")
            result = {
                'original_title': title,
                'original_content': content,
                'summary': f"{title}. {content[:100]}",
                'sentences_count': 2,
                'service': 'simple',
                'success': True,
                'error': None,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            self.summary_cache[cache_key] = result
            return result
        
        summary = ""
        service_used = None
        error_msg = None
        success = False
        
        # API 요청 카운트 증가
        self.api_total_requests += 1
        
        # Gemini API 사용 시도
        if self.gemini_model:
            try:
                prompt = self._create_summary_prompt(title, content)
                
                response = self.gemini_model.generate_content(prompt)
                
                if response and response.text:
                    summary = response.text.strip()
                    service_used = 'gemini'
                    success = True
                    logger.debug("Gemini API 요약 생성 성공")
                else:
                    raise Exception("Gemini API 응답이 비어있습니다.")
                
            except Exception as e:
                logger.error(f"Gemini API 요약 실패: {e}")
                error_msg = str(e)
                self.api_error_count += 1
        
        # Gemini 실패시 대체 요약 생성 (사용자 요구사항)
        if not summary:
            summary = self._extract_fallback_summary(title, content)
            service_used = 'fallback'
            success = False
            logger.debug("대체 요약 생성 사용")
        
        # 문장 수 계산 (정확히 3문장인지 확인)
        sentences = re.split(r'[.!?。！？]', summary)
        sentences_count = len([s for s in sentences if s.strip()])
        
        # 3문장이 아니면 경고 로그
        if sentences_count != 3 and service_used == 'gemini':
            logger.warning(f"요약이 3문장이 아님: {sentences_count}문장")
        
        result = {
            'original_title': title,
            'original_content': content,
            'summary': summary,
            'sentences_count': sentences_count,
            'service': service_used,
            'success': success,
            'error': error_msg,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # 캐시 저장
        self.summary_cache[cache_key] = result
        
        return result
    
    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        글 요약 (한국어 우선, 번역된 내용 사용)
        
        Args:
            article: 요약할 글 데이터
            
        Returns:
            요약이 추가된 글 데이터
        """
        summarized_article = article.copy()
        
        try:
            # 번역된 한국어 텍스트 우선 사용
            title = article.get('title_ko') or article.get('title', '')
            content = article.get('content_ko') or article.get('content', '')
            
            # 요약 생성
            summary_result = self.summarize_text(title, content)
            
            # 결과 반영
            summarized_article.update({
                'summary': summary_result['summary'],
                'summary_sentences': summary_result['sentences_count'],
                'summarized_at': summary_result['created_at'],
                'summarization_service': summary_result['service'],
                'summarization_success': summary_result['success'],
                'summarization_error': summary_result['error']
            })
            
            if summary_result['success']:
                logger.info(f"글 요약 완료: {title[:50]}...")
            else:
                logger.warning(f"글 요약 실패 (대체 요약 사용): {title[:50]}...")
            
        except Exception as e:
            logger.error(f"글 요약 처리 실패: {e}")
            summarized_article.update({
                'summary': article.get('title', ''),
                'summary_sentences': 1,
                'summarized_at': datetime.now(timezone.utc).isoformat(),
                'summarization_service': 'error',
                'summarization_success': False,
                'summarization_error': str(e)
            })
        
        return summarized_article
    
    def summarize_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        글 목록 일괄 요약
        
        Args:
            articles: 요약할 글 목록
            
        Returns:
            요약이 추가된 글 목록
        """
        if not articles:
            return []
        
        logger.info(f"일괄 요약 시작: {len(articles)}개 글")
        
        summarized_articles = []
        
        for i, article in enumerate(articles):
            try:
                summarized = self.summarize_article(article)
                summarized_articles.append(summarized)
                
                # 진행 상황 로그
                if (i + 1) % 3 == 0:
                    logger.info(f"요약 진행: {i + 1}/{len(articles)}")
                
                # API 요청 제한 대응 (Gemini는 분당 요청 제한이 있음)
                time.sleep(2)
                
                # 킬스위치 체크 (중간에 멈출 수 있음)
                if self._check_killswitch():
                    logger.warning("킬스위치 활성화로 나머지 글들은 대체 요약 사용")
                
            except Exception as e:
                logger.error(f"글 요약 실패 (인덱스 {i}): {e}")
                # 요약 실패해도 원본은 포함
                article['summary'] = article.get('title', '')
                article['summarization_error'] = str(e)
                summarized_articles.append(article)
                continue
        
        logger.info(f"일괄 요약 완료: {len(summarized_articles)}개")
        
        # 최종 통계 로그
        error_rate = self.api_error_count / self.api_total_requests if self.api_total_requests > 0 else 0
        logger.info(f"Gemini API 오류율: {error_rate:.2%} ({self.api_error_count}/{self.api_total_requests})")
        
        return summarized_articles
    
    def get_summarization_stats(self) -> Dict[str, Any]:
        """
        요약 통계 정보 (킬스위치 상태 포함)
        
        Returns:
            요약 통계
        """
        error_rate = self.api_error_count / self.api_total_requests if self.api_total_requests > 0 else 0
        
        return {
            'cache_size': len(self.summary_cache),
            'gemini_available': self.gemini_model is not None,
            'api_total_requests': self.api_total_requests,
            'api_error_count': self.api_error_count,
            'api_error_rate': error_rate,
            'killswitch_active': self.killswitch_active,
            'killswitch_threshold': self.killswitch_threshold
        }
    
    def clear_cache(self):
        """요약 캐시 클리어"""
        self.summary_cache.clear()
        logger.info("요약 캐시가 클리어되었습니다.")
    
    def reset_killswitch(self):
        """킬스위치 리셋 (수동 복구용)"""
        self.killswitch_active = False
        self.api_error_count = 0
        self.api_total_requests = 0
        logger.info("킬스위치가 리셋되었습니다.")
    
    def test_connection(self) -> bool:
        """
        Gemini API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        if not self.gemini_model:
            return False
        
        try:
            test_prompt = "간단한 테스트입니다."
            response = self.gemini_model.generate_content(test_prompt)
            return bool(response and response.text)
            
        except Exception as e:
            logger.error(f"Gemini 연결 테스트 실패: {e}")
            return False


# 유틸리티 함수
def summarize_articles(articles: List[Dict[str, Any]], config: Config = None) -> List[Dict[str, Any]]:
    """
    글 목록 요약 편의 함수
    
    Args:
        articles: 요약할 글 목록
        config: 설정 객체
        
    Returns:
        요약이 추가된 글 목록
    """
    summarizer = Summarizer(config)
    return summarizer.summarize_articles_batch(articles)


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    summarizer = Summarizer()
    
    # 연결 테스트
    if summarizer.test_connection():
        print("✅ Gemini API 연결 성공")
        
        # 요약 테스트
        test_title = "머신러닝을 활용한 데이터 분석 방법"
        test_content = "머신러닝은 현대 데이터 분석의 핵심 기술로 자리 잡았습니다. 다양한 알고리즘과 기법을 통해 패턴을 발견하고 예측 모델을 구축할 수 있습니다. 특히 딥러닝과 신경망 기술의 발전으로 더욱 정교한 분석이 가능해졌습니다. 데이터 전처리부터 모델 평가까지의 전체 파이프라인을 이해하는 것이 중요합니다."
        
        result = summarizer.summarize_text(test_title, test_content)
        
        print(f"원문 제목: {test_title}")
        print(f"요약 ({result['sentences_count']}문장): {result['summary']}")
        print(f"서비스: {result['service']}")
        print(f"성공: {result['success']}")
        
        if result['error']:
            print(f"오류: {result['error']}")
    else:
        print("❌ Gemini API 연결 실패")
    
    # 통계 출력
    stats = summarizer.get_summarization_stats()
    print(f"\n요약 통계: {stats}")