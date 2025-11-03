#!/bin/bash

echo "🚀 건국대 글로컬 공지사항 시스템 - 서버 설정 스크립트"

# Ubuntu/Debian 시스템 확인
if ! command -v apt &> /dev/null; then
    echo "❌ 이 스크립트는 Ubuntu/Debian 시스템용입니다."
    exit 1
fi

# 시스템 업데이트
echo "📦 시스템 패키지 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# Docker 설치
echo "🐳 Docker 설치 중..."
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Docker GPG 키 추가
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker 저장소 추가
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치 (standalone)
echo "🔧 Docker Compose 설치 중..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 방화벽 설정
echo "🔥 방화벽 설정 중..."
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw --force enable

# Git 설치
echo "📥 Git 설치 중..."
sudo apt install -y git

echo "✅ 서버 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. 터미널을 재시작하거나 다음 명령어 실행: newgrp docker"
echo "2. 프로젝트 클론: git clone <repository-url>"
echo "3. 프로젝트 디렉토리로 이동: cd DDalKKak"
echo "4. 배포 실행: ./deploy.sh"
echo ""
echo "🌐 배포 완료 후 http://your-server-ip 에서 접속 가능합니다."