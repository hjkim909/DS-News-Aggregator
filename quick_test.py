#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS News Aggregator - 간단한 연결 테스트
API 키 없이도 기본 기능들을 테스트
"""

import sys
import os
from datetime import datetime

print("🚀 DS News Aggregator 연결 테스트 시작")
print("="*50)

# 1. 기본 모듈 로드 테스트
print("📦 모듈 로드 테스트:")
try:
    from config import Config
    print("  ✅ config 모듈 로드 성공")
    
    from collectors.reddit_collector import RedditCollector
    print("  ✅ reddit_collector 모듈 로드 성공")
    
    from collectors.korean_blog_collector import KoreanBlogCollector
    print("  ✅ korean_blog_collector 모듈 로드 성공")
    
    from processors.translator import Translator
    print("  ✅ translator 모듈 로드 성공")
    
    from processors.summarizer import Summarizer
    print("  ✅ summarizer 모듈 로드 성공")
    
    from app import app
    print("  ✅ Flask 앱 로드 성공")
    
except ImportError as e:
    print(f"  ❌ 모듈 로드 실패: {e}")
    sys.exit(1)

# 2. 설정 확인
print("\n🔧 설정 확인:")
try:
    config = Config()
    
    print(f"  📊 Reddit 설정:")
    print(f"    CLIENT_ID: {'✅ 설정됨' if config.REDDIT_CLIENT_ID else '❌ 미설정'}")
    print(f"    CLIENT_SECRET: {'✅ 설정됨' if config.REDDIT_CLIENT_SECRET else '❌ 미설정'}")
    
    print(f"  🤖 Gemini 설정:")
    print(f"    API_KEY: {'✅ 설정됨' if config.GEMINI_API_KEY else '❌ 미설정'}")
    
    print(f"  ⚙️  기타 설정:")
    print(f"    최소 업보트: {config.MIN_UPVOTES}")
    print(f"    최소 점수: {config.MIN_SCORE_THRESHOLD}")
    print(f"    최종 글 수: {config.FINAL_ARTICLE_COUNT}")
    
except Exception as e:
    print(f"  ❌ 설정 확인 실패: {e}")

# 3. 번역 모듈 기본 테스트
print("\n🌐 번역 모듈 기본 테스트:")
try:
    translator = Translator()
    
    # 한국어 텍스트 (번역 스킵 테스트)
    korean_text = "머신러닝은 데이터를 분석하는 기술입니다."
    result = translator.translate_text(korean_text)
    
    if result['translation_needed'] == False:
        print("  ✅ 한국어 번역 스킵 기능 작동")
    else:
        print("  ⚠️  한국어 번역 스킵 기능 문제")
    
    # 영문 텍스트 (번역 테스트 - API 키 없어도 실행됨)
    english_text = "Machine learning is a technology for analyzing data."
    result = translator.translate_text(english_text)
    
    if result['translation_needed']:
        print("  ✅ 영문 번역 필요성 감지 성공")
        if result['success']:
            print(f"    번역 결과: {result['translated_text'][:50]}...")
        else:
            print(f"    ⚠️  번역 실패: {result['error']} (API 키 필요)")
    
except Exception as e:
    print(f"  ❌ 번역 테스트 실패: {e}")

# 4. Flask 앱 테스트
print("\n🌐 Flask 앱 테스트:")
try:
    app.config['TESTING'] = True
    client = app.test_client()
    
    # 메인 페이지
    response = client.get('/')
    if response.status_code == 200:
        print("  ✅ 메인 페이지 로드 성공")
    else:
        print(f"  ❌ 메인 페이지 로드 실패: {response.status_code}")
    
    # API 상태
    response = client.get('/api/status')
    if response.status_code == 200:
        print("  ✅ 상태 API 응답 성공")
    else:
        print(f"  ❌ 상태 API 응답 실패: {response.status_code}")
    
    # 정적 파일
    response = client.get('/static/style.css')
    if response.status_code == 200:
        print("  ✅ CSS 파일 로드 성공")
    else:
        print(f"  ⚠️  CSS 파일 로드 실패: {response.status_code}")
        
    response = client.get('/static/app.js')
    if response.status_code == 200:
        print("  ✅ JS 파일 로드 성공")
    else:
        print(f"  ⚠️  JS 파일 로드 실패: {response.status_code}")
    
except Exception as e:
    print(f"  ❌ Flask 앱 테스트 실패: {e}")

# 5. 디렉토리 확인
print("\n📁 디렉토리 구조 확인:")
required_dirs = ['data', 'logs', 'reports', 'static', 'templates', 'collectors', 'processors', 'scripts']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"  ✅ {dir_name}/ 디렉토리 존재")
    else:
        print(f"  ❌ {dir_name}/ 디렉토리 없음")
        os.makedirs(dir_name, exist_ok=True)
        print(f"    ➡️  {dir_name}/ 디렉토리 생성함")

# 6. 중요 파일 확인
print("\n📄 중요 파일 확인:")
important_files = [
    'app.py', 'config.py', 'main.py', 'requirements.txt',
    'env.example', 'README.md', 'railway.toml'
]
for file_name in important_files:
    if os.path.exists(file_name):
        print(f"  ✅ {file_name} 파일 존재")
    else:
        print(f"  ❌ {file_name} 파일 없음")

# 7. 환경변수 파일 확인
print("\n🔑 환경변수 설정 확인:")
if os.path.exists('.env'):
    print("  ✅ .env 파일 존재")
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'your-reddit-client-id' in content:
                print("  ⚠️  .env 파일에 실제 API 키를 입력해야 합니다")
            else:
                print("  ✅ .env 파일에 실제 값들이 설정된 것 같습니다")
    except:
        print("  ⚠️  .env 파일 읽기 실패")
else:
    print("  ❌ .env 파일 없음")
    print("  💡 다음 명령어로 생성하세요: cp env.example .env")

print(f"\n{'='*50}")
print("🎯 연결 테스트 완료!")
print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 다음 단계 안내
print(f"\n📋 다음 단계:")
if not os.path.exists('.env'):
    print("1. API 키 설정: cp env.example .env")
    print("2. .env 파일 편집하여 실제 API 키 입력")
    print("3. 다시 테스트: python quick_test.py")
else:
    print("1. 전체 시스템 테스트: python run_all_tests.py")
    print("2. 웹앱 실행: python app.py")
    print("3. 브라우저에서 http://localhost:5000 접속")

print("="*50)
