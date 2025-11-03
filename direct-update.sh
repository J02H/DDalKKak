#!/bin/bash

# 직접 서버 파일 업데이트
SERVER_IP="52.79.109.92"

echo "🔄 서버 파일 직접 업데이트 중..."

# curl을 사용해서 서버에 직접 명령 전송
curl -X POST "http://$SERVER_IP:8080/api/update-files" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_html",
    "changes": [
      {"find": "💻 LMS", "replace": "💻 TLS"},
      {"find": "https://lms.kku.ac.kr", "replace": "https://tls.kku.ac.kr"}
    ]
  }' || echo "API 호출 실패"

echo "✅ 업데이트 완료!"