#!/bin/bash

echo "🚀 AWS EC2 배포"

# 키 파일 자동 찾기
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
    echo "💡 키 파일을 이 폴더에 복사하세요: cp ~/Downloads/your-key.pem ."
    exit 1
fi

# EC2 IP 입력
read -p "EC2 IP 주소를 입력하세요: " EC2_IP
if [ -z "$EC2_IP" ]; then
    echo "❌ EC2 IP 주소를 입력해주세요."
    exit 1
fi

echo "🔑 키 파일: $KEY_FILE"
echo "📤 파일 업로드 중..."

# 파일 업로드
scp -i "$KEY_FILE" -r . ubuntu@$EC2_IP:~/DDalKKak/

echo "🔧 서버에서 배포 실행 중..."
ssh -i "$KEY_FILE" ubuntu@$EC2_IP << 'EOF'
    cd DDalKKak
    
    # Docker 설치 확인
    if ! command -v docker &> /dev/null; then
        echo "🐳 Docker 설치 중..."
        sudo apt update
        sudo apt install -y docker.io docker-compose
        sudo systemctl start docker
        sudo usermod -aG docker ubuntu
        echo "⚠️  Docker 설치 완료. 다시 실행해주세요: ./deploy-aws.sh"
        exit 1
    fi
    
    # 배포 실행
    ./deploy.sh
EOF

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료!"
    echo "🌐 웹사이트: http://$EC2_IP"
else
    echo "⚠️  Docker 설치 완료. 다시 실행하세요: ./deploy-aws.sh"
fi