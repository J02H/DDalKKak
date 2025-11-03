#!/bin/bash

echo "🚀 DDalKKak 배포 시작..."

# Docker 컨테이너 중지 및 제거
docker-compose down

# Docker 이미지 빌드 및 실행
docker-compose up -d --build

echo "✅ 배포 완료!"
echo "🌐 http://localhost 에서 확인하세요."