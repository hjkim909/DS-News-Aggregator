#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - 품질 검증 스크립트
필터링 정확도, 번역 품질, 요약 품질을 상세히 검증
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import re

# 프로젝트 모듈
from config import Config
from collectors.content_filter import ContentFilter
from processors.translator import Translator
from processors.summarizer import Summarizer

class QualityMetrics:
    """품질 메트릭 클래스"""
    
    def __init__(self):
        self.results = {
            'filtering': {
                'total_tested': 0,
                'correctly_filtered': 0,
                'false_positives': 0,
                'false_negatives': 0,
                'accuracy': 0,
                'precision': 0,
                'recall': 0
            },
            'translation': {
                'total_tested': 0,
                'successful': 0,
                'failed': 0,
                'skipped_korean': 0,
                'success_rate': 0,
                'avg_translation_time': 0
            },
            'summarization': {
                'total_tested': 0,
                'successful': 0,
                'three_sentences': 0,
                'keyword_coverage': 0,
                'success_rate': 0,
                'avg_summary_time': 0
            }
        }
    
    def calculate_filtering_metrics(self, test_results: List[Dict]):
        """필터링 메트릭 계산"""
        total = len(test_results)
        true_positives = sum(1 for r in test_results if r['expected'] == True and r['actual'] == True)
        true_negatives = sum(1 for r in test_results if r['expected'] == False and r['actual'] == False)
        false_positives = sum(1 for r in test_results if r['expected'] == False and r['actual'] == True)
        false_negatives = sum(1 for r in test_results if r['expected'] == True and r['actual'] == False)
        
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        self.results['filtering'].update({
            'total_tested': total,
            'correctly_filtered': true_positives + true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'accuracy': accuracy * 100,
            'precision': precision * 100,
            'recall': recall * 100
        })
    
    def save_report(self, filename: str = None):
        """품질 리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"quality_report_{timestamp}.json"
        
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.results,
            'summary': self._generate_summary()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _generate_summary(self) -> Dict[str, Any]:
        """품질 요약 생성"""
        filtering = self.results['filtering']
        translation = self.results['translation']
        summarization = self.results['summarization']
        
        return {
            'overall_score': (
                filtering['accuracy'] * 0.4 +
                translation['success_rate'] * 0.3 +
                summarization['success_rate'] * 0.3
            ),
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

class FilteringQualityTester:
    """필터링 품질 테스터"""
    
    def __init__(self, config: Config):
        self.config = config
        self.content_filter = ContentFilter(config)
        
    def create_test_dataset(self) -> List[Dict[str, Any]]:
        """테스트 데이터셋 생성"""
        
        # 고품질 글들 (통과해야 함)
        high_quality_articles = [
            {
                'id': 'hq_1',
                'title': 'LLM을 활용한 시계열 예측 방법론 완벽 가이드',
                'content': '본 연구에서는 대규모 언어 모델(LLM)을 시계열 데이터 예측에 활용하는 혁신적인 방법론을 제시합니다. Transformer 아키텍처를 기반으로 한 새로운 접근법으로 기존 ARIMA 모델 대비 15% 향상된 성능을 달성했습니다. 실제 금융 데이터셋을 통한 실험 결과, 제안된 방법이 다양한 시계열 패턴에서 일관된 예측 정확도를 보여줍니다.',
                'source': 'naver_d2',
                'expected': True,
                'category': '고품질_기술'
            },
            {
                'id': 'hq_2',
                'title': '머신러닝 모델 배포를 위한 MLOps 구현 전략',
                'content': '프로덕션 환경에서 머신러닝 모델을 안정적으로 배포하기 위한 MLOps 파이프라인 구축 방법을 단계별로 설명합니다. Docker 컨테이너화, Kubernetes 오케스트레이션, 모델 버저닝, A/B 테스팅까지 포함한 완전한 워크플로우를 제시합니다.',
                'source': 'kakao_tech',
                'expected': True,
                'category': '고품질_실무'
            },
            {
                'id': 'hq_3',
                'title': 'Deep Learning for Computer Vision: 실제 프로젝트 구현',
                'content': 'Computer Vision 프로젝트에서 딥러닝을 실제로 적용하는 과정을 상세히 다룹니다. CNN 아키텍처 설계부터 데이터 전처리, 모델 훈련, 성능 평가까지의 전체 파이프라인을 PyTorch를 사용하여 구현합니다.',
                'source': 'ai_times',
                'expected': True,
                'category': '고품질_튜토리얼'
            },
            {
                'id': 'hq_4',
                'title': 'Advanced Time Series Analysis with Python',
                'content': 'Python을 사용한 고급 시계열 분석 기법을 소개합니다. SARIMA, Prophet, LSTM까지 다양한 모델을 비교 분석하고, 실제 비즈니스 데이터에 적용한 사례를 통해 각 모델의 장단점을 설명합니다.',
                'source': 'reddit',
                'reddit_score': 42,
                'expected': True,
                'category': '고품질_분석'
            }
        ]
        
        # 중품질 글들 (경계선 케이스)
        medium_quality_articles = [
            {
                'id': 'mq_1',
                'title': '머신러닝 기초 개념 정리',
                'content': '머신러닝의 기본 개념들을 정리해보겠습니다. 지도학습, 비지도학습, 강화학습의 차이점과 각각의 대표적인 알고리즘들을 간단히 소개합니다.',
                'source': 'naver_d2',
                'expected': False,  # 너무 기초적
                'category': '중품질_기초'
            },
            {
                'id': 'mq_2',
                'title': 'AI 트렌드 2024',
                'content': '2024년 인공지능 분야의 주요 트렌드를 살펴보겠습니다. ChatGPT의 등장 이후 LLM 시장의 변화와 새로운 기술들을 정리했습니다.',
                'source': 'ai_times',
                'expected': False,  # 트렌드 정리만
                'category': '중품질_트렌드'
            }
        ]
        
        # 저품질 글들 (차단되어야 함)
        low_quality_articles = [
            {
                'id': 'lq_1',
                'title': '머신러닝 책 추천해주세요!!!',
                'content': '머신러닝을 공부하려고 하는데 어떤 책이 좋을까요? 추천해주세요! 초보자도 이해할 수 있는 책으로 부탁드립니다!!',
                'source': 'reddit',
                'reddit_score': 3,
                'expected': False,
                'category': '저품질_추천요청'
            },
            {
                'id': 'lq_2',
                'title': '이 모델 결과 어떻게 생각하세요?',
                'content': 'CNN 모델을 만들어봤는데 정확도가 85%가 나왔어요. 어떻게 생각하시나요? 더 개선할 방법이 있을까요?',
                'source': 'reddit',
                'reddit_score': 7,
                'expected': False,
                'category': '저품질_의견요청'
            },
            {
                'id': 'lq_3',
                'title': '파이썬 설치가 안돼요 ㅠㅠ',
                'content': '파이썬 설치하는데 자꾸 오류가 나요ㅠㅠ 어떻게 해야 하나요? 도와주세요!!!',
                'source': 'reddit',
                'reddit_score': 1,
                'expected': False,
                'category': '저품질_기술문제'
            },
            {
                'id': 'lq_4',
                'title': '데이터 사이언티스트 어때요?',
                'content': '데이터 사이언티스트로 전직하려고 하는데 어떨까요? 전망이 좋나요? 연봉은 어느 정도 되나요?',
                'source': 'reddit',
                'reddit_score': 2,
                'expected': False,
                'category': '저품질_진로상담'
            }
        ]
        
        return high_quality_articles + medium_quality_articles + low_quality_articles
    
    def test_filtering_accuracy(self) -> List[Dict[str, Any]]:
        """필터링 정확도 테스트"""
        print("🔍 필터링 정확도 테스트 시작...")
        
        test_dataset = self.create_test_dataset()
        results = []
        
        for article in test_dataset:
            # 점수 계산
            if article['source'] == 'reddit':
                score = self.content_filter._calculate_reddit_score(
                    article['title'],
                    article['content'],
                    article.get('reddit_score', 0)
                )
            else:
                score = self.content_filter._calculate_blog_score(
                    article['title'],
                    article['content'],
                    article['source']
                )
            
            # 필터링 결과 (70점 이상 통과)
            passed = score >= self.config.MIN_SCORE_THRESHOLD
            expected = article['expected']
            
            result = {
                'id': article['id'],
                'title': article['title'][:50] + '...',
                'category': article['category'],
                'score': score,
                'expected': expected,
                'actual': passed,
                'correct': expected == passed
            }
            
            results.append(result)
            
            status = "✅ 정답" if result['correct'] else "❌ 오답"
            print(f"  {article['id']}: {score:>3.0f}점 -> {'통과' if passed else '차단'} ({article['category']}) {status}")
        
        return results
    
    def analyze_filtering_errors(self, results: List[Dict]) -> Dict[str, Any]:
        """필터링 오류 분석"""
        errors = [r for r in results if not r['correct']]
        
        error_analysis = {
            'false_positives': [r for r in errors if r['actual'] == True and r['expected'] == False],
            'false_negatives': [r for r in errors if r['actual'] == False and r['expected'] == True],
            'common_patterns': {}
        }
        
        print(f"\n🔍 오류 분석 ({len(errors)}개 오류):")
        
        if error_analysis['false_positives']:
            print(f"  🔴 거짓 양성 (잘못 통과): {len(error_analysis['false_positives'])}개")
            for fp in error_analysis['false_positives']:
                print(f"    - {fp['title']} ({fp['score']:.0f}점)")
        
        if error_analysis['false_negatives']:
            print(f"  🔴 거짓 음성 (잘못 차단): {len(error_analysis['false_negatives'])}개")
            for fn in error_analysis['false_negatives']:
                print(f"    - {fn['title']} ({fn['score']:.0f}점)")
        
        return error_analysis

class TranslationQualityTester:
    """번역 품질 테스터"""
    
    def __init__(self, config: Config):
        self.config = config
        self.translator = Translator(config)
        
    def create_translation_testset(self) -> List[Dict[str, Any]]:
        """번역 테스트 데이터셋 생성"""
        return [
            {
                'id': 'tr_1',
                'text': 'Machine learning algorithms automatically identify patterns in large datasets.',
                'expected_keywords': ['머신러닝', '알고리즘', '패턴', '데이터'],
                'difficulty': 'easy'
            },
            {
                'id': 'tr_2', 
                'text': 'Deep neural networks with convolutional layers excel at computer vision tasks.',
                'expected_keywords': ['딥', '신경망', '컨볼루션', '컴퓨터 비전'],
                'difficulty': 'medium'
            },
            {
                'id': 'tr_3',
                'text': 'Transformer architectures leverage self-attention mechanisms to process sequential data efficiently.',
                'expected_keywords': ['트랜스포머', '셀프어텐션', '순차', '데이터'],
                'difficulty': 'hard'
            },
            {
                'id': 'tr_4',
                'text': 'Gradient descent optimization iteratively updates model parameters to minimize loss functions.',
                'expected_keywords': ['경사', '하강', '최적화', '매개변수', '손실'],
                'difficulty': 'hard'
            },
            {
                'id': 'tr_5',
                'text': 'Cross-validation techniques help evaluate model performance and prevent overfitting.',
                'expected_keywords': ['교차', '검증', '성능', '과적합'],
                'difficulty': 'medium'
            },
            {
                'id': 'tr_6',
                'text': 'Time series forecasting models predict future values based on historical patterns.',
                'expected_keywords': ['시계열', '예측', '미래', '패턴'],
                'difficulty': 'easy'
            }
        ]
    
    def test_translation_quality(self) -> List[Dict[str, Any]]:
        """번역 품질 테스트"""
        print("🌐 번역 품질 테스트 시작...")
        
        test_dataset = self.create_translation_testset()
        results = []
        
        for test_case in test_dataset:
            print(f"  📝 {test_case['id']} ({test_case['difficulty']})...")
            
            start_time = time.time()
            
            try:
                result = self.translator.translate_text(test_case['text'], 'ko')
                
                translation_time = time.time() - start_time
                
                if result['success']:
                    translated_text = result['translated_text']
                    
                    # 키워드 커버리지 계산
                    keyword_coverage = 0
                    for keyword in test_case['expected_keywords']:
                        if keyword in translated_text:
                            keyword_coverage += 1
                    
                    coverage_rate = keyword_coverage / len(test_case['expected_keywords']) * 100
                    
                    # 품질 점수 계산
                    quality_score = min(100, coverage_rate * 1.2 + 20)  # 기본 20점 + 키워드 보너스
                    
                    test_result = {
                        'id': test_case['id'],
                        'original': test_case['text'][:60] + '...',
                        'translated': translated_text[:60] + '...',
                        'difficulty': test_case['difficulty'],
                        'success': True,
                        'keyword_coverage': coverage_rate,
                        'quality_score': quality_score,
                        'translation_time': translation_time,
                        'service': result.get('service', 'unknown')
                    }
                    
                    print(f"    ✅ 번역 성공 (품질: {quality_score:.1f}점, 키워드: {keyword_coverage}/{len(test_case['expected_keywords'])})")
                    print(f"       원문: {test_case['text'][:80]}...")
                    print(f"       번역: {translated_text[:80]}...")
                
                else:
                    test_result = {
                        'id': test_case['id'],
                        'original': test_case['text'][:60] + '...',
                        'translated': '',
                        'difficulty': test_case['difficulty'],
                        'success': False,
                        'keyword_coverage': 0,
                        'quality_score': 0,
                        'translation_time': translation_time,
                        'error': result.get('error', 'Unknown error')
                    }
                    
                    print(f"    ❌ 번역 실패: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                test_result = {
                    'id': test_case['id'],
                    'original': test_case['text'][:60] + '...',
                    'translated': '',
                    'difficulty': test_case['difficulty'],
                    'success': False,
                    'keyword_coverage': 0,
                    'quality_score': 0,
                    'translation_time': time.time() - start_time,
                    'error': str(e)
                }
                
                print(f"    💥 번역 오류: {e}")
            
            results.append(test_result)
            time.sleep(1)  # API 제한 대응
        
        return results
    
    def analyze_translation_quality(self, results: List[Dict]) -> Dict[str, Any]:
        """번역 품질 분석"""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        analysis = {
            'success_rate': len(successful) / len(results) * 100 if results else 0,
            'avg_quality_score': sum(r['quality_score'] for r in successful) / len(successful) if successful else 0,
            'avg_translation_time': sum(r['translation_time'] for r in results) / len(results) if results else 0,
            'difficulty_breakdown': {}
        }
        
        # 난이도별 분석
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_results = [r for r in results if r['difficulty'] == difficulty]
            if difficulty_results:
                difficulty_success = [r for r in difficulty_results if r['success']]
                analysis['difficulty_breakdown'][difficulty] = {
                    'total': len(difficulty_results),
                    'successful': len(difficulty_success),
                    'success_rate': len(difficulty_success) / len(difficulty_results) * 100,
                    'avg_quality': sum(r['quality_score'] for r in difficulty_success) / len(difficulty_success) if difficulty_success else 0
                }
        
        print(f"\n📊 번역 품질 분석:")
        print(f"  전체 성공률: {analysis['success_rate']:.1f}%")
        print(f"  평균 품질점수: {analysis['avg_quality_score']:.1f}점")
        print(f"  평균 번역시간: {analysis['avg_translation_time']:.3f}초")
        
        print(f"  난이도별 성공률:")
        for difficulty, stats in analysis['difficulty_breakdown'].items():
            print(f"    {difficulty}: {stats['success_rate']:.1f}% ({stats['successful']}/{stats['total']})")
        
        return analysis

class SummarizationQualityTester:
    """요약 품질 테스터"""
    
    def __init__(self, config: Config):
        self.config = config
        self.summarizer = Summarizer(config)
    
    def create_summarization_testset(self) -> List[Dict[str, Any]]:
        """요약 테스트 데이터셋 생성"""
        return [
            {
                'id': 'sum_1',
                'title': '딥러닝을 활용한 자연어 처리',
                'content': '''자연어 처리(Natural Language Processing, NLP)는 컴퓨터가 인간의 언어를 이해하고 처리할 수 있도록 하는 인공지능 분야입니다. 최근 딥러닝 기술의 발전으로 NLP 분야에서 혁신적인 성과를 거두고 있습니다. 

특히 Transformer 아키텍처의 등장은 NLP 분야의 패러다임을 완전히 바꾸어 놓았습니다. BERT, GPT 같은 대규모 언어 모델들이 다양한 NLP 태스크에서 인간 수준의 성능을 보여주고 있습니다. 

이러한 기술들은 번역, 감정 분석, 텍스트 요약, 질의응답 등 실제 비즈니스 영역에서도 광범위하게 활용되고 있습니다. 앞으로 더욱 발전된 언어 모델들이 등장할 것으로 예상되며, NLP 기술은 우리 일상생활에 더욱 깊숙이 들어올 것입니다.''',
                'key_concepts': ['NLP', '딥러닝', 'Transformer', 'BERT', 'GPT', '언어모델'],
                'expected_sentences': 3,
                'difficulty': 'medium'
            },
            {
                'id': 'sum_2',
                'title': '시계열 데이터 분석 방법론',
                'content': '''시계열 데이터 분석은 시간에 따라 변화하는 데이터의 패턴을 파악하고 미래를 예측하는 분석 기법입니다. 주식 가격, 날씨 데이터, 판매량 등 시간의 흐름에 따라 수집되는 대부분의 데이터가 시계열 데이터에 해당합니다.

전통적인 시계열 분석 방법으로는 ARIMA, 지수 평활법, 계절 분해 등이 있습니다. 이러한 방법들은 선형적인 패턴을 잘 포착하지만, 복잡한 비선형 패턴을 처리하는 데는 한계가 있습니다.

최근에는 LSTM, GRU와 같은 순환 신경망(RNN) 계열의 딥러닝 모델들이 시계열 예측에 활용되고 있습니다. 특히 Prophet, Transformer 기반 모델들은 계절성과 트렌드를 효과적으로 학습하여 기존 방법보다 우수한 성능을 보여줍니다. 실제 비즈니스에서는 이러한 기법들을 조합하여 수요 예측, 재고 관리, 리스크 분석 등에 활용하고 있습니다.''',
                'key_concepts': ['시계열', 'ARIMA', 'LSTM', 'Prophet', '예측', '패턴'],
                'expected_sentences': 3,
                'difficulty': 'medium'
            },
            {
                'id': 'sum_3',
                'title': 'MLOps와 모델 배포 전략',
                'content': '''MLOps(Machine Learning Operations)는 머신러닝 모델의 개발부터 배포, 모니터링까지의 전체 생명주기를 효율적으로 관리하는 방법론입니다. DevOps의 개념을 머신러닝 영역에 적용한 것으로, 모델의 지속적 통합과 배포를 목표로 합니다.

MLOps의 핵심 구성 요소는 다음과 같습니다. 첫째, 버전 관리 시스템을 통한 코드와 데이터의 추적 가능성 확보입니다. Git과 DVC를 활용하여 실험과 데이터를 체계적으로 관리할 수 있습니다. 둘째, 자동화된 파이프라인 구축입니다. CI/CD 파이프라인을 통해 모델 훈련부터 배포까지 자동화할 수 있습니다. 

셋째, 모니터링과 로깅 시스템입니다. 배포된 모델의 성능을 실시간으로 모니터링하고, 데이터 드리프트나 모델 성능 저하를 빠르게 감지할 수 있습니다. 넷째, 컨테이너화와 오케스트레이션입니다. Docker와 Kubernetes를 활용하여 모델을 안정적으로 배포하고 확장할 수 있습니다.

실제 기업에서는 Kubeflow, MLflow, Amazon SageMaker 등의 플랫폼을 활용하여 MLOps를 구현하고 있습니다.''',
                'key_concepts': ['MLOps', 'DevOps', '배포', '모니터링', '자동화', 'Docker'],
                'expected_sentences': 3,
                'difficulty': 'hard'
            }
        ]
    
    def test_summarization_quality(self) -> List[Dict[str, Any]]:
        """요약 품질 테스트"""
        print("📄 요약 품질 테스트 시작...")
        
        test_dataset = self.create_summarization_testset()
        results = []
        
        for test_case in test_dataset:
            print(f"  📝 {test_case['id']} ({test_case['difficulty']})...")
            
            start_time = time.time()
            
            try:
                result = self.summarizer.summarize_text(test_case['title'], test_case['content'])
                
                summarization_time = time.time() - start_time
                
                if result['success']:
                    summary = result['summary']
                    sentences_count = result['sentences_count']
                    
                    # 키워드 커버리지 계산
                    keyword_coverage = 0
                    for concept in test_case['key_concepts']:
                        if concept.lower() in summary.lower():
                            keyword_coverage += 1
                    
                    coverage_rate = keyword_coverage / len(test_case['key_concepts']) * 100
                    
                    # 문장 수 정확도
                    sentence_accuracy = 100 if sentences_count == 3 else max(0, 100 - abs(sentences_count - 3) * 20)
                    
                    # 전체 품질 점수
                    quality_score = (coverage_rate * 0.6 + sentence_accuracy * 0.4)
                    
                    test_result = {
                        'id': test_case['id'],
                        'title': test_case['title'],
                        'summary': summary,
                        'difficulty': test_case['difficulty'],
                        'success': True,
                        'sentences_count': sentences_count,
                        'expected_sentences': test_case['expected_sentences'],
                        'keyword_coverage': coverage_rate,
                        'quality_score': quality_score,
                        'summarization_time': summarization_time,
                        'service': result.get('service', 'unknown')
                    }
                    
                    print(f"    ✅ 요약 성공 (품질: {quality_score:.1f}점)")
                    print(f"       문장수: {sentences_count}/3, 키워드: {keyword_coverage}/{len(test_case['key_concepts'])}")
                    print(f"       요약: {summary[:100]}...")
                
                else:
                    test_result = {
                        'id': test_case['id'],
                        'title': test_case['title'],
                        'summary': '',
                        'difficulty': test_case['difficulty'],
                        'success': False,
                        'sentences_count': 0,
                        'expected_sentences': test_case['expected_sentences'],
                        'keyword_coverage': 0,
                        'quality_score': 0,
                        'summarization_time': summarization_time,
                        'error': result.get('error', 'Unknown error')
                    }
                    
                    print(f"    ❌ 요약 실패: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                test_result = {
                    'id': test_case['id'],
                    'title': test_case['title'],
                    'summary': '',
                    'difficulty': test_case['difficulty'],
                    'success': False,
                    'sentences_count': 0,
                    'expected_sentences': test_case['expected_sentences'],
                    'keyword_coverage': 0,
                    'quality_score': 0,
                    'summarization_time': time.time() - start_time,
                    'error': str(e)
                }
                
                print(f"    💥 요약 오류: {e}")
            
            results.append(test_result)
            time.sleep(3)  # Gemini API 제한 대응
        
        return results
    
    def analyze_summarization_quality(self, results: List[Dict]) -> Dict[str, Any]:
        """요약 품질 분석"""
        successful = [r for r in results if r['success']]
        three_sentence_summaries = [r for r in successful if r['sentences_count'] == 3]
        
        analysis = {
            'success_rate': len(successful) / len(results) * 100 if results else 0,
            'three_sentence_rate': len(three_sentence_summaries) / len(results) * 100 if results else 0,
            'avg_quality_score': sum(r['quality_score'] for r in successful) / len(successful) if successful else 0,
            'avg_keyword_coverage': sum(r['keyword_coverage'] for r in successful) / len(successful) if successful else 0,
            'avg_summarization_time': sum(r['summarization_time'] for r in results) / len(results) if results else 0,
            'difficulty_breakdown': {}
        }
        
        # 난이도별 분석
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_results = [r for r in results if r['difficulty'] == difficulty]
            if difficulty_results:
                difficulty_success = [r for r in difficulty_results if r['success']]
                analysis['difficulty_breakdown'][difficulty] = {
                    'total': len(difficulty_results),
                    'successful': len(difficulty_success),
                    'success_rate': len(difficulty_success) / len(difficulty_results) * 100,
                    'avg_quality': sum(r['quality_score'] for r in difficulty_success) / len(difficulty_success) if difficulty_success else 0
                }
        
        print(f"\n📊 요약 품질 분석:")
        print(f"  전체 성공률: {analysis['success_rate']:.1f}%")
        print(f"  3문장 요약률: {analysis['three_sentence_rate']:.1f}%")
        print(f"  평균 품질점수: {analysis['avg_quality_score']:.1f}점")
        print(f"  평균 키워드 커버리지: {analysis['avg_keyword_coverage']:.1f}%")
        print(f"  평균 요약시간: {analysis['avg_summarization_time']:.3f}초")
        
        return analysis

def run_quality_tests():
    """전체 품질 테스트 실행"""
    print("🎯 DS News Aggregator 품질 검증 테스트 시작")
    print("="*60)
    
    config = Config()
    metrics = QualityMetrics()
    
    try:
        # 1. 필터링 품질 테스트
        print("\n1️⃣ 필터링 품질 테스트")
        print("-" * 30)
        
        filtering_tester = FilteringQualityTester(config)
        filtering_results = filtering_tester.test_filtering_accuracy()
        filtering_analysis = filtering_tester.analyze_filtering_errors(filtering_results)
        
        metrics.calculate_filtering_metrics(filtering_results)
        
        # 2. 번역 품질 테스트
        print("\n2️⃣ 번역 품질 테스트")
        print("-" * 30)
        
        translation_tester = TranslationQualityTester(config)
        translation_results = translation_tester.test_translation_quality()
        translation_analysis = translation_tester.analyze_translation_quality(translation_results)
        
        metrics.results['translation'].update({
            'total_tested': len(translation_results),
            'successful': len([r for r in translation_results if r['success']]),
            'success_rate': translation_analysis['success_rate'],
            'avg_translation_time': translation_analysis['avg_translation_time']
        })
        
        # 3. 요약 품질 테스트
        print("\n3️⃣ 요약 품질 테스트")
        print("-" * 30)
        
        summarization_tester = SummarizationQualityTester(config)
        summarization_results = summarization_tester.test_summarization_quality()
        summarization_analysis = summarization_tester.analyze_summarization_quality(summarization_results)
        
        metrics.results['summarization'].update({
            'total_tested': len(summarization_results),
            'successful': len([r for r in summarization_results if r['success']]),
            'success_rate': summarization_analysis['success_rate'],
            'three_sentences': summarization_analysis['three_sentence_rate'],
            'keyword_coverage': summarization_analysis['avg_keyword_coverage'],
            'avg_summary_time': summarization_analysis['avg_summarization_time']
        })
        
        # 최종 리포트 생성
        print("\n📊 최종 품질 리포트")
        print("="*60)
        
        print(f"🔍 필터링 품질:")
        print(f"   정확도: {metrics.results['filtering']['accuracy']:.1f}%")
        print(f"   정밀도: {metrics.results['filtering']['precision']:.1f}%")
        print(f"   재현율: {metrics.results['filtering']['recall']:.1f}%")
        
        print(f"🌐 번역 품질:")
        print(f"   성공률: {metrics.results['translation']['success_rate']:.1f}%")
        print(f"   평균 시간: {metrics.results['translation']['avg_translation_time']:.3f}초")
        
        print(f"📄 요약 품질:")
        print(f"   성공률: {metrics.results['summarization']['success_rate']:.1f}%")
        print(f"   3문장 비율: {metrics.results['summarization']['three_sentences']:.1f}%")
        print(f"   키워드 커버리지: {metrics.results['summarization']['keyword_coverage']:.1f}%")
        
        # 전체 품질 점수
        overall_score = (
            metrics.results['filtering']['accuracy'] * 0.4 +
            metrics.results['translation']['success_rate'] * 0.3 +
            metrics.results['summarization']['success_rate'] * 0.3
        )
        
        print(f"\n🎯 전체 품질 점수: {overall_score:.1f}점")
        
        if overall_score >= 80:
            print("🎉 우수한 품질 - 배포 준비 완료!")
        elif overall_score >= 70:
            print("✅ 양호한 품질 - 일부 개선 필요")
        else:
            print("⚠️  품질 개선 필요 - 추가 최적화 권장")
        
        # 리포트 저장
        report_path = metrics.save_report()
        print(f"\n📋 상세 리포트: {report_path}")
        
        return overall_score >= 70
        
    except Exception as e:
        print(f"💥 품질 테스트 실패: {e}")
        return False

if __name__ == '__main__':
    success = run_quality_tests()
    sys.exit(0 if success else 1)
