#!/bin/bash

echo "🚀 AWS EC2 간단 배포"

# 키 파일 확인
if [ ! -f "DDalKKak-key.pem" ]; then
    echo "❌ DDalKKak-key.pem 파일이 없습니다."
    echo "키 파일을 이 폴더로 복사하세요:"
    echo "cp ~/Downloads/DDalKKak-key.pem ."
    exit 1
fi

# 키 파일 권한 설정
chmod 400 DDalKKak-key.pem

# EC2 IP 입력
read -p "EC2 IP 주소 (54.180.30.98): " EC2_IP
EC2_IP=${EC2_IP:-54.180.30.98}

echo "📤 파일 업로드 중..."
scp -i DDalKKak-key.pem -r . ubuntu@$EC2_IP:~/DDalKKak/

echo "🔧 서버 설정 및 배포 중..."
ssh -i DDalKKak-key.pem ubuntu@$EC2_IP << 'EOF'
    cd DDalKKak
    
    # Docker 설치
    if ! command -v docker &> /dev/null; then
        sudo apt update
        sudo apt install -y docker.io docker-compose
        sudo systemctl start docker
        sudo usermod -aG docker ubuntu
        echo "Docker 설치 완료. 재접속 필요."
        exit
    fi
    
    # 배포 실행
    ./deploy.sh
EOF

echo "✅ 배포 완료!"
echo "🌐 웹사이트: http://$EC2_IP"