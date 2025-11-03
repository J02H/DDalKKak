#!/bin/bash

echo "🚀 건국대 글로컬 공지사항 시스템 - 자동 서버 배포"

# 서버 정보 입력
read -p "서버 IP 주소를 입력하세요: " SERVER_IP
read -p "서버 사용자명을 입력하세요 (기본: ubuntu): " SERVER_USER
SERVER_USER=${SERVER_USER:-ubuntu}

if [ -z "$SERVER_IP" ]; then
    echo "❌ 서버 IP 주소를 입력해주세요."
    exit 1
fi

echo "📦 배포 파일 준비 중..."

# 배포에 필요한 파일만 압축
tar -czf deploy-package.tar.gz \
    backend/ \
    frontend/ \
    kku_glocal_all_notices.json \
    notices_by_college/ \
    Dockerfile \
    docker-compose.yml \
    nginx.conf \
    deploy.sh \
    server-setup.sh \
    setup-ssl.sh \
    nginx-domain.conf \
    README.md

echo "📤 서버로 파일 업로드 중..."
# 키 파일 찾기
KEY_FILE=""
for key in *.pem; do
    if [ -f "$key" ]; then
        KEY_FILE="$key"
        chmod 400 "$key"
        break
    fi
done

if [ -z "$KEY_FILE" ]; then
    echo "❌ .pem 키 파일을 찾을 수 없습니다."
    exit 1
fi

echo "🔑 키 파일 사용: $KEY_FILE"
scp -i "$KEY_FILE" deploy-package.tar.gz $SERVER_USER@$SERVER_IP:~/

echo "🔧 서버에서 배포 실행 중..."
ssh -i "$KEY_FILE" $SERVER_USER@$SERVER_IP << 'EOF'
    # 기존 디렉토리 제거
    rm -rf DDalKKak
    
    # 파일 압축 해제
    tar -xzf deploy-package.tar.gz
    mkdir -p DDalKKak
    mv backend frontend kku_glocal_all_notices.json notices_by_college Dockerfile docker-compose.yml nginx.conf deploy.sh server-setup.sh setup-ssl.sh nginx-domain.conf README.md DDalKKak/
    cd DDalKKak
    
    # 서버 설정 (Docker 등)
    if ! command -v docker &> /dev/null; then
        echo "🐳 Docker 설치 중..."
        chmod +x server-setup.sh
        ./server-setup.sh
        newgrp docker
    fi
    
    # 배포 실행
    echo "🚀 서비스 배포 중..."
    chmod +x deploy.sh
    ./deploy.sh
    
    # 임시 파일 정리
    rm -f ~/deploy-package.tar.gz
    
    echo "✅ 서버 배포 완료!"
    echo "🌐 웹사이트: http://$SERVER_IP"
EOF

# 로컬 임시 파일 정리
rm -f deploy-package.tar.gz

echo "🎉 자동 배포 완료!"
echo "🌐 웹사이트: http://$SERVER_IP"