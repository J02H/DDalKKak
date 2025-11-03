#!/usr/bin/env python3
import requests
import json

# 서버에 직접 파일 업로드하는 API 엔드포인트 생성
def update_server_files():
    server_url = "http://52.79.109.92:8080"
    
    # HTML 파일 내용 읽기
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 백엔드 파일 내용 읽기
    with open('backend/app.py', 'r', encoding='utf-8') as f:
        backend_content = f.read()
    
    # 서버에 업데이트 요청
    try:
        response = requests.post(f"{server_url}/api/update-files", 
                               json={
                                   'html': html_content,
                                   'backend': backend_content
                               }, 
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ 서버 파일 업데이트 성공!")
        else:
            print(f"❌ 업데이트 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    update_server_files()