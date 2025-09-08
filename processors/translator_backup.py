#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Enhanced Translator
Gemini API를 활용한 고품질 번역 + googletrans 백업
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
import re
from datetime import datetime, timezone

# Gemini API 라이브러리
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# googletrans 라이브러리 (백업용)
try:
    from googletrans import Translator as GoogleTranslator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)

class Translator:
    """Gemini API + googletrans를 사용한 고품질 번역기 클래스"""
    
    def __init__(self, config: Config = None):
        """
        번역기 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        self.gemini_model = None
        self.googletrans_client = None
        self.translation_cache = {}
        
        # 기술 용어 사전
        self.tech_dictionary = {
            'Machine Learning': '머신러닝',
            'Deep Learning': '딥러닝',
            'Neural Network': '신경망',
            'Artificial Intelligence': '인공지능',
            'Data Science': '데이터 사이언스',
            'Natural Language Processing': '자연어 처리',
            'Computer Vision': '컴퓨터 비전',
            'Reinforcement Learning': '강화학습',
            'Time Series': '시계열',
            'Feature Engineering': '피처 엔지니어링',
            'Model Deployment': '모델 배포',
            'MLOps': 'MLOps',
            'API': 'API',
            'Framework': '프레임워크',
            'Algorithm': '알고리즘',
            'Dataset': '데이터셋',
            'Training': '훈련',
            'Inference': '추론',
            'Pipeline': '파이프라인',
            'Transformer': '트랜스포머'
        }
        
        # Gemini API 초기화
        self._initialize_gemini()
        
        # googletrans 초기화 (백업용)
        self._initialize_googletrans()
    
    def _initialize_gemini(self):
        """Gemini API 초기화"""
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai 라이브러리가 설치되지 않았습니다.")
            return
            
        if not self.config.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY가 설정되지 않았습니다.")
            return
        
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(self.config.GEMINI_MODEL)
            logger.info("Gemini API 번역 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"Gemini API 초기화 실패: {e}")
            self.gemini_model = None
    
    def _initialize_googletrans(self):
        """googletrans 초기화"""
        if not GOOGLETRANS_AVAILABLE:
            logger.error("googletrans 라이브러리가 설치되지 않았습니다.")
            return
        
        try:
            self.googletrans_client = GoogleTranslator()
            logger.info("googletrans 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"googletrans 초기화 실패: {e}")
    
    def _detect_language(self, text: str) -> str:
        """
        텍스트의 언어 감지
        
        Args:
            text: 언어를 감지할 텍스트
            
        Returns:
            감지된 언어 코드 ('ko' 또는 'en')
        """
        try:
            # 한국어 패턴 체크 (더 정확한 감지)
            korean_pattern = r'[가-힣]'
            korean_chars = len(re.findall(korean_pattern, text))
            
            # 전체 문자 대비 한국어 문자 비율
            total_chars = len(re.sub(r'\s+', '', text))
            if total_chars > 0 and korean_chars / total_chars > 0.1:  # 10% 이상이면 한국어
                return 'ko'
            
            # googletrans로 언어 감지 시도
            if self.googletrans_client:
                try:
                    detection = self.googletrans_client.detect(text[:100])  # 처음 100자만 감지
                    return detection.lang
                except Exception as e:
                    logger.debug(f"googletrans 언어 감지 실패: {e}")
            
            # 기본값은 영어
            return 'en'
            
        except Exception as e:
            logger.error(f"언어 감지 실패: {e}")
            return 'en'
    
    def _clean_text_for_translation(self, text: str) -> str:
        """
        번역을 위한 텍스트 정리 및 길이 제한
        
        Args:
            text: 정리할 텍스트
            
        Returns:
            정리된 텍스트 (2000자 이상이면 첫 1000자만)
        """
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 2000자 이상 글은 첫 1000자만 번역 (사용자 요구사항)
        if len(text) > 2000:
            text = text[:1000] + "..."
            logger.info(f"텍스트가 2000자를 초과하여 1000자로 제한했습니다.")
        
        return text
    
    def translate_text(self, text: str, target_language: str = 'ko') -> Dict[str, Any]:
        """
        텍스트 번역 (영문만 번역, 한국어는 스킵)
        
        Args:
            text: 번역할 텍스트
            target_language: 목표 언어 (기본: 한국어)
            
        Returns:
            번역 결과
        """
        if not text or not text.strip():
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': 'unknown',
                'target_language': target_language,
                'translation_needed': False,
                'success': True,
                'error': None
            }
        
        # 텍스트 정리 및 길이 제한
        cleaned_text = self._clean_text_for_translation(text)
        
        # 캐시 확인
        cache_key = f"{hash(cleaned_text)}_{target_language}"
        if cache_key in self.translation_cache:
            logger.debug("캐시에서 번역 결과 반환")
            return self.translation_cache[cache_key]
        
        # 언어 감지
        detected_lang = self._detect_language(cleaned_text)
        
        # 이미 한국어면 번역 스킵 (사용자 요구사항)
        if detected_lang == 'ko' and target_language == 'ko':
            result = {
                'original_text': text,
                'translated_text': cleaned_text,
                'source_language': 'ko',
                'target_language': target_language,
                'translation_needed': False,
                'success': True,
                'error': None
            }
            self.translation_cache[cache_key] = result
            return result
        
        # 영문만 번역 (사용자 요구사항)
        if detected_lang != 'en':
            logger.info(f"영문이 아닌 언어({detected_lang})는 번역하지 않습니다.")
            result = {
                'original_text': text,
                'translated_text': cleaned_text,
                'source_language': detected_lang,
                'target_language': target_language,
                'translation_needed': False,
                'success': True,
                'error': None
            }
            self.translation_cache[cache_key] = result
            return result
        
        # googletrans로 번역 시도
        if not self.googletrans_client:
            # 번역 실패시 원문 그대로 반환 (사용자 요구사항)
            result = {
                'original_text': text,
                'translated_text': cleaned_text,
                'source_language': detected_lang,
                'target_language': target_language,
                'translation_needed': True,
                'success': False,
                'error': 'googletrans 클라이언트가 초기화되지 않았습니다.'
            }
            self.translation_cache[cache_key] = result
            return result
        
        try:
            # 번역 실행
            translation = self.googletrans_client.translate(
                cleaned_text,
                dest=target_language,
                src='en'
            )
            
            result = {
                'original_text': text,
                'translated_text': translation.text,
                'source_language': 'en',
                'target_language': target_language,
                'translation_needed': True,
                'success': True,
                'error': None
            }
            
            # 캐시 저장
            self.translation_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"번역 실패: {e}")
            
            # 번역 실패시 원문 그대로 반환 (사용자 요구사항)
            result = {
                'original_text': text,
                'translated_text': cleaned_text,
                'source_language': detected_lang,
                'target_language': target_language,
                'translation_needed': True,
                'success': False,
                'error': str(e)
            }
            
            # 캐시 저장
            self.translation_cache[cache_key] = result
            return result
    
    def translate_article(self, article: Dict[str, Any], target_language: str = 'ko') -> Dict[str, Any]:
        """
        글 전체 번역 (제목과 내용)
        
        Args:
            article: 번역할 글 데이터
            target_language: 목표 언어
            
        Returns:
            번역된 글 데이터
        """
        translated_article = article.copy()
        
        try:
            # 번역이 필요한지 확인
            needs_translation = article.get('needs_translation', True)
            if not needs_translation:
                logger.debug(f"번역 불필요: {article.get('title', '')[:50]}")
                return translated_article
            
            # 제목 번역
            title_result = self.translate_text(
                article.get('title', ''),
                target_language=target_language
            )
            
            # 내용 번역
            content_result = self.translate_text(
                article.get('content', ''),
                target_language=target_language
            )
            
            # 번역 결과 반영
            translated_article.update({
                'title_ko': title_result['translated_text'],
                'content_ko': content_result['translated_text'],
                'title_original': article.get('title', ''),
                'content_original': article.get('content', ''),
                'translated_at': datetime.now(timezone.utc).isoformat(),
                'translation_success': title_result['success'] and content_result['success'],
                'translation_errors': []
            })
            
            # 번역 오류 기록
            if not title_result['success']:
                translated_article['translation_errors'].append(f"제목: {title_result['error']}")
            if not content_result['success']:
                translated_article['translation_errors'].append(f"내용: {content_result['error']}")
            
            if translated_article['translation_success']:
                logger.info(f"글 번역 완료: {article.get('title', '')[:50]}...")
            else:
                logger.warning(f"글 번역 실패 (원문 유지): {article.get('title', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"글 번역 처리 실패: {e}")
            translated_article['translation_errors'] = [str(e)]
            translated_article['translation_success'] = False
        
        return translated_article
    
    def translate_articles_batch(self, articles: List[Dict[str, Any]], 
                               target_language: str = 'ko') -> List[Dict[str, Any]]:
        """
        글 목록 일괄 번역
        
        Args:
            articles: 번역할 글 목록
            target_language: 목표 언어
            
        Returns:
            번역된 글 목록
        """
        if not articles:
            return []
        
        logger.info(f"일괄 번역 시작: {len(articles)}개 글")
        
        translated_articles = []
        
        for i, article in enumerate(articles):
            try:
                translated = self.translate_article(article, target_language)
                translated_articles.append(translated)
                
                # 진행 상황 로그
                if (i + 1) % 5 == 0:
                    logger.info(f"번역 진행: {i + 1}/{len(articles)}")
                
                # API 요청 제한 대응 (googletrans는 무료 서비스라 제한이 있음)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"글 번역 실패 (인덱스 {i}): {e}")
                # 번역 실패해도 원본은 포함
                translated_articles.append(article)
                continue
        
        logger.info(f"일괄 번역 완료: {len(translated_articles)}개")
        return translated_articles
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """
        번역 통계 정보
        
        Returns:
            번역 통계
        """
        return {
            'cache_size': len(self.translation_cache),
            'googletrans_available': self.googletrans_client is not None,
            'service_status': 'available' if self.googletrans_client else 'unavailable'
        }
    
    def clear_cache(self):
        """번역 캐시 클리어"""
        self.translation_cache.clear()
        logger.info("번역 캐시가 클리어되었습니다.")


# 유틸리티 함수
def translate_articles(articles: List[Dict[str, Any]], 
                      config: Config = None,
                      target_language: str = 'ko') -> List[Dict[str, Any]]:
    """
    글 목록 번역 편의 함수
    
    Args:
        articles: 번역할 글 목록
        config: 설정 객체
        target_language: 목표 언어
        
    Returns:
        번역된 글 목록
    """
    translator = Translator(config)
    return translator.translate_articles_batch(articles, target_language)


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    
    translator = Translator()
    
    # 번역 테스트
    test_texts = [
        "Machine Learning is transforming the way we approach data analysis.",  # 영문 -> 번역됨
        "머신러닝은 데이터 분석 방식을 변화시키고 있습니다.",  # 한국어 -> 번역 스킵
        "This is a very long text that exceeds 2000 characters. " * 100  # 긴 텍스트 -> 1000자로 제한
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n=== 테스트 {i} ===")
        result = translator.translate_text(text)
        print(f"원문: {result['original_text'][:100]}...")
        print(f"번역: {result['translated_text'][:100]}...")
        print(f"번역 필요: {result['translation_needed']}")
        print(f"성공: {result['success']}")
        
        if result['error']:
            print(f"오류: {result['error']}")
    
    # 통계 출력
    stats = translator.get_translation_stats()
    print(f"\n번역 통계: {stats}")