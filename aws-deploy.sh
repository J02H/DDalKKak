#!/bin/bash

echo "🚀 AWS EC2 자동 배포 스크립트"

# EC2 정보 입력
read -p "EC2 퍼블릭 IP 주소를 입력하세요: " EC2_IP
read -p "키 파일 경로를 입력하세요 (기본: ~/Downloads/DDalKKak-key.pem): " KEY_PATH
KEY_PATH=${KEY_PATH:-~/Downloads/DDalKKak-key.pem}

if [ -z "$EC2_IP" ]; then
    echo "❌ EC2 IP 주소를 입력해주세요."
    exit 1
fi

# 키 파일 권한 설정
chmod 400 $KEY_PATH

echo "📦 배포 파일 준비 중..."

# 배포 패키지 생성
tar -czf aws-deploy-package.tar.gz \
    backend/ \
    frontend/ \
    kku_glocal_all_notices.json \
    notices_by_college/ \
    Dockerfile \
    docker-compose.yml \
    nginx.conf \
    deploy.sh \
    server-setup.sh

echo "📤 EC2로 파일 업로드 중..."
scp -i $KEY_PATH aws-deploy-package.tar.gz ubuntu@$EC2_IP:~/

echo "🔧 EC2에서 배포 실행 중..."
ssh -i $KEY_PATH ubuntu@$EC2_IP << 'EOF'
    # 기존 디렉토리 제거
    sudo rm -rf DDalKKak
    
    # 파일 압축 해제
    tar -xzf aws-deploy-package.tar.gz
    mkdir -p DDalKKak
    mv backend frontend kku_glocal_all_notices.json notices_by_college Dockerfile docker-compose.yml nginx.conf deploy.sh server-setup.sh DDalKKak/
    cd DDalKKak
    
    # 서버 설정 (Docker 설치)
    if ! command -v docker &> /dev/null; then
        echo "🐳 Docker 설치 중..."
        chmod +x server-setup.sh
        ./server-setup.sh
        
        # Docker 그룹 적용
        sudo usermod -aG docker ubuntu
        newgrp docker << 'DOCKER_EOF'
            # 배포 실행
            echo "🚀 서비스 배포 중..."
            chmod +x deploy.sh
            ./deploy.sh
DOCKER_EOF
    else
        # 배포 실행
        echo "🚀 서비스 배포 중..."
        chmod +x deploy.sh
        ./deploy.sh
    fi
    
    # 임시 파일 정리
    rm -f ~/aws-deploy-package.tar.gz
    
    echo "✅ AWS EC2 배포 완료!"
EOF

# 로컬 임시 파일 정리
rm -f aws-deploy-package.tar.gz

echo "🎉 AWS EC2 배포 완료!"
echo "🌐 웹사이트: http://$EC2_IP"
echo "📋 EC2 관리: https://console.aws.amazon.com/ec2/"