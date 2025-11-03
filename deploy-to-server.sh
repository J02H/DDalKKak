#!/bin/bash

set -euo pipefail

# 서버 정보
SERVER_IP="52.79.109.92"
SERVER_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/DDalKKak"

echo "🚀 서버에 변경사항 배포 시작..."

# 1. 서버에 파일 복사

echo "📁 파일 복사 중..."
scp -o ConnectTimeout=30 -o StrictHostKeyChecking=no -r frontend/ backend/ docker-compose.yml kku_glocal_all_notices.json $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# 2. 서버에서 Docker 재빌드 및 재시작
echo "🔄 서버에서 Docker 재빌드 중..."
ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
cd /home/ubuntu/DDalKKak
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo "✅ 배포 완료!"
EOF

echo "🎉 서버 배포가 완료되었습니다!"
echo "🌐 http://52.79.109.92 에서 확인하세요."