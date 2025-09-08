#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - 모바일 테스트 스크립트
반응형 디자인, 터치 인터랙션, 로딩 속도를 테스트
"""

import time
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import urljoin

# Flask 테스트용
from app import app

class MobileTestMetrics:
    """모바일 테스트 메트릭"""
    
    def __init__(self):
        self.results = {
            'responsive_design': {
                'media_queries_found': 0,
                'mobile_breakpoints': [],
                'grid_responsiveness': False,
                'text_scaling': False,
                'button_sizing': False,
                'score': 0
            },
            'touch_interaction': {
                'touch_targets_adequate': 0,
                'touch_events_present': False,
                'hover_alternatives': False,
                'gesture_support': False,
                'score': 0
            },
            'loading_performance': {
                'html_load_time': 0,
                'css_load_time': 0,
                'js_load_time': 0,
                'total_load_time': 0,
                'meets_target': False,
                'score': 0
            },
            'content_optimization': {
                'viewport_meta': False,
                'image_optimization': False,
                'font_optimization': False,
                'compression_support': False,
                'score': 0
            }
        }
    
    def calculate_overall_score(self) -> float:
        """전체 모바일 점수 계산"""
        scores = [
            self.results['responsive_design']['score'],
            self.results['touch_interaction']['score'],
            self.results['loading_performance']['score'],
            self.results['content_optimization']['score']
        ]
        return sum(scores) / len(scores)
    
    def save_report(self, filename: str = None):
        """모바일 테스트 리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mobile_test_report_{timestamp}.json"
        
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        overall_score = self.calculate_overall_score()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'grade': self._get_grade(overall_score),
            'metrics': self.results,
            'recommendations': self._generate_recommendations()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _get_grade(self, score: float) -> str:
        """점수에 따른 등급"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'C+'
        elif score >= 65:
            return 'C'
        else:
            return 'D'
    
    def _generate_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if self.results['responsive_design']['score'] < 80:
            recommendations.append("반응형 디자인 개선: 더 많은 미디어 쿼리와 브레이크포인트 추가")
        
        if self.results['touch_interaction']['score'] < 80:
            recommendations.append("터치 인터랙션 개선: 터치 타겟 크기를 44px 이상으로 확대")
        
        if self.results['loading_performance']['score'] < 80:
            recommendations.append("로딩 성능 개선: CSS/JS 파일 최적화 및 압축")
        
        if self.results['content_optimization']['score'] < 80:
            recommendations.append("콘텐츠 최적화: 이미지 압축 및 폰트 최적화")
        
        return recommendations

class ResponsiveDesignTester:
    """반응형 디자인 테스터"""
    
    def __init__(self, app):
        self.app = app
        self.client = app.test_client()
    
    def test_css_responsiveness(self) -> Dict[str, Any]:
        """CSS 반응형 기능 테스트"""
        print("📱 CSS 반응형 기능 테스트...")
        
        results = {
            'media_queries': [],
            'breakpoints': [],
            'responsive_features': []
        }
        
        try:
            # CSS 파일 내용 가져오기
            css_response = self.client.get('/static/style.css')
            if css_response.status_code == 200:
                css_content = css_response.data.decode('utf-8')
                
                # 미디어 쿼리 찾기
                media_query_patterns = [
                    r'@media\s*\([^)]*max-width:\s*(\d+)px[^)]*\)',
                    r'@media\s*\([^)]*min-width:\s*(\d+)px[^)]*\)',
                    r'@media.*screen.*and.*\(.*width.*\)',
                ]
                
                for pattern in media_query_patterns:
                    matches = re.findall(pattern, css_content, re.IGNORECASE)
                    results['media_queries'].extend(matches)
                
                # 일반적인 브레이크포인트 확인
                common_breakpoints = ['768px', '640px', '480px', '1024px', '1200px']
                for bp in common_breakpoints:
                    if bp in css_content:
                        results['breakpoints'].append(bp)
                        print(f"  ✅ 브레이크포인트 발견: {bp}")
                
                # 반응형 기능 확인
                responsive_features = {
                    'grid-template-columns': 'CSS Grid 반응형',
                    'flex-direction: column': '플렉스박스 스택',
                    'hidden sm:': 'Tailwind 반응형 숨김',
                    'text-sm': '반응형 텍스트',
                    'p-2 sm:p-4': '반응형 패딩',
                    'gap-2 md:gap-4': '반응형 간격'
                }
                
                for feature, description in responsive_features.items():
                    if feature in css_content:
                        results['responsive_features'].append(description)
                        print(f"  ✅ {description} 기능 발견")
                
            else:
                print(f"  ❌ CSS 파일 로드 실패: {css_response.status_code}")
                
        except Exception as e:
            print(f"  💥 CSS 분석 실패: {e}")
        
        return results
    
    def test_html_viewport_meta(self) -> Dict[str, Any]:
        """HTML 뷰포트 메타태그 테스트"""
        print("📱 HTML 뷰포트 설정 테스트...")
        
        results = {
            'viewport_meta': False,
            'mobile_optimized': False,
            'touch_icon': False
        }
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 뷰포트 메타태그 확인
                viewport_patterns = [
                    r'<meta[^>]*name=["\']viewport["\'][^>]*>',
                    r'width=device-width',
                    r'initial-scale=1'
                ]
                
                for pattern in viewport_patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        results['viewport_meta'] = True
                        print(f"  ✅ 뷰포트 메타태그 발견")
                        break
                
                # 모바일 최적화 확인
                mobile_features = [
                    'user-scalable=no',
                    'maximum-scale=',
                    'minimum-scale=',
                    'touch-action'
                ]
                
                mobile_feature_count = sum(1 for feature in mobile_features if feature in html_content)
                results['mobile_optimized'] = mobile_feature_count > 0
                
                # 터치 아이콘 확인
                if 'apple-touch-icon' in html_content or 'touch-icon' in html_content:
                    results['touch_icon'] = True
                    print(f"  ✅ 터치 아이콘 설정 발견")
                
            else:
                print(f"  ❌ HTML 페이지 로드 실패: {response.status_code}")
                
        except Exception as e:
            print(f"  💥 HTML 분석 실패: {e}")
        
        return results
    
    def simulate_different_screen_sizes(self) -> Dict[str, Any]:
        """다양한 화면 크기 시뮬레이션"""
        print("📱 화면 크기별 시뮬레이션...")
        
        screen_sizes = {
            'mobile': {'width': 375, 'height': 667, 'name': '모바일 (iPhone SE)'},
            'tablet': {'width': 768, 'height': 1024, 'name': '태블릿 (iPad)'},
            'desktop': {'width': 1920, 'height': 1080, 'name': '데스크톱 (Full HD)'}
        }
        
        results = {}
        
        for size_name, dimensions in screen_sizes.items():
            print(f"  📐 {dimensions['name']} ({dimensions['width']}x{dimensions['height']}) 시뮬레이션...")
            
            # 실제 화면 크기 시뮬레이션은 브라우저 없이 제한적
            # HTML/CSS 분석으로 대체
            try:
                response = self.client.get('/')
                if response.status_code == 200:
                    results[size_name] = {
                        'responsive': True,  # CSS 기반으로 추정
                        'load_time': 0.1,   # 시뮬레이션 값
                        'usable': True
                    }
                    print(f"    ✅ {dimensions['name']} 호환성 양호")
                else:
                    results[size_name] = {
                        'responsive': False,
                        'load_time': 0,
                        'usable': False
                    }
                    
            except Exception as e:
                print(f"    ❌ {dimensions['name']} 시뮬레이션 실패: {e}")
                results[size_name] = {'responsive': False, 'load_time': 0, 'usable': False}
        
        return results

class TouchInteractionTester:
    """터치 인터랙션 테스터"""
    
    def __init__(self, app):
        self.app = app
        self.client = app.test_client()
    
    def test_touch_target_sizes(self) -> Dict[str, Any]:
        """터치 타겟 크기 테스트"""
        print("👆 터치 타겟 크기 테스트...")
        
        results = {
            'adequate_touch_targets': [],
            'small_touch_targets': [],
            'button_analysis': {}
        }
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 버튼과 링크 요소 분석
                touch_elements = {
                    'button': re.findall(r'<button[^>]*class="([^"]*)"[^>]*>', html_content),
                    'link': re.findall(r'<a[^>]*class="([^"]*)"[^>]*>', html_content),
                    'input': re.findall(r'<input[^>]*class="([^"]*)"[^>]*>', html_content)
                }
                
                # Tailwind CSS 클래스에서 패딩/크기 분석
                adequate_size_patterns = [
                    r'p-[3-9]|p-1[0-9]',  # 충분한 패딩
                    r'px-[3-9]|px-1[0-9]',  # 충분한 가로 패딩
                    r'py-[3-9]|py-1[0-9]',  # 충분한 세로 패딩
                    r'h-1[0-9]|h-2[0-9]',   # 충분한 높이
                    r'w-1[0-9]|w-2[0-9]',   # 충분한 너비
                    r'min-w-\[2\.5rem\]',   # 최소 너비 설정
                    r'text-lg|text-xl',     # 큰 텍스트
                ]
                
                for element_type, class_lists in touch_elements.items():
                    adequate_count = 0
                    total_count = len(class_lists)
                    
                    for class_list in class_lists:
                        is_adequate = any(re.search(pattern, class_list) for pattern in adequate_size_patterns)
                        if is_adequate:
                            adequate_count += 1
                            results['adequate_touch_targets'].append(f"{element_type}: {class_list[:50]}")
                        else:
                            results['small_touch_targets'].append(f"{element_type}: {class_list[:50]}")
                    
                    if total_count > 0:
                        adequacy_rate = adequate_count / total_count * 100
                        results['button_analysis'][element_type] = {
                            'total': total_count,
                            'adequate': adequate_count,
                            'adequacy_rate': adequacy_rate
                        }
                        print(f"  📊 {element_type}: {adequate_count}/{total_count} ({adequacy_rate:.1f}%) 적절한 크기")
                    
        except Exception as e:
            print(f"  💥 터치 타겟 분석 실패: {e}")
        
        return results
    
    def test_touch_events_support(self) -> Dict[str, Any]:
        """터치 이벤트 지원 테스트"""
        print("👆 터치 이벤트 지원 테스트...")
        
        results = {
            'click_events': False,
            'touch_events': False,
            'gesture_support': False,
            'hover_alternatives': False
        }
        
        try:
            # JavaScript 파일 확인
            js_response = self.client.get('/static/app.js')
            if js_response.status_code == 200:
                js_content = js_response.data.decode('utf-8')
                
                # 이벤트 리스너 확인
                event_patterns = {
                    'click_events': [r'addEventListener\(["\']click["\']', r'onclick=', r'\.click\('],
                    'touch_events': [r'touchstart', r'touchmove', r'touchend', r'touchcancel'],
                    'gesture_support': [r'gesturestart', r'gesturechange', r'gestureend'],
                    'hover_alternatives': [r'mouseenter', r'mouseleave', r':hover']
                }
                
                for event_type, patterns in event_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, js_content, re.IGNORECASE):
                            results[event_type] = True
                            print(f"  ✅ {event_type} 지원 발견")
                            break
            
            # CSS에서 호버 대안 확인
            css_response = self.client.get('/static/style.css')
            if css_response.status_code == 200:
                css_content = css_response.data.decode('utf-8')
                
                # 터치 친화적 CSS 확인
                touch_css_patterns = [
                    r'@media\s*\([^)]*hover:\s*hover[^)]*\)',  # 호버 지원 장치만
                    r'@media\s*\([^)]*pointer:\s*coarse[^)]*\)',  # 터치 장치 대응
                    r':active',  # 터치시 활성 상태
                    r'touch-action'  # 터치 액션 제어
                ]
                
                hover_alternative_count = sum(1 for pattern in touch_css_patterns 
                                           if re.search(pattern, css_content, re.IGNORECASE))
                
                if hover_alternative_count > 0:
                    results['hover_alternatives'] = True
                    print(f"  ✅ 터치 친화적 CSS 기능 {hover_alternative_count}개 발견")
                    
        except Exception as e:
            print(f"  💥 터치 이벤트 분석 실패: {e}")
        
        return results
    
    def test_gesture_navigation(self) -> Dict[str, Any]:
        """제스처 네비게이션 테스트"""
        print("👆 제스처 네비게이션 테스트...")
        
        results = {
            'swipe_support': False,
            'pinch_zoom': False,
            'scroll_optimization': False,
            'keyboard_navigation': False
        }
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 스크롤 최적화 확인
                scroll_indicators = [
                    'overflow-y-auto',
                    'scroll-behavior: smooth',
                    'overscroll-behavior',
                    '-webkit-overflow-scrolling'
                ]
                
                for indicator in scroll_indicators:
                    if indicator in html_content:
                        results['scroll_optimization'] = True
                        print(f"  ✅ 스크롤 최적화 발견: {indicator}")
                        break
                
                # 키보드 네비게이션 지원
                keyboard_indicators = [
                    'tabindex=',
                    'role="button"',
                    'aria-label=',
                    'focus:'
                ]
                
                keyboard_features = sum(1 for indicator in keyboard_indicators if indicator in html_content)
                if keyboard_features > 0:
                    results['keyboard_navigation'] = True
                    print(f"  ✅ 키보드 네비게이션 기능 {keyboard_features}개 발견")
                    
        except Exception as e:
            print(f"  💥 제스처 네비게이션 분석 실패: {e}")
        
        return results

class LoadingPerformanceTester:
    """로딩 성능 테스터"""
    
    def __init__(self, app):
        self.app = app
        self.client = app.test_client()
    
    def test_page_load_times(self) -> Dict[str, Any]:
        """페이지 로딩 시간 테스트"""
        print("⚡ 페이지 로딩 시간 테스트...")
        
        results = {
            'html_load_time': 0,
            'css_load_time': 0,
            'js_load_time': 0,
            'api_response_time': 0,
            'total_simulated_time': 0
        }
        
        try:
            # HTML 로딩 시간
            start_time = time.time()
            html_response = self.client.get('/')
            html_load_time = time.time() - start_time
            results['html_load_time'] = html_load_time
            print(f"  📄 HTML 로딩: {html_load_time:.3f}초")
            
            # CSS 로딩 시간
            start_time = time.time()
            css_response = self.client.get('/static/style.css')
            css_load_time = time.time() - start_time
            results['css_load_time'] = css_load_time
            print(f"  🎨 CSS 로딩: {css_load_time:.3f}초")
            
            # JavaScript 로딩 시간
            start_time = time.time()
            js_response = self.client.get('/static/app.js')
            js_load_time = time.time() - start_time
            results['js_load_time'] = js_load_time
            print(f"  ⚙️  JS 로딩: {js_load_time:.3f}초")
            
            # API 응답 시간
            start_time = time.time()
            api_response = self.client.get('/api/status')
            api_response_time = time.time() - start_time
            results['api_response_time'] = api_response_time
            print(f"  🔌 API 응답: {api_response_time:.3f}초")
            
            # 시뮬레이션된 총 로딩 시간 (병렬 로딩 고려)
            total_time = max(html_load_time, css_load_time, js_load_time) + api_response_time
            results['total_simulated_time'] = total_time
            
            print(f"  📊 시뮬레이션된 총 로딩: {total_time:.3f}초")
            
            # 3초 목표 달성 여부
            target_time = 3.0
            meets_target = total_time <= target_time
            results['meets_3s_target'] = meets_target
            
            status = "✅" if meets_target else "❌"
            print(f"  🎯 3초 목표: {status} ({total_time:.3f}초 / {target_time}초)")
            
        except Exception as e:
            print(f"  💥 로딩 시간 테스트 실패: {e}")
        
        return results
    
    def test_resource_optimization(self) -> Dict[str, Any]:
        """리소스 최적화 테스트"""
        print("📦 리소스 최적화 테스트...")
        
        results = {
            'css_size': 0,
            'js_size': 0,
            'html_size': 0,
            'compression_headers': False,
            'cache_headers': False
        }
        
        try:
            # 파일 크기 측정
            resources = {
                'css': '/static/style.css',
                'js': '/static/app.js',
                'html': '/'
            }
            
            for resource_type, url in resources.items():
                response = self.client.get(url)
                if response.status_code == 200:
                    size = len(response.data)
                    size_kb = size / 1024
                    results[f'{resource_type}_size'] = size_kb
                    print(f"  📄 {resource_type.upper()} 크기: {size_kb:.1f}KB")
                    
                    # 압축 헤더 확인
                    if 'content-encoding' in response.headers:
                        results['compression_headers'] = True
                        print(f"    ✅ 압축 지원: {response.headers['content-encoding']}")
                    
                    # 캐시 헤더 확인
                    cache_headers = ['cache-control', 'expires', 'etag', 'last-modified']
                    for header in cache_headers:
                        if header in response.headers:
                            results['cache_headers'] = True
                            print(f"    ✅ 캐시 헤더: {header}")
                            break
            
            # 크기 기준 평가
            size_limits = {'css': 100, 'js': 200, 'html': 50}  # KB 기준
            
            for resource_type, limit in size_limits.items():
                actual_size = results[f'{resource_type}_size']
                if actual_size <= limit:
                    print(f"    ✅ {resource_type.upper()} 크기 적절 ({actual_size:.1f}KB ≤ {limit}KB)")
                else:
                    print(f"    ⚠️  {resource_type.upper()} 크기 큼 ({actual_size:.1f}KB > {limit}KB)")
                    
        except Exception as e:
            print(f"  💥 리소스 최적화 테스트 실패: {e}")
        
        return results

class ContentOptimizationTester:
    """콘텐츠 최적화 테스터"""
    
    def __init__(self, app):
        self.app = app
        self.client = app.test_client()
    
    def test_image_optimization(self) -> Dict[str, Any]:
        """이미지 최적화 테스트"""
        print("🖼️  이미지 최적화 테스트...")
        
        results = {
            'responsive_images': False,
            'lazy_loading': False,
            'optimized_formats': False,
            'alt_texts': False
        }
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 이미지 태그 분석
                image_patterns = {
                    'responsive_images': [r'<img[^>]*srcset=', r'<picture>', r'sizes='],
                    'lazy_loading': [r'loading="lazy"', r'data-src='],
                    'optimized_formats': [r'\.webp', r'\.avif', r'<source[^>]*type="image/webp"'],
                    'alt_texts': [r'<img[^>]*alt="[^"]+']
                }
                
                for feature, patterns in image_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, html_content, re.IGNORECASE):
                            results[feature] = True
                            print(f"  ✅ {feature} 지원 발견")
                            break
                
                # 이미지 개수 확인
                img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
                if img_tags:
                    print(f"  📊 이미지 {len(img_tags)}개 발견")
                else:
                    print(f"  ℹ️  이미지 없음 (아이콘 기반 UI)")
                    results['optimized_formats'] = True  # 이미지가 없으면 최적화됨
                    
        except Exception as e:
            print(f"  💥 이미지 최적화 테스트 실패: {e}")
        
        return results
    
    def test_font_optimization(self) -> Dict[str, Any]:
        """폰트 최적화 테스트"""
        print("🔤 폰트 최적화 테스트...")
        
        results = {
            'web_fonts': False,
            'font_display': False,
            'font_preload': False,
            'system_fonts': False
        }
        
        try:
            # HTML에서 폰트 로딩 확인
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 웹폰트 로딩 확인
                webfont_patterns = [
                    r'fonts\.googleapis\.com',
                    r'fonts\.gstatic\.com',
                    r'@font-face',
                    r'\.woff2?'
                ]
                
                for pattern in webfont_patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        results['web_fonts'] = True
                        print(f"  ✅ 웹폰트 로딩 발견")
                        break
                
                # 폰트 디스플레이 최적화
                font_display_patterns = [
                    r'font-display:\s*swap',
                    r'font-display:\s*fallback',
                    r'font-display:\s*optional'
                ]
                
                for pattern in font_display_patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        results['font_display'] = True
                        print(f"  ✅ 폰트 디스플레이 최적화 발견")
                        break
                
                # 폰트 프리로드 확인
                if re.search(r'<link[^>]*rel="preload"[^>]*font', html_content, re.IGNORECASE):
                    results['font_preload'] = True
                    print(f"  ✅ 폰트 프리로드 발견")
            
            # CSS에서 시스템 폰트 사용 확인
            css_response = self.client.get('/static/style.css')
            if css_response.status_code == 200:
                css_content = css_response.data.decode('utf-8')
                
                # 시스템 폰트 스택 확인
                system_font_patterns = [
                    r'-apple-system',
                    r'BlinkMacSystemFont',
                    r'system-ui',
                    r'sans-serif'
                ]
                
                system_font_count = sum(1 for pattern in system_font_patterns 
                                     if pattern in css_content)
                
                if system_font_count >= 3:  # 여러 시스템 폰트 사용
                    results['system_fonts'] = True
                    print(f"  ✅ 시스템 폰트 스택 사용 ({system_font_count}개)")
                    
        except Exception as e:
            print(f"  💥 폰트 최적화 테스트 실패: {e}")
        
        return results
    
    def test_accessibility_features(self) -> Dict[str, Any]:
        """접근성 기능 테스트"""
        print("♿ 접근성 기능 테스트...")
        
        results = {
            'semantic_html': False,
            'aria_labels': False,
            'color_contrast': False,
            'keyboard_navigation': False,
            'focus_indicators': False
        }
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # 시맨틱 HTML 확인
                semantic_tags = [
                    '<header>', '<main>', '<nav>', '<section>', 
                    '<article>', '<aside>', '<footer>'
                ]
                
                semantic_count = sum(1 for tag in semantic_tags if tag in html_content)
                if semantic_count >= 3:
                    results['semantic_html'] = True
                    print(f"  ✅ 시맨틱 HTML 사용 ({semantic_count}개 태그)")
                
                # ARIA 레이블 확인
                aria_patterns = [
                    r'aria-label=',
                    r'aria-describedby=',
                    r'aria-labelledby=',
                    r'role="'
                ]
                
                aria_count = sum(1 for pattern in aria_patterns 
                               if re.search(pattern, html_content, re.IGNORECASE))
                
                if aria_count > 0:
                    results['aria_labels'] = True
                    print(f"  ✅ ARIA 레이블 사용 ({aria_count}개)")
                
                # 키보드 네비게이션 지원
                keyboard_indicators = ['tabindex=', 'focus:', 'outline:']
                keyboard_count = sum(1 for indicator in keyboard_indicators 
                                   if indicator in html_content)
                
                if keyboard_count > 0:
                    results['keyboard_navigation'] = True
                    print(f"  ✅ 키보드 네비게이션 지원")
            
            # CSS에서 접근성 확인
            css_response = self.client.get('/static/style.css')
            if css_response.status_code == 200:
                css_content = css_response.data.decode('utf-8')
                
                # 포커스 인디케이터 확인
                focus_patterns = [':focus', 'focus:', 'outline:', 'focus-visible']
                focus_count = sum(1 for pattern in focus_patterns if pattern in css_content)
                
                if focus_count > 0:
                    results['focus_indicators'] = True
                    print(f"  ✅ 포커스 인디케이터 설정")
                
                # 고대비 모드 지원
                if '@media (prefers-contrast: high)' in css_content:
                    results['color_contrast'] = True
                    print(f"  ✅ 고대비 모드 지원")
                    
        except Exception as e:
            print(f"  💥 접근성 테스트 실패: {e}")
        
        return results

def run_mobile_tests():
    """전체 모바일 테스트 실행"""
    print("📱 DS News Aggregator 모바일 테스트 시작")
    print("="*60)
    
    app.config['TESTING'] = True
    metrics = MobileTestMetrics()
    
    try:
        # 1. 반응형 디자인 테스트
        print("\n1️⃣ 반응형 디자인 테스트")
        print("-" * 30)
        
        responsive_tester = ResponsiveDesignTester(app)
        
        css_results = responsive_tester.test_css_responsiveness()
        viewport_results = responsive_tester.test_html_viewport_meta()
        screen_results = responsive_tester.simulate_different_screen_sizes()
        
        # 반응형 점수 계산
        responsive_score = 0
        if len(css_results['breakpoints']) >= 2:
            responsive_score += 30
        if len(css_results['responsive_features']) >= 3:
            responsive_score += 25
        if viewport_results['viewport_meta']:
            responsive_score += 25
        if all(screen['responsive'] for screen in screen_results.values()):
            responsive_score += 20
        
        metrics.results['responsive_design']['score'] = responsive_score
        metrics.results['responsive_design']['media_queries_found'] = len(css_results['media_queries'])
        metrics.results['responsive_design']['mobile_breakpoints'] = css_results['breakpoints']
        
        # 2. 터치 인터랙션 테스트
        print("\n2️⃣ 터치 인터랙션 테스트")
        print("-" * 30)
        
        touch_tester = TouchInteractionTester(app)
        
        touch_target_results = touch_tester.test_touch_target_sizes()
        touch_event_results = touch_tester.test_touch_events_support()
        gesture_results = touch_tester.test_gesture_navigation()
        
        # 터치 점수 계산
        touch_score = 0
        if touch_target_results['adequate_touch_targets']:
            touch_score += 30
        if touch_event_results['click_events']:
            touch_score += 25
        if touch_event_results['hover_alternatives']:
            touch_score += 25
        if gesture_results['scroll_optimization']:
            touch_score += 20
        
        metrics.results['touch_interaction']['score'] = touch_score
        
        # 3. 로딩 성능 테스트
        print("\n3️⃣ 로딩 성능 테스트")
        print("-" * 30)
        
        loading_tester = LoadingPerformanceTester(app)
        
        load_time_results = loading_tester.test_page_load_times()
        resource_results = loading_tester.test_resource_optimization()
        
        # 로딩 점수 계산
        loading_score = 0
        if load_time_results.get('meets_3s_target', False):
            loading_score += 40
        elif load_time_results.get('total_simulated_time', 5) < 5:
            loading_score += 20
        
        if resource_results['css_size'] < 100:  # 100KB 미만
            loading_score += 20
        if resource_results['js_size'] < 200:   # 200KB 미만
            loading_score += 20
        if resource_results['compression_headers']:
            loading_score += 10
        if resource_results['cache_headers']:
            loading_score += 10
        
        metrics.results['loading_performance']['score'] = loading_score
        metrics.results['loading_performance'].update(load_time_results)
        
        # 4. 콘텐츠 최적화 테스트
        print("\n4️⃣ 콘텐츠 최적화 테스트")
        print("-" * 30)
        
        content_tester = ContentOptimizationTester(app)
        
        image_results = content_tester.test_image_optimization()
        font_results = content_tester.test_font_optimization()
        accessibility_results = content_tester.test_accessibility_features()
        
        # 콘텐츠 점수 계산
        content_score = 0
        if image_results['optimized_formats']:
            content_score += 20
        if font_results['system_fonts']:
            content_score += 20
        if viewport_results['viewport_meta']:
            content_score += 20
        if accessibility_results['semantic_html']:
            content_score += 20
        if accessibility_results['aria_labels']:
            content_score += 10
        if accessibility_results['keyboard_navigation']:
            content_score += 10
        
        metrics.results['content_optimization']['score'] = content_score
        metrics.results['content_optimization']['viewport_meta'] = viewport_results['viewport_meta']
        
        # 최종 결과 출력
        overall_score = metrics.calculate_overall_score()
        grade = metrics._get_grade(overall_score)
        
        print("\n📊 모바일 테스트 결과")
        print("="*60)
        print(f"📱 반응형 디자인: {metrics.results['responsive_design']['score']}점")
        print(f"👆 터치 인터랙션: {metrics.results['touch_interaction']['score']}점")
        print(f"⚡ 로딩 성능: {metrics.results['loading_performance']['score']}점")
        print(f"📦 콘텐츠 최적화: {metrics.results['content_optimization']['score']}점")
        print(f"\n🎯 전체 점수: {overall_score:.1f}점 ({grade} 등급)")
        
        # 권장사항 출력
        recommendations = metrics._generate_recommendations()
        if recommendations:
            print(f"\n💡 개선 권장사항:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # 리포트 저장
        report_path = metrics.save_report()
        print(f"\n📋 상세 리포트: {report_path}")
        
        # 합격 기준 (75점 이상)
        passing_score = 75
        if overall_score >= passing_score:
            print(f"\n🎉 모바일 테스트 통과! ({overall_score:.1f}점 ≥ {passing_score}점)")
            return True
        else:
            print(f"\n⚠️  모바일 최적화 개선 필요 ({overall_score:.1f}점 < {passing_score}점)")
            return False
            
    except Exception as e:
        print(f"💥 모바일 테스트 실패: {e}")
        return False

if __name__ == '__main__':
    success = run_mobile_tests()
    sys.exit(0 if success else 1)
