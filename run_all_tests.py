#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - 전체 테스트 실행 스크립트
통합 테스트, 성능 테스트, 품질 테스트, 모바일 테스트를 모두 실행
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any

def run_command(command: List[str], test_name: str) -> Dict[str, Any]:
    """커맨드 실행 및 결과 반환"""
    print(f"\n🚀 {test_name} 실행 중...")
    print(f"   명령어: {' '.join(command)}")
    
    start_time = time.time()
    
    try:
        # 프로세스 실행
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=1800,  # 30분 타임아웃
            cwd=os.getcwd()
        )
        
        duration = time.time() - start_time
        
        return {
            'name': test_name,
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'name': test_name,
            'success': False,
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': 'Test timed out after 30 minutes',
            'return_code': -1
        }
        
    except Exception as e:
        return {
            'name': test_name,
            'success': False,
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': str(e),
            'return_code': -2
        }

def run_individual_tests() -> List[Dict[str, Any]]:
    """개별 테스트들을 순차 실행"""
    
    tests = [
        {
            'name': '통합 테스트',
            'command': [sys.executable, 'test_integration.py'],
            'description': 'API 연결, 파이프라인, 웹앱 기능 종합 테스트',
            'weight': 0.3
        },
        {
            'name': '성능 테스트',
            'command': [sys.executable, 'test_performance.py', 'full'],
            'description': '메모리 사용량, 실행 시간, API 호출 최적화 테스트',
            'weight': 0.2
        },
        {
            'name': '품질 테스트',
            'command': [sys.executable, 'test_quality.py'],
            'description': '필터링 정확도, 번역 품질, 요약 품질 검증',
            'weight': 0.3
        },
        {
            'name': '모바일 테스트',
            'command': [sys.executable, 'test_mobile.py'],
            'description': '반응형 디자인, 터치 인터랙션, 로딩 속도 테스트',
            'weight': 0.2
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test['name']} 시작")
        print(f"📝 설명: {test['description']}")
        print(f"⚖️  가중치: {test['weight']*100:.0f}%")
        print(f"{'='*60}")
        
        result = run_command(test['command'], test['name'])
        result['weight'] = test['weight']
        result['description'] = test['description']
        
        # 실시간 결과 출력
        if result['success']:
            print(f"✅ {test['name']} 성공 ({result['duration']:.1f}초)")
        else:
            print(f"❌ {test['name']} 실패 ({result['duration']:.1f}초)")
            print(f"   오류 코드: {result['return_code']}")
            if result['stderr']:
                print(f"   오류: {result['stderr'][:200]}...")
        
        results.append(result)
        
        # 테스트 간 쿨타임
        time.sleep(2)
    
    return results

def generate_test_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """테스트 결과 리포트 생성"""
    
    total_tests = len(results)
    successful_tests = len([r for r in results if r['success']])
    failed_tests = total_tests - successful_tests
    
    total_duration = sum(r['duration'] for r in results)
    
    # 가중 평균 점수 계산
    weighted_score = 0
    total_weight = 0
    
    for result in results:
        if result['success']:
            weighted_score += result['weight'] * 100
        total_weight += result['weight']
    
    overall_score = (weighted_score / total_weight) if total_weight > 0 else 0
    
    # 등급 계산
    if overall_score >= 90:
        grade = 'A+'
    elif overall_score >= 85:
        grade = 'A'
    elif overall_score >= 80:
        grade = 'B+'
    elif overall_score >= 75:
        grade = 'B'
    elif overall_score >= 70:
        grade = 'C+'
    else:
        grade = 'D'
    
    return {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'overall_score': overall_score,
            'grade': grade
        },
        'detailed_results': results,
        'recommendations': generate_recommendations(results)
    }

def generate_recommendations(results: List[Dict[str, Any]]) -> List[str]:
    """테스트 결과 기반 권장사항 생성"""
    recommendations = []
    
    failed_tests = [r for r in results if not r['success']]
    
    for failed_test in failed_tests:
        test_name = failed_test['name']
        
        if '통합' in test_name:
            recommendations.append("API 키 설정을 확인하고 네트워크 연결을 점검하세요.")
            recommendations.append("모든 필수 Python 패키지가 설치되었는지 확인하세요.")
        
        elif '성능' in test_name:
            recommendations.append("메모리 사용량을 최적화하고 불필요한 프로세스를 종료하세요.")
            recommendations.append("API 호출 빈도를 줄이거나 캐싱을 강화하세요.")
        
        elif '품질' in test_name:
            recommendations.append("필터링 규칙을 재검토하고 키워드를 업데이트하세요.")
            recommendations.append("번역 및 요약 API의 응답 품질을 점검하세요.")
        
        elif '모바일' in test_name:
            recommendations.append("CSS 미디어 쿼리를 추가하여 반응형 디자인을 강화하세요.")
            recommendations.append("터치 타겟 크기를 44px 이상으로 확대하세요.")
    
    # 성공한 테스트에 대한 유지 권장사항
    successful_tests = [r for r in results if r['success']]
    if len(successful_tests) > 0:
        recommendations.append("성공한 테스트 영역의 품질을 지속적으로 유지하세요.")
    
    return list(set(recommendations))  # 중복 제거

