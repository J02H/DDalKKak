#!/bin/bash

echo "🚀 건국대 글로컬 공지사항 시스템 - 완전 자동 배포"

# 배포 옵션 선택
echo "배포 옵션을 선택하세요:"
echo "1) 로컬 테스트"
echo "2) 서버 배포"
echo "3) 서버 배포 + SSL 설정"

read -p "선택 (1-3): " OPTION

case $OPTION in
    1)
        echo "🏠 로컬 테스트 시작..."
        ./deploy.sh
        echo "✅ 로컬 배포 완료! http://localhost 에서 확인하세요."
        ;;
    2)
        echo "🌐 서버 배포 시작..."
        ./auto-deploy.sh
        ;;
    3)
        echo "🔒 서버 배포 + SSL 설정 시작..."
        ./auto-deploy.sh
        
        read -p "SSL 설정을 진행하시겠습니까? (y/n): " SSL_CONFIRM
        if [ "$SSL_CONFIRM" = "y" ]; then
            read -p "서버 IP 주소: " SERVER_IP
            read -p "서버 사용자명 (기본: ubuntu): " SERVER_USER
            SERVER_USER=${SERVER_USER:-ubuntu}
            
            echo "🔐 SSL 설정 중..."
            ssh $SERVER_USER@$SERVER_IP "cd DDalKKak && ./setup-ssl.sh"
        fi
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

# 배포 완료 후 정리
read -p "불필요한 파일을 정리하시겠습니까? (y/n): " CLEANUP
if [ "$CLEANUP" = "y" ]; then
    ./cleanup.sh
fi

echo "🎉 모든 작업이 완료되었습니다!"