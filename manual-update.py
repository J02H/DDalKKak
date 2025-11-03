#!/usr/bin/env python3
import requests
import time

def update_server():
    server_url = "http://52.79.109.92"
    
    # 서버가 응답하는지 확인
    try:
        response = requests.get(server_url, timeout=10)
        print(f"✅ 서버 응답: {response.status_code}")
        
        # 현재 HTML 내용 확인
        if "💻 LMS" in response.text:
            print("❌ 아직 LMS로 되어있음 - 수동 업데이트 필요")
        elif "💻 TLS" in response.text:
            print("✅ 이미 TLS로 업데이트됨")
        else:
            print("⚠️ LMS/TLS 텍스트를 찾을 수 없음")
            
        # 즐겨찾기 버튼 위치 확인
        if 'margin-right: 8px' in response.text:
            print("✅ 즐겨찾기 버튼이 왼쪽에 위치함")
        else:
            print("❌ 즐겨찾기 버튼 위치 업데이트 필요")
            
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")

if __name__ == "__main__":
    update_server()