#!/bin/bash
# DS News Aggregator - 뉴스 수집 스크립트
# 사용법: ./수집_실행.sh

echo "🚀 DS News Aggregator 뉴스 수집 시작..."
echo ""

# 뉴스 수집 실행
python -c "from processors.pipeline import run_ds_news_pipeline; import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'); stats = run_ds_news_pipeline(); print(f'\n✅ 수집 완료!'); print(f'수집: {stats[\"original_articles\"]}개 → 필터링: {stats[\"filtered_articles\"]}개 → 저장: {stats[\"final_articles\"]}개')"

echo ""
echo "📊 결과를 Git에 저장하시겠습니까? (y/n)"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "📦 Git에 커밋 중..."
    git add data/articles*.json
    git commit -m "📰 뉴스 수집: $(date +'%Y-%m-%d %H:%M')"
    
    echo "🚀 GitHub에 푸시 중..."
    git push origin main
    
    echo ""
    echo "✅ 완료! Railway에 자동 배포됩니다."
    echo "🌐 웹사이트: https://ds-news-aggregator-production.up.railway.app"
else
    echo "ℹ️  로컬에만 저장되었습니다."
fi

