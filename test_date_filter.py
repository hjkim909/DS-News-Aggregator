#!/usr/bin/env python3
"""
날짜 필터링 기능 테스트 스크립트
"""

import json
import os
import glob

DATA_DIR = 'data'

def test_date_api():
    """날짜 목록 API 로직 테스트"""
    print("=" * 60)
    print("📅 날짜 필터링 기능 테스트")
    print("=" * 60)
    
    # 1. 날짜별 파일 찾기
    date_files = glob.glob(os.path.join(DATA_DIR, 'articles_*.json'))
    print(f"\n1️⃣ 발견된 파일: {len(date_files)}개")
    for file_path in date_files:
        filename = os.path.basename(file_path)
        print(f"   - {filename}")
    
    # 2. 날짜 추출 및 검증
    dates = []
    print(f"\n2️⃣ 날짜 추출 및 검증:")
    
    for file_path in date_files:
        filename = os.path.basename(file_path)
        
        # articles.json 제외
        if filename == 'articles.json':
            print(f"   ⏭️  건너뜀: {filename} (최신 파일)")
            continue
        
        # 날짜 추출
        date_str = filename.replace('articles_', '').replace('.json', '')
        
        # 날짜 형식 검증
        if len(date_str) != 10 or date_str.count('-') != 2:
            print(f"   ❌ 잘못된 형식: {filename} → {date_str}")
            continue
        
        # 파일 로드
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                article_count = len(data.get('articles', []))
                dates.append({
                    'date': date_str,
                    'count': article_count,
                    'file': filename
                })
                print(f"   ✅ {date_str}: {article_count}개 글")
        except Exception as e:
            print(f"   ❌ 로드 실패: {filename} - {e}")
    
    # 3. 정렬
    dates.sort(key=lambda x: x['date'], reverse=True)
    print(f"\n3️⃣ 날짜 정렬 (최신순):")
    for i, date_info in enumerate(dates, 1):
        print(f"   {i}. {date_info['date']}: {date_info['count']}개")
    
    # 4. API 응답 시뮬레이션
    print(f"\n4️⃣ API 응답 시뮬레이션:")
    api_response = {
        'success': True,
        'dates': dates,
        'total': len(dates)
    }
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # 5. 결과 요약
    print(f"\n" + "=" * 60)
    print(f"📊 테스트 결과:")
    print(f"   - 총 파일: {len(date_files)}개")
    print(f"   - 유효한 날짜: {len(dates)}개")
    if len(dates) > 0:
        print(f"   - 최신 날짜: {dates[0]['date']} ({dates[0]['count']}개)")
        print(f"   - 가장 오래된 날짜: {dates[-1]['date']} ({dates[-1]['count']}개)")
        print(f"\n✅ 날짜 필터링이 정상 작동합니다!")
    else:
        print(f"\n⚠️  날짜별 파일이 없습니다.")
        print(f"   해결 방법: python main.py 를 실행하여 뉴스를 수집하세요.")
    print("=" * 60)

if __name__ == '__main__':
    test_date_api()

