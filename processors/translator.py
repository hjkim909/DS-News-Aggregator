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

class TranslatorEnhanced:
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
        self.translation_stats = {
            'gemini_success': 0,
            'gemini_fail': 0,
            'googletrans_success': 0,
            'googletrans_fail': 0
        }
        
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
            'Transformer': '트랜스포머',
            'LLM': 'LLM',
            'Large Language Model': '대형 언어 모델',
            'Embedding': '임베딩',
            'Fine-tuning': '파인튜닝',
            'Prompt Engineering': '프롬프트 엔지니어링'
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
        """googletrans 초기화 (백업용)"""
        if not GOOGLETRANS_AVAILABLE:
            logger.warning("googletrans 라이브러리가 설치되지 않았습니다.")
            return
        
        try:
            self.googletrans_client = GoogleTranslator()
            logger.info("googletrans 백업 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"googletrans 초기화 실패: {e}")
    
    def _is_korean(self, text: str) -> bool:
        """텍스트가 주로 한국어인지 확인"""
        if not text:
            return True
            
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'[가-힣A-Za-z]', text))
        
        if total_chars == 0:
            return True
            
        korean_ratio = korean_chars / total_chars
        return korean_ratio > 0.3
    
    def _preprocess_text(self, text: str) -> str:
        """번역 전 텍스트 전처리"""
        if not text:
            return text
            
        # 기술 용어 보호
        protected_text = text
        for eng_term, kor_term in self.tech_dictionary.items():
            # 이미 한국어로 되어있으면 영어로 임시 변경 (번역 후 복원)
            protected_text = protected_text.replace(kor_term, f"__TECH__{eng_term}__TECH__")
        
        return protected_text
    
    def _postprocess_text(self, text: str) -> str:
        """번역 후 텍스트 후처리"""
        if not text:
            return text
            
        # 기술 용어 복원
        processed_text = text
        for eng_term, kor_term in self.tech_dictionary.items():
            processed_text = processed_text.replace(f"__TECH__{eng_term}__TECH__", kor_term)
            # 영어 용어가 그대로 남아있으면 한국어로 교체
            processed_text = processed_text.replace(eng_term, kor_term)
        
        return processed_text
    
    def _translate_with_gemini(self, text: str, content_type: str = "general") -> Dict[str, Any]:
        """Gemini API를 사용한 고품질 번역"""
        if not self.gemini_model:
            return {'success': False, 'error': 'Gemini API가 초기화되지 않았습니다.'}
        
        # 캐시 확인
        cache_key = f"gemini_{hash(text)}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            # 컨텍스트에 맞는 프롬프트 생성
            if content_type == "title":
                prompt = f"""다음 영문 기술 블로그 제목을 한국어로 번역해주세요.
기술 용어는 정확히 번역하고, 자연스러운 한국어 제목으로 만들어주세요.
원문의 의미를 정확히 전달하되 한국어로 읽기 편하게 번역해주세요.

번역할 제목: {text}

번역된 제목만 출력하세요."""

            elif content_type == "content":
                prompt = f"""다음 영문 기술 글을 한국어로 번역해주세요.
기술 용어와 개념은 정확히 번역하고, 자연스러운 한국어 문체로 번역해주세요.
코드나 특수 기호는 그대로 유지하되, 설명 부분은 이해하기 쉽게 번역해주세요.

번역할 내용: {text}

번역된 내용만 출력하세요."""
            
            else:  # general
                prompt = f"""다음 영문을 자연스러운 한국어로 번역해주세요.
기술 용어는 정확히 번역하고, 한국어로 읽기 편하게 번역해주세요.

번역할 내용: {text}

번역된 내용만 출력하세요."""
            
            response = self.gemini_model.generate_content(prompt)
            translated_text = response.text.strip()
            
            # 후처리
            translated_text = self._postprocess_text(translated_text)
            
            result = {
                'success': True,
                'translated_text': translated_text,
                'method': 'gemini',
                'original_text': text
            }
            
            # 캐시 저장
            self.translation_cache[cache_key] = result
            self.translation_stats['gemini_success'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini API 번역 실패: {e}")
            self.translation_stats['gemini_fail'] += 1
            return {'success': False, 'error': str(e)}
    
    def _translate_with_googletrans(self, text: str) -> Dict[str, Any]:
        """googletrans를 사용한 백업 번역"""
        if not self.googletrans_client:
            return {'success': False, 'error': 'googletrans가 초기화되지 않았습니다.'}
        
        # 캐시 확인
        cache_key = f"googletrans_{hash(text)}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            # 2000자 이상이면 첫 1000자만 번역
            text_to_translate = text[:1000] if len(text) > 2000 else text
            
            # 전처리
            preprocessed_text = self._preprocess_text(text_to_translate)
            
            result = self.googletrans_client.translate(
                preprocessed_text, 
                src='en', 
                dest='ko'
            )
            
            # 후처리
            translated_text = self._postprocess_text(result.text)
            
            result_dict = {
                'success': True,
                'translated_text': translated_text,
                'method': 'googletrans',
                'original_text': text,
                'truncated': len(text) > 2000
            }
            
            # 캐시 저장
            self.translation_cache[cache_key] = result_dict
            self.translation_stats['googletrans_success'] += 1
            
            return result_dict
            
        except Exception as e:
            logger.error(f"googletrans 번역 실패: {e}")
            self.translation_stats['googletrans_fail'] += 1
            return {'success': False, 'error': str(e)}
    
    def translate_text(self, text: str, content_type: str = "general") -> Dict[str, Any]:
        """
        텍스트 번역 (Gemini 우선, googletrans 백업)
        
        Args:
            text: 번역할 텍스트
            content_type: 컨텐츠 타입 ('title', 'content', 'general')
        
        Returns:
            번역 결과 딕셔너리
        """
        if not text or not text.strip():
            return {
                'success': True,
                'translated_text': text,
                'translation_needed': False,
                'method': 'no_translation'
            }
        
        # 한국어 텍스트면 번역 스킵
        if self._is_korean(text):
            return {
                'success': True,
                'translated_text': text,
                'translation_needed': False,
                'method': 'korean_detected'
            }
        
        # 1. Gemini API 번역 시도
        gemini_result = self._translate_with_gemini(text, content_type)
        if gemini_result['success']:
            gemini_result['translation_needed'] = True
            return gemini_result
        
        logger.warning(f"Gemini 번역 실패, googletrans로 백업: {gemini_result.get('error')}")
        
        # 2. googletrans 백업 번역
        googletrans_result = self._translate_with_googletrans(text)
        if googletrans_result['success']:
            googletrans_result['translation_needed'] = True
            return googletrans_result
        
        # 3. 모든 번역 실패시 원문 반환
        logger.error("모든 번역 방법 실패, 원문 반환")
        return {
            'success': False,
            'translated_text': text,
            'translation_needed': True,
            'method': 'failed',
            'error': f"Gemini: {gemini_result.get('error')}, googletrans: {googletrans_result.get('error')}"
        }
    
    def translate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        기사 전체 번역
        
        Args:
            article: 번역할 기사 딕셔너리
        
        Returns:
            번역된 기사 딕셔너리
        """
        translated_article = article.copy()
        
        # 제목 번역
        if 'title' in article:
            title_result = self.translate_text(article['title'], 'title')
            translated_article['title_ko'] = title_result['translated_text']
        
        # 내용 번역
        if 'content' in article:
            content_result = self.translate_text(article['content'], 'content')
            translated_article['content_ko'] = content_result['translated_text']
        
        return translated_article
    
    def translate_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 글을 배치로 번역
        
        Args:
            articles: 번역할 글 목록
            
        Returns:
            번역된 글 목록
        """
        translated_articles = []
        
        logger.info(f"{len(articles)}개 글 번역 시작")
        
        for i, article in enumerate(articles, 1):
            try:
                translated_article = self.translate_article(article)
                translated_articles.append(translated_article)
                
                if i % 5 == 0:
                    logger.info(f"번역 진행: {i}/{len(articles)}개 완료")
                    time.sleep(1)  # API Rate Limiting 방지
                    
            except Exception as e:
                logger.error(f"글 번역 중 오류 ({article.get('title', '')[:50]}): {e}")
                # 오류가 발생해도 원본 글은 반환
                translated_articles.append(article)
        
        logger.info(f"배치 번역 완료: {len(translated_articles)}개")
        return translated_articles
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """번역 통계 반환"""
        total_gemini = self.translation_stats['gemini_success'] + self.translation_stats['gemini_fail']
        total_googletrans = self.translation_stats['googletrans_success'] + self.translation_stats['googletrans_fail']
        
        return {
            'gemini': {
                'success': self.translation_stats['gemini_success'],
                'fail': self.translation_stats['gemini_fail'],
                'success_rate': (self.translation_stats['gemini_success'] / total_gemini * 100) if total_gemini > 0 else 0
            },
            'googletrans': {
                'success': self.translation_stats['googletrans_success'],
                'fail': self.translation_stats['googletrans_fail'],
                'success_rate': (self.translation_stats['googletrans_success'] / total_googletrans * 100) if total_googletrans > 0 else 0
            },
            'cache_size': len(self.translation_cache)
        }

# 기존 Translator 클래스와의 호환성을 위한 별칭
Translator = TranslatorEnhanced

if __name__ == '__main__':
    # 번역기 테스트
    config = Config()
    translator = TranslatorEnhanced(config)
    
    # 테스트 텍스트들
    test_texts = [
        "Machine Learning fundamentals for data scientists",
        "Deep Learning을 활용한 시계열 예측",
        "How to implement Neural Networks using PyTorch",
        "Building scalable ML pipelines in production"
    ]
    
    print("🧪 향상된 번역기 테스트")
    print("="*50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. 원문: {text}")
        result = translator.translate_text(text, 'title')
        
        if result['success']:
            print(f"   번역: {result['translated_text']}")
            print(f"   방법: {result['method']}")
            print(f"   번역필요: {result['translation_needed']}")
        else:
            print(f"   오류: {result.get('error')}")
    
    print(f"\n📊 번역 통계:")
    stats = translator.get_translation_stats()
    print(f"   Gemini 성공률: {stats['gemini']['success_rate']:.1f}%")
    print(f"   googletrans 성공률: {stats['googletrans']['success_rate']:.1f}%")
    print(f"   캐시 크기: {stats['cache_size']}")
