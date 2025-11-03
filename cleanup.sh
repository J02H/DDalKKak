#!/bin/bash

echo "🧹 불필요한 파일 정리 중..."

# 개발용 파일들 제거
rm -f simple_crawler.py
rm -f kku_glocal_crawler.py

# 임시 파일들 제거
rm -f *.log
rm -f *.tmp
rm -f .DS_Store

# Python 캐시 파일들 제거
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Docker 관련 임시 파일들 제거
rm -f docker-compose-ssl.yml

echo "✅ 파일 정리 완료!"

# 최종 파일 목록 표시
echo ""
echo "📁 최종 프로젝트 구조:"
tree -I '__pycache__|*.pyc|.git' || ls -la