#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - 성능 체크 스크립트
메모리 사용량, API 호출 횟수, 실행 시간을 상세하게 추적
"""

import time
import psutil
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import threading
import matplotlib.pyplot as plt
import seaborn as sns

# 프로젝트 모듈
from config import Config
from processors.pipeline import DSNewsPipeline

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, name: str = "Performance Test"):
        self.name = name
        self.process = psutil.Process()
        self.monitoring = False
        self.data = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_mb': [],
            'memory_percent': [],
            'io_read_bytes': [],
            'io_write_bytes': [],
            'network_sent': [],
            'network_recv': []
        }
        self.start_time = None
        self.end_time = None
        self.api_calls = {
            'reddit': [],
            'gemini': [],
            'googletrans': [],
            'rss': []
        }
        
    def start(self):
        """모니터링 시작"""
        self.start_time = time.time()
        self.monitoring = True
        
        # 초기 네트워크/IO 상태
        self.initial_io = self.process.io_counters()
        self.initial_net = psutil.net_io_counters()
        
        # 백그라운드 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🔍 성능 모니터링 시작: {self.name}")
    
    def stop(self):
        """모니터링 중지"""
        self.end_time = time.time()
        self.monitoring = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
            
        print(f"⏹️  성능 모니터링 종료: {self.name}")
        
    def _monitor_loop(self):
        """백그라운드 모니터링 루프"""
        while self.monitoring:
            try:
                timestamp = time.time() - self.start_time
                
                # CPU 사용률
                cpu_percent = self.process.cpu_percent(interval=0.1)
                
                # 메모리 사용량
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = self.process.memory_percent()
                
                # I/O 정보
                current_io = self.process.io_counters()
                io_read = (current_io.read_bytes - self.initial_io.read_bytes) / 1024 / 1024
                io_write = (current_io.write_bytes - self.initial_io.write_bytes) / 1024 / 1024
                
                # 네트워크 정보 (전체 시스템)
                current_net = psutil.net_io_counters()
                net_sent = (current_net.bytes_sent - self.initial_net.bytes_sent) / 1024 / 1024
                net_recv = (current_net.bytes_recv - self.initial_net.bytes_recv) / 1024 / 1024
                
                # 데이터 저장
                self.data['timestamps'].append(timestamp)
                self.data['cpu_percent'].append(cpu_percent)
                self.data['memory_mb'].append(memory_mb)
                self.data['memory_percent'].append(memory_percent)
                self.data['io_read_bytes'].append(io_read)
                self.data['io_write_bytes'].append(io_write)
                self.data['network_sent'].append(net_sent)
                self.data['network_recv'].append(net_recv)
                
                time.sleep(1)  # 1초 간격
                
            except Exception as e:
                print(f"⚠️  모니터링 오류: {e}")
                break
    
    def record_api_call(self, api_type: str, duration: float, success: bool, details: str = ""):
        """API 호출 기록"""
        if api_type in self.api_calls:
            self.api_calls[api_type].append({
                'timestamp': time.time() - (self.start_time or time.time()),
                'duration': duration,
                'success': success,
                'details': details
            })
    
    def get_duration(self) -> float:
        """총 실행 시간"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def get_memory_stats(self) -> Dict[str, float]:
        """메모리 통계"""
        if not self.data['memory_mb']:
            return {}
            
        memory_data = self.data['memory_mb']
        return {
            'min_mb': min(memory_data),
            'max_mb': max(memory_data),
            'avg_mb': sum(memory_data) / len(memory_data),
            'peak_usage_mb': max(memory_data) - min(memory_data),
            'final_mb': memory_data[-1] if memory_data else 0
        }
    
    def get_cpu_stats(self) -> Dict[str, float]:
        """CPU 통계"""
        if not self.data['cpu_percent']:
            return {}
            
        cpu_data = self.data['cpu_percent']
        return {
            'min_percent': min(cpu_data),
            'max_percent': max(cpu_data),
            'avg_percent': sum(cpu_data) / len(cpu_data),
            'peak_usage': max(cpu_data)
        }
    
    def get_api_stats(self) -> Dict[str, Any]:
        """API 호출 통계"""
        stats = {}
        
        for api_type, calls in self.api_calls.items():
            if calls:
                durations = [call['duration'] for call in calls]
                successes = [call['success'] for call in calls]
                
                stats[api_type] = {
                    'total_calls': len(calls),
                    'successful_calls': sum(successes),
                    'success_rate': sum(successes) / len(successes) * 100 if successes else 0,
                    'avg_duration': sum(durations) / len(durations) if durations else 0,
                    'total_duration': sum(durations),
                    'min_duration': min(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0
                }
            else:
                stats[api_type] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'success_rate': 0,
                    'avg_duration': 0,
                    'total_duration': 0,
                    'min_duration': 0,
                    'max_duration': 0
                }
        
        return stats
    
    def save_report(self, filename: str = None):
        """성능 리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_report_{timestamp}.json"
        
        report = {
            'test_name': self.name,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration(),
            'memory_stats': self.get_memory_stats(),
            'cpu_stats': self.get_cpu_stats(),
            'api_stats': self.get_api_stats(),
            'raw_data': self.data
        }
        
        os.makedirs('reports', exist_ok=True)
        report_path = os.path.join('reports', filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 성능 리포트 저장: {report_path}")
        return report_path
    
    def generate_charts(self, output_dir: str = "reports/charts"):
        """성능 차트 생성"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # GUI 없는 환경용
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 스타일 설정
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. 메모리 사용량 차트
            plt.figure(figsize=(12, 6))
            plt.plot(self.data['timestamps'], self.data['memory_mb'], 'b-', linewidth=2, label='메모리 사용량 (MB)')
            plt.fill_between(self.data['timestamps'], self.data['memory_mb'], alpha=0.3)
            plt.xlabel('시간 (초)')
            plt.ylabel('메모리 (MB)')
            plt.title(f'{self.name} - 메모리 사용량 변화')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'memory_usage.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. CPU 사용률 차트
            plt.figure(figsize=(12, 6))
            plt.plot(self.data['timestamps'], self.data['cpu_percent'], 'r-', linewidth=2, label='CPU 사용률 (%)')
            plt.fill_between(self.data['timestamps'], self.data['cpu_percent'], alpha=0.3)
            plt.xlabel('시간 (초)')
            plt.ylabel('CPU 사용률 (%)')
            plt.title(f'{self.name} - CPU 사용률 변화')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'cpu_usage.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. I/O 활동 차트
            plt.figure(figsize=(12, 6))
            plt.plot(self.data['timestamps'], self.data['io_read_bytes'], 'g-', linewidth=2, label='읽기 (MB)')
            plt.plot(self.data['timestamps'], self.data['io_write_bytes'], 'orange', linewidth=2, label='쓰기 (MB)')
            plt.xlabel('시간 (초)')
            plt.ylabel('I/O (MB)')
            plt.title(f'{self.name} - I/O 활동')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'io_activity.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # 4. API 호출 통계 차트
            api_stats = self.get_api_stats()
            if any(stats['total_calls'] > 0 for stats in api_stats.values()):
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # API 호출 횟수
                apis = list(api_stats.keys())
                calls = [api_stats[api]['total_calls'] for api in apis]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                
                ax1.bar(apis, calls, color=colors[:len(apis)])
                ax1.set_title('API 호출 횟수')
                ax1.set_ylabel('호출 수')
                ax1.tick_params(axis='x', rotation=45)
                
                # API 성공률
                success_rates = [api_stats[api]['success_rate'] for api in apis]
                ax2.bar(apis, success_rates, color=colors[:len(apis)])
                ax2.set_title('API 성공률 (%)')
                ax2.set_ylabel('성공률 (%)')
                ax2.set_ylim(0, 100)
                ax2.tick_params(axis='x', rotation=45)
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'api_stats.png'), dpi=300, bbox_inches='tight')
                plt.close()
            
            print(f"📈 성능 차트 생성 완료: {output_dir}")
            
        except ImportError:
            print("📊 차트 생성을 위해 matplotlib과 seaborn을 설치하세요: pip install matplotlib seaborn")
        except Exception as e:
            print(f"📈 차트 생성 실패: {e}")
    
    def print_summary(self):
        """성능 요약 출력"""
        print(f"\n📊 성능 요약 - {self.name}")
        print("="*50)
        
        # 기본 정보
        duration = self.get_duration()
        print(f"⏱️  총 실행 시간: {duration:.2f}초 ({duration/60:.1f}분)")
        
        # 메모리 통계
        memory_stats = self.get_memory_stats()
        if memory_stats:
            print(f"💾 메모리 사용량:")
            print(f"   최소: {memory_stats['min_mb']:.1f}MB")
            print(f"   최대: {memory_stats['max_mb']:.1f}MB")
            print(f"   평균: {memory_stats['avg_mb']:.1f}MB")
            print(f"   피크 증가: {memory_stats['peak_usage_mb']:.1f}MB")
        
        # CPU 통계
        cpu_stats = self.get_cpu_stats()
        if cpu_stats:
            print(f"🔥 CPU 사용률:")
            print(f"   최소: {cpu_stats['min_percent']:.1f}%")
            print(f"   최대: {cpu_stats['max_percent']:.1f}%")
            print(f"   평균: {cpu_stats['avg_percent']:.1f}%")
        
        # API 통계
        api_stats = self.get_api_stats()
        total_api_calls = sum(stats['total_calls'] for stats in api_stats.values())
        if total_api_calls > 0:
            print(f"🌐 API 호출 통계:")
            print(f"   총 호출: {total_api_calls}회")
            
            for api, stats in api_stats.items():
                if stats['total_calls'] > 0:
                    print(f"   {api}: {stats['total_calls']}회 "
                          f"(성공률 {stats['success_rate']:.1f}%, "
                          f"평균 {stats['avg_duration']:.3f}초)")
        
        # 성능 목표 체크
        print(f"\n🎯 성능 목표 체크:")
        
        # 10분 이내 목표
        target_duration = 600  # 10분
        duration_status = "✅" if duration <= target_duration else "❌"
        print(f"   {duration_status} 실행시간: {duration:.1f}초 / {target_duration}초")
        
        # 500MB 이하 메모리 목표
        if memory_stats:
            max_memory = memory_stats['max_mb']
            memory_target = 500
            memory_status = "✅" if max_memory <= memory_target else "❌"
            print(f"   {memory_status} 메모리: {max_memory:.1f}MB / {memory_target}MB")
        
        # API 성공률 90% 이상 목표
        if api_stats:
            overall_success_rate = sum(stats['successful_calls'] for stats in api_stats.values()) / max(total_api_calls, 1) * 100
            api_status = "✅" if overall_success_rate >= 90 else "❌"
            print(f"   {api_status} API 성공률: {overall_success_rate:.1f}% / 90%")