def save_test_report(report: Dict[str, Any], filename: str = None) -> str:
    """테스트 리포트 저장"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"full_test_report_{timestamp}.json"
    
    os.makedirs('reports', exist_ok=True)
    filepath = os.path.join('reports', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return filepath

def print_final_summary(report: Dict[str, Any]):
    """최종 요약 출력"""
    summary = report['summary']
    
    print(f"\n{'='*70}")
    print(f"🎯 DS News Aggregator 전체 테스트 완료")
    print(f"{'='*70}")
    
    print(f"📊 테스트 결과 요약:")
    print(f"   🧪 총 테스트: {summary['total_tests']}개")
    print(f"   ✅ 성공: {summary['successful_tests']}개")
    print(f"   ❌ 실패: {summary['failed_tests']}개")
    print(f"   📈 성공률: {summary['success_rate']:.1f}%")
    print(f"   ⏱️  총 소요시간: {summary['total_duration']:.1f}초 ({summary['total_duration']/60:.1f}분)")
    
    print(f"\n🏆 전체 평가:")
    print(f"   📊 종합 점수: {summary['overall_score']:.1f}점")
    print(f"   🏅 등급: {summary['grade']}")
    
    # 등급별 메시지
    grade_messages = {
        'A+': "🎉 최우수! 프로덕션 배포 완벽 준비",
        'A': "🌟 우수! 프로덕션 배포 준비 완료",
        'B+': "👍 양호! 일부 최적화 후 배포 권장",
        'B': "✅ 보통! 몇 가지 개선 후 배포 가능",
        'C+': "⚠️  개선 필요! 주요 이슈 해결 후 배포",
        'D': "🚫 심각한 문제! 전반적인 개선 필요"
    }
    
    print(f"   💬 {grade_messages.get(summary['grade'], '평가 대기 중')}")
    
    # 개별 테스트 결과
    print(f"\n📋 개별 테스트 상세:")
    for result in report['detailed_results']:
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {result['name']}: {result['duration']:.1f}초")
        if not result['success'] and result['stderr']:
            print(f"      💥 오류: {result['stderr'][:100]}...")
    
    # 권장사항
    if report['recommendations']:
        print(f"\n💡 개선 권장사항:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n📁 상세 리포트는 reports/ 폴더에서 확인하세요")
    print(f"{'='*70}")

def check_prerequisites() -> bool:
    """전체 테스트 실행을 위한 사전 요구사항 확인"""
    print("🔍 사전 요구사항 체크...")
    
    # Python 버전 확인
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 버전이 낮습니다: {python_version.major}.{python_version.minor} < 3.8")
        return False
    else:
        print(f"✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 필수 파일 존재 확인
    required_files = [
        'app.py',
        'config.py',
        'main.py',
        'test_integration.py',
        'test_performance.py',
        'test_quality.py',
        'test_mobile.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 필수 파일 누락: {', '.join(missing_files)}")
        return False
    else:
        print(f"✅ 모든 필수 파일 존재 확인")
    
    # 디렉토리 생성
    required_dirs = ['data', 'logs', 'reports']
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
    print(f"✅ 필요 디렉토리 생성 완료")
    
    # 환경변수 파일 확인 (경고만)
    if not os.path.exists('.env'):
        print(f"⚠️  .env 파일이 없습니다. API 관련 테스트는 제한될 수 있습니다.")
    else:
        print(f"✅ .env 파일 발견")
    
    return True

def main():
    """메인 실행 함수"""
    print("🚀 DS News Aggregator 전체 테스트 스위트")
    print("="*70)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 작업 디렉토리: {os.getcwd()}")
    print(f"🐍 Python: {sys.version}")
    
    # 사전 요구사항 확인
    if not check_prerequisites():
        print("\n❌ 사전 요구사항을 충족하지 않습니다. 테스트를 중단합니다.")
        sys.exit(1)
    
    try:
        # 전체 테스트 실행
        print(f"\n🧪 전체 테스트 실행 시작...")
        print(f"⏱️  예상 소요 시간: 10-20분")
        
        start_time = time.time()
        test_results = run_individual_tests()
        total_duration = time.time() - start_time
        
        # 리포트 생성
        report = generate_test_report(test_results)
        report['summary']['actual_total_duration'] = total_duration
        
        # 리포트 저장
        report_path = save_test_report(report)
        
        # 최종 요약 출력
        print_final_summary(report)
        
        print(f"\n📋 상세 테스트 리포트: {report_path}")
        print(f"🏁 전체 테스트 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 성공/실패 결정
        success_rate = report['summary']['success_rate']
        overall_score = report['summary']['overall_score']
        
        if success_rate >= 75 and overall_score >= 70:
            print(f"\n🎉 전체 테스트 통과! 시스템이 배포 준비 상태입니다.")
            return 0
        else:
            print(f"\n⚠️  일부 테스트 실패. 개선 후 재테스트를 권장합니다.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  사용자에 의해 테스트가 중단되었습니다.")
        return 2
        
    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {e}")
        return 3

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
