#!/bin/bash

echo "🚀 건국대 글로컬 공지사항 시스템 배포 시작"

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다. Docker를 먼저 설치해주세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다. Docker Compose를 먼저 설치해주세요."
    exit 1
fi

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down

# 이미지 빌드 및 컨테이너 실행
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build

echo "🚀 서비스 시작 중..."
docker-compose up -d

# 서비스 상태 확인
echo "⏳ 서비스 시작 대기 중..."
sleep 10

if curl -f http://localhost/api/colleges > /dev/null 2>&1; then
    echo "✅ 배포 완료! 서비스가 정상적으로 실행 중입니다."
    echo "🌐 웹사이트: http://localhost"
    echo "🔗 API: http://localhost/api"
else
    echo "❌ 서비스 시작에 실패했습니다. 로그를 확인해주세요:"
    docker-compose logs
fi

echo ""
echo "📋 유용한 명령어:"
echo "  - 로그 확인: docker-compose logs"
echo "  - 서비스 중지: docker-compose down"
echo "  - 서비스 재시작: docker-compose restart"