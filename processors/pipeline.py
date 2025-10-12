#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - Main Pipeline
수집 → 필터링 → 번역 → 요약 → JSON 저장 전체 파이프라인 구현
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time

# 로컬 모듈 임포트
from config import Config
from collectors.news_media_collector import NewsMediaCollector
from collectors.practical_blog_collector import PracticalBlogCollector
from collectors.company_blog_collector import CompanyBlogCollector
from collectors.content_filter import ContentFilter
from processors.translator import Translator
from processors.summarizer import Summarizer

logger = logging.getLogger(__name__)

class DSNewsPipeline:
    """DS News Aggregator 전체 파이프라인 클래스"""
    
    def __init__(self, config: Config = None):
        """
        파이프라인 초기화
        
        Args:
            config: 설정 객체
        """
        self.config = config or Config()
        
        # PRD v2.0 - 각 단계별 컴포넌트 초기화
        self.news_media_collector = NewsMediaCollector(self.config)
        self.practical_blog_collector = PracticalBlogCollector(self.config)
        self.company_blog_collector = CompanyBlogCollector(self.config)
        self.content_filter = ContentFilter(self.config)
        self.translator = Translator(self.config)
        self.summarizer = Summarizer(self.config)
        
        # 파이프라인 통계
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'stage_times': {},
            'original_articles': 0,
            'filtered_articles': 0,
            'translated_articles': 0,
            'summarized_articles': 0,
            'final_articles': 0,
            'errors': []
        }
    
    def _log_stage_start(self, stage_name: str):
        """단계 시작 로깅"""
        logger.info(f"===== {stage_name} 시작 =====")
        self.pipeline_stats['stage_times'][stage_name + '_start'] = datetime.now(timezone.utc)
    
    def _log_stage_end(self, stage_name: str, result_count: int):
        """단계 완료 로깅"""
        end_time = datetime.now(timezone.utc)
        start_time = self.pipeline_stats['stage_times'][stage_name + '_start']
        duration = (end_time - start_time).total_seconds()
        
        self.pipeline_stats['stage_times'][stage_name + '_duration'] = duration
        
        logger.info(f"===== {stage_name} 완료: {result_count}개 글, {duration:.1f}초 =====")
    
    def step1_collect_articles(self) -> List[Dict[str, Any]]:
        """
        1단계: PRD v2.0 - 뉴스 미디어(50%) + 블로그(30%) + 기업(20%) 수집
        
        Returns:
            수집된 모든 글 목록
        """
        self._log_stage_start("글 수집")
        
        all_articles = []
        
        try:
            # 뉴스 미디어 수집 (50%)
            logger.info("뉴스 미디어에서 AI/ML 뉴스 수집 중...")
            news_articles = self.news_media_collector.collect(
                max_articles_per_source=self.config.NEWS_MEDIA_MAX_ARTICLES
            )
            all_articles.extend(news_articles)
            logger.info(f"뉴스 미디어 수집 완료: {len(news_articles)}개")
            
            # 실용 블로그 수집 (30%)
            logger.info("실용 블로그/꿀팁 플랫폼에서 수집 중...")
            blog_articles = self.practical_blog_collector.collect(
                max_articles_per_source=self.config.PRACTICAL_BLOG_MAX_ARTICLES
            )
            all_articles.extend(blog_articles)
            logger.info(f"실용 블로그 수집 완료: {len(blog_articles)}개")
            
            # 기업 블로그 수집 (20%)
            logger.info("기업 기술 블로그에서 수집 중...")
            company_articles = self.company_blog_collector.collect(
                max_articles_per_source=self.config.COMPANY_BLOG_MAX_ARTICLES
            )
            all_articles.extend(company_articles)
            logger.info(f"기업 블로그 수집 완료: {len(company_articles)}개")
            
            # 수집 비율 분석
            news_ratio = len(news_articles) / len(all_articles) * 100 if all_articles else 0
            blog_ratio = len(blog_articles) / len(all_articles) * 100 if all_articles else 0
            company_ratio = len(company_articles) / len(all_articles) * 100 if all_articles else 0
            
            logger.info(f"수집 비율 - 뉴스: {news_ratio:.1f}%, 블로그: {blog_ratio:.1f}%, 기업: {company_ratio:.1f}%")
            
        except Exception as e:
            error_msg = f"글 수집 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
        
        self.pipeline_stats['original_articles'] = len(all_articles)
        self._log_stage_end("글 수집", len(all_articles))
        
        return all_articles
    
    def step2_filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        2단계: PRD v2.0 콘텐츠 필터링 (뉴스 50%, 블로그 30%, 기업 20% 비율 유지)
        
        Args:
            articles: 필터링할 글 목록
            
        Returns:
            필터링된 글 목록
        """
        self._log_stage_start("콘텐츠 필터링")
        
        try:
            # 소스별 분류
            news_articles = [a for a in articles if a.get('source_id', '').startswith(('techcrunch', 'venturebeat', 'mit_tech', 'ai_times', 'zdnet', 'tech42'))]
            blog_articles = [a for a in articles if a.get('source_id', '').startswith(('towards_data', 'analytics_vidhya', 'kdnuggets', 'neptune'))]
            company_articles = [a for a in articles if a.get('source_id', '').startswith(('google_ai', 'openai', 'naver_d2', 'kakao_tech'))]
            
            logger.info(f"소스별 분류: 뉴스 {len(news_articles)}개, 블로그 {len(blog_articles)}개, 기업 {len(company_articles)}개")
            
            # PRD v2.0 비율에 따른 선별 (5-10개 총 목표)
            target_total = min(10, len(articles))  # 최대 10개
            
            # 뉴스 3-5개 (50%)
            news_target = max(3, min(5, int(target_total * self.config.NEWS_MEDIA_RATIO)))
            news_filtered = self.content_filter.get_top_articles(news_articles)[:news_target]
            
            # 블로그 2-3개 (30%)
            blog_target = max(2, min(3, int(target_total * self.config.PRACTICAL_BLOG_RATIO)))
            blog_filtered = self.content_filter.get_top_articles(blog_articles)[:blog_target]
            
            # 기업 1-2개 (20%)
            company_target = max(1, min(2, int(target_total * self.config.COMPANY_BLOG_RATIO)))
            company_filtered = self.content_filter.get_top_articles(company_articles)[:company_target]
            
            # 최종 결합
            filtered_articles = news_filtered + blog_filtered + company_filtered
            
            # 점수순 정렬
            filtered_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            self.pipeline_stats['filtered_articles'] = len(filtered_articles)
            
            logger.info(f"최종 선별: 뉴스 {len(news_filtered)}개, 블로그 {len(blog_filtered)}개, 기업 {len(company_filtered)}개 = 총 {len(filtered_articles)}개")
            
            # 필터링 분석 결과
            analysis = self.content_filter.analyze_filtering_results(articles, filtered_articles)
            logger.info(f"필터링 분석: {analysis}")
            
        except Exception as e:
            error_msg = f"콘텐츠 필터링 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
            # 실패시 기본 필터링 적용
            filtered_articles = self.content_filter.get_top_articles(articles)
        
        self._log_stage_end("콘텐츠 필터링", len(filtered_articles))
        return filtered_articles
    
    def step3_translate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        3단계: 글 번역 (영문만 한국어로 번역, 2000자 이상은 1000자만)
        
        Args:
            articles: 번역할 글 목록
            
        Returns:
            번역된 글 목록
        """
        self._log_stage_start("글 번역")
        
        try:
            # 번역이 필요한 글만 필터링
            articles_to_translate = [
                article for article in articles 
                if article.get('needs_translation', False)
            ]
            
            if articles_to_translate:
                logger.info(f"{len(articles_to_translate)}개 글 번역 시작...")
                translated_articles = self.translator.translate_articles_batch(articles_to_translate)
                
                # 번역 결과를 원래 리스트에 반영
                translated_dict = {a['id']: a for a in translated_articles}
                
                result_articles = []
                for article in articles:
                    if article['id'] in translated_dict:
                        result_articles.append(translated_dict[article['id']])
                    else:
                        result_articles.append(article)
                
                self.pipeline_stats['translated_articles'] = len(articles_to_translate)
            else:
                logger.info("번역이 필요한 글이 없습니다.")
                result_articles = articles
                self.pipeline_stats['translated_articles'] = 0
            
            # 번역 통계
            translation_stats = self.translator.get_translation_stats()
            logger.info(f"번역 통계: {translation_stats}")
            
        except Exception as e:
            error_msg = f"글 번역 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
            result_articles = articles  # 실패시 원본 반환
        
        self._log_stage_end("글 번역", len(result_articles))
        return result_articles
    
    def step4_summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        4단계: 글 요약 (Gemini Pro로 정확히 3문장 요약)
        
        Args:
            articles: 요약할 글 목록
            
        Returns:
            요약된 글 목록
        """
        self._log_stage_start("글 요약")
        
        try:
            logger.info(f"{len(articles)}개 글 요약 시작...")
            
            summarized_articles = self.summarizer.summarize_articles_batch(articles)
            self.pipeline_stats['summarized_articles'] = len(summarized_articles)
            
            # 요약 통계
            summary_stats = self.summarizer.get_summarization_stats()
            logger.info(f"요약 통계: {summary_stats}")
            
            # 킬스위치 상태 확인
            if summary_stats.get('killswitch_active', False):
                logger.warning("⚠️  Gemini API 킬스위치가 활성화되었습니다. API 상태를 확인하세요.")
            
        except Exception as e:
            error_msg = f"글 요약 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
            summarized_articles = articles  # 실패시 원본 반환
        
        self._log_stage_end("글 요약", len(summarized_articles))
        return summarized_articles
    
    def step5_save_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """
        5단계: JSON 저장 (사용자 요구사항 형식)
        
        Args:
            articles: 저장할 글 목록
            
        Returns:
            저장 성공 여부
        """
        self._log_stage_start("JSON 저장")
        
        try:
            # 데이터 디렉토리 생성
            os.makedirs(os.path.dirname(self.config.ARTICLES_FILE), exist_ok=True)
            
            # 사용자 요구사항에 맞는 JSON 형식
            today = datetime.now(timezone.utc).date().isoformat()
            
            output_data = {
                "date": today,
                "articles": articles
            }
            
            # 메인 파일 저장
            with open(self.config.ARTICLES_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            # 히스토리 파일 저장
            history_file = os.path.join(self.config.DATA_DIR, f'articles_{today}.json')
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.pipeline_stats['final_articles'] = len(articles)
            
            logger.info(f"JSON 저장 완료:")
            logger.info(f"  - 메인 파일: {self.config.ARTICLES_FILE}")
            logger.info(f"  - 히스토리: {history_file}")
            logger.info(f"  - 총 글 수: {len(articles)}개")
            
            self._log_stage_end("JSON 저장", len(articles))
            return True
            
        except Exception as e:
            error_msg = f"JSON 저장 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
            self._log_stage_end("JSON 저장", 0)
            return False
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        전체 파이프라인 실행: 수집 → 필터링 → 번역 → 요약 → JSON 저장
        
        Returns:
            파이프라인 실행 결과 통계
        """
        logger.info("🚀 DS News Aggregator 파이프라인 시작")
        self.pipeline_stats['start_time'] = datetime.now(timezone.utc)
        
        try:
            # 1단계: 글 수집
            articles = self.step1_collect_articles()
            
            if not articles:
                logger.warning("수집된 글이 없습니다. 파이프라인을 종료합니다.")
                return self.get_pipeline_stats()
            
            # 2단계: 콘텐츠 필터링
            articles = self.step2_filter_articles(articles)
            
            if not articles:
                logger.warning("필터링 후 남은 글이 없습니다. 파이프라인을 종료합니다.")
                return self.get_pipeline_stats()
            
            # 3단계: 글 번역
            articles = self.step3_translate_articles(articles)
            
            # 4단계: 글 요약
            articles = self.step4_summarize_articles(articles)
            
            # 5단계: JSON 저장
            success = self.step5_save_articles(articles)
            
            if success:
                logger.info("🎉 파이프라인 성공적으로 완료!")
            else:
                logger.error("💥 파이프라인 저장 단계에서 실패")
            
        except Exception as e:
            error_msg = f"파이프라인 실행 실패: {e}"
            logger.error(error_msg)
            self.pipeline_stats['errors'].append(error_msg)
        
        finally:
            self.pipeline_stats['end_time'] = datetime.now(timezone.utc)
        
        return self.get_pipeline_stats()
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        파이프라인 실행 통계 반환
        
        Returns:
            실행 통계 딕셔너리
        """
        stats = self.pipeline_stats.copy()
        
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['total_duration_seconds'] = duration.total_seconds()
            stats['total_duration_str'] = str(duration).split('.')[0]
        
        return stats
    
    def run_pipeline_step_by_step(self, save_intermediates: bool = True) -> Dict[str, Any]:
        """
        파이프라인을 단계별로 실행 (디버깅/개발용)
        
        Args:
            save_intermediates: 중간 결과 저장 여부
            
        Returns:
            실행 통계
        """
        logger.info("🔧 DS News Aggregator 파이프라인 단계별 실행")
        
        # 각 단계별 결과 저장
        step_results = {}
        
        # 1단계
        articles = self.step1_collect_articles()
        step_results['step1_collect'] = articles
        
        if save_intermediates:
            with open('data/step1_collected.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
        
        if not articles:
            return self.get_pipeline_stats()
        
        # 2단계
        articles = self.step2_filter_articles(articles)
        step_results['step2_filter'] = articles
        
        if save_intermediates:
            with open('data/step2_filtered.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
        
        if not articles:
            return self.get_pipeline_stats()
        
        # 3단계
        articles = self.step3_translate_articles(articles)
        step_results['step3_translate'] = articles
        
        if save_intermediates:
            with open('data/step3_translated.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
        
        # 4단계
        articles = self.step4_summarize_articles(articles)
        step_results['step4_summarize'] = articles
        
        if save_intermediates:
            with open('data/step4_summarized.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
        
        # 5단계
        self.step5_save_articles(articles)
        step_results['step5_final'] = articles
        
        logger.info("📊 단계별 파이프라인 완료!")
        return self.get_pipeline_stats()


# 편의 함수들
def run_ds_news_pipeline(config: Config = None) -> Dict[str, Any]:
    """
    DS News Aggregator 파이프라인 실행 편의 함수
    
    Args:
        config: 설정 객체
        
    Returns:
        실행 결과 통계
    """
    pipeline = DSNewsPipeline(config)
    return pipeline.run_full_pipeline()


def run_pipeline_with_custom_steps(collect: bool = True, 
                                  filter_content: bool = True,
                                  translate: bool = True, 
                                  summarize: bool = True,
                                  save: bool = True,
                                  config: Config = None) -> Dict[str, Any]:
    """
    사용자 정의 단계로 파이프라인 실행
    
    Args:
        collect: 수집 단계 실행 여부
        filter_content: 필터링 단계 실행 여부
        translate: 번역 단계 실행 여부
        summarize: 요약 단계 실행 여부
        save: 저장 단계 실행 여부
        config: 설정 객체
        
    Returns:
        실행 결과 통계
    """
    pipeline = DSNewsPipeline(config)
    pipeline.pipeline_stats['start_time'] = datetime.now(timezone.utc)
    
    articles = []
    
    try:
        if collect:
            articles = pipeline.step1_collect_articles()
            if not articles:
                return pipeline.get_pipeline_stats()
        
        if filter_content and articles:
            articles = pipeline.step2_filter_articles(articles)
            if not articles:
                return pipeline.get_pipeline_stats()
        
        if translate and articles:
            articles = pipeline.step3_translate_articles(articles)
        
        if summarize and articles:
            articles = pipeline.step4_summarize_articles(articles)
        
        if save and articles:
            pipeline.step5_save_articles(articles)
            
    except Exception as e:
        logger.error(f"사용자 정의 파이프라인 실행 실패: {e}")
        pipeline.pipeline_stats['errors'].append(str(e))
    
    finally:
        pipeline.pipeline_stats['end_time'] = datetime.now(timezone.utc)
    
    return pipeline.get_pipeline_stats()


if __name__ == "__main__":
    # 테스트 실행
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 명령줄 인자에 따른 실행 모드
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        # 디버그 모드: 단계별 실행
        pipeline = DSNewsPipeline()
        stats = pipeline.run_pipeline_step_by_step()
    else:
        # 일반 모드: 전체 실행
        stats = run_ds_news_pipeline()
    
    # 결과 출력
    print("\n" + "="*50)
    print("파이프라인 실행 결과")
    print("="*50)
    print(f"전체 소요 시간: {stats.get('total_duration_str', 'N/A')}")
    print(f"수집된 글: {stats['original_articles']}개")
    print(f"필터링된 글: {stats['filtered_articles']}개")
    print(f"번역된 글: {stats['translated_articles']}개")
    print(f"요약된 글: {stats['summarized_articles']}개")
    print(f"최종 저장된 글: {stats['final_articles']}개")
    
    if stats['errors']:
        print(f"오류 {len(stats['errors'])}개:")
        for error in stats['errors']:
            print(f"  - {error}")
    
    print("\n🎉 파이프라인 테스트 완료!")