class EnhancedPipeline(DSNewsPipeline):
    """성능 모니터링이 가능한 파이프라인"""
    
    def __init__(self, config=None, monitor=None):
        super().__init__(config)
        self.monitor = monitor
    
    def _monitor_api_call(self, api_type: str, func, *args, **kwargs):
        """API 호출 모니터링"""
        if not self.monitor:
            return func(*args, **kwargs)
            
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            self.monitor.record_api_call(api_type, duration, True, f"Success: {type(result)}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.record_api_call(api_type, duration, False, f"Error: {str(e)}")
            raise

def run_performance_test():
    """전체 성능 테스트 실행"""
    print("🚀 DS News Aggregator 성능 테스트 시작")
    print("="*60)
    
    # 성능 모니터 초기화
    monitor = PerformanceMonitor("DS News Pipeline Performance Test")
    
    try:
        # 모니터링 시작
        monitor.start()
        
        # 강화된 파이프라인 실행
        config = Config()
        pipeline = EnhancedPipeline(config, monitor)
        
        print("📊 성능 최적화 테스트 모드로 파이프라인 실행...")
        
        # 테스트용 소량 데이터로 전체 파이프라인 실행
        stats = pipeline.run_full_pipeline()
        
        print(f"🎉 파이프라인 실행 완료!")
        print(f"📊 처리된 글: {stats.get('final_articles', 0)}개")
        
    except KeyboardInterrupt:
        print("\n⏹️  성능 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"💥 성능 테스트 실패: {e}")
    finally:
        # 모니터링 중지
        monitor.stop()
        
        # 결과 출력
        monitor.print_summary()
        
        # 리포트 저장
        report_path = monitor.save_report()
        
        # 차트 생성
        monitor.generate_charts()
        
        print(f"\n📋 상세 리포트: {report_path}")
        print("📈 성능 차트: reports/charts/")

def run_memory_stress_test():
    """메모리 스트레스 테스트"""
    print("💾 메모리 스트레스 테스트 시작")
    
    monitor = PerformanceMonitor("Memory Stress Test")
    monitor.start()
    
    try:
        # 대용량 데이터 생성 및 처리
        print("📊 대용량 테스트 데이터 생성 중...")
        
        test_articles = []
        for i in range(1000):  # 1000개 가짜 글 생성
            article = {
                'id': f'stress_test_{i}',
                'title': f'Test Article {i} - ' + 'Long title content ' * 20,
                'content': 'This is a very long test content that simulates real article content. ' * 100,
                'title_ko': f'테스트 글 {i} - ' + '긴 제목 내용 ' * 20,
                'content_ko': '이것은 실제 글 내용을 시뮬레이션하는 매우 긴 테스트 내용입니다. ' * 100,
                'summary': f'Test summary for article {i}. ' * 10,
                'url': f'https://test.com/article/{i}',
                'source': 'test',
                'score': 75 + (i % 25),
                'published': '2024-12-30T08:00:00Z'
            }
            test_articles.append(article)
        
        print(f"🔄 {len(test_articles)}개 글 처리 중...")
        
        # 필터링 작업 시뮬레이션
        from collectors.content_filter import ContentFilter
        content_filter = ContentFilter()
        
        filtered_articles = content_filter.filter_articles(test_articles)
        
        print(f"✅ {len(filtered_articles)}개 글 필터링 완료")
        
        # 번역 작업 시뮬레이션 (소량)
        print("🌐 번역 시뮬레이션...")
        for article in filtered_articles[:10]:  # 상위 10개만
            # 번역 시뮬레이션 (실제 API 호출 없이)
            time.sleep(0.1)  # API 지연 시뮬레이션
        
        print("✅ 메모리 스트레스 테스트 완료")
        
    finally:
        monitor.stop()
        monitor.print_summary()
        monitor.save_report("memory_stress_test.json")

def benchmark_apis():
    """API 성능 벤치마크"""
    print("🔌 API 성능 벤치마크 시작")
    
    monitor = PerformanceMonitor("API Benchmark")
    monitor.start()
    
    config = Config()
    
    try:
        # Reddit API 벤치마크
        print("🔴 Reddit API 성능 테스트...")
        from collectors.reddit_collector import RedditCollector
        reddit_collector = RedditCollector(config)
        
        for i in range(3):  # 3회 테스트
            start_time = time.time()
            try:
                articles = reddit_collector.collect_from_subreddit('MachineLearning', limit=5)
                duration = time.time() - start_time
                monitor.record_api_call('reddit', duration, True, f"Collected {len(articles)} articles")
                print(f"  Round {i+1}: {duration:.2f}초, {len(articles)}개 글")
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_api_call('reddit', duration, False, str(e))
                print(f"  Round {i+1}: 실패 - {e}")
            
            time.sleep(2)  # API 제한 대응
        
        # Gemini API 벤치마크 (사용 가능한 경우)
        print("🔵 Gemini API 성능 테스트...")
        from processors.summarizer import Summarizer
        summarizer = Summarizer(config)
        
        test_content = "머신러닝은 인공지능의 핵심 기술입니다. " * 50
        
        for i in range(3):  # 3회 테스트
            start_time = time.time()
            try:
                result = summarizer.summarize_text("테스트 제목", test_content)
                duration = time.time() - start_time
                success = result['success']
                monitor.record_api_call('gemini', duration, success, result.get('service', 'unknown'))
                status = "성공" if success else "실패"
                print(f"  Round {i+1}: {duration:.2f}초, {status}")
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_api_call('gemini', duration, False, str(e))
                print(f"  Round {i+1}: 실패 - {e}")
                
            time.sleep(3)  # API 제한 대응
        
    finally:
        monitor.stop()
        monitor.print_summary()
        monitor.save_report("api_benchmark.json")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'memory':
            run_memory_stress_test()
        elif test_type == 'api':
            benchmark_apis()
        elif test_type == 'full':
            run_performance_test()
        else:
            print("사용법: python test_performance.py [memory|api|full]")
    else:
        run_performance_test()
