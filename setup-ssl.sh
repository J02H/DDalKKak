#!/bin/bash

# 도메인 입력 받기
read -p "도메인을 입력하세요 (예: example.com): " DOMAIN
read -p "이메일을 입력하세요: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ 도메인과 이메일을 모두 입력해주세요."
    exit 1
fi

echo "🔒 SSL 인증서 설정 시작: $DOMAIN"

# Certbot 설치
echo "📦 Certbot 설치 중..."
sudo apt update
sudo apt install -y certbot

# 기존 컨테이너 중지
echo "⏸️ 기존 서비스 중지 중..."
docker-compose down

# SSL 인증서 발급
echo "🔐 SSL 인증서 발급 중..."
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

# nginx 설정 파일 업데이트
echo "⚙️ Nginx 설정 업데이트 중..."
cp nginx-domain.conf nginx.conf
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Docker Compose 파일 업데이트 (SSL 볼륨 마운트 추가)
cat > docker-compose-ssl.yml << EOF
services:
  backend:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./kku_glocal_all_notices.json:/app/kku_glocal_all_notices.json:ro
      - ./notices_by_college:/app/notices_by_college:ro
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
    restart: unless-stopped
EOF

# SSL 설정으로 서비스 재시작
echo "🚀 SSL 설정으로 서비스 시작 중..."
docker-compose -f docker-compose-ssl.yml up -d

# SSL 인증서 자동 갱신 설정
echo "🔄 SSL 인증서 자동 갱신 설정 중..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f $(pwd)/docker-compose-ssl.yml restart nginx") | crontab -

echo "✅ SSL 설정 완료!"
echo "🌐 웹사이트: https://$DOMAIN"
echo "🔒 SSL 인증서가 자동으로 갱신됩니다."