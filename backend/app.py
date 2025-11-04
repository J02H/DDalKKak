from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime
import re
from typing import Dict, List, Optional
from firebase_config import get_db

app = FastAPI(title="DDalKKak API", version="1.0.0")

# Firebase 초기화
try:
    db = get_db()
    print("✅ Firebase 연결 성공")
except Exception as e:
    print(f"❌ Firebase 연결 실패: {e}")
    db = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}

class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    email: str
    department: str
    student_id: Optional[str] = ""

class UserLogin(BaseModel):
    username: str
    password: str

class NoticeContent(BaseModel):
    url: str

class BookmarkData(BaseModel):
    id: str
    title: str
    college: str
    department: str
    date: str
    link: str

USERS = {
    'admin': 'admin123',
    'student': 'student123',
}

USER_PROFILES = {
    'admin': {
        'name': '관리자',
        'email': 'admin@kku.ac.kr',
        'department': '전산팀',
        'student_id': 'ADMIN001',
        'join_date': '2024-01-01'
    },
    'student': {
        'name': '김학생',
        'email': 'student@kku.ac.kr', 
        'department': '컴퓨터공학과',
        'student_id': '202012345',
        'join_date': '2024-03-01'
    },
}

USER_BOOKMARKS = {}

# Firebase 데이터베이스 함수들
def create_user_in_db(username, user_data):
    if db:
        try:
            db.collection('users').document(username).set(user_data)
            return True
        except Exception as e:
            print(f"DB 사용자 생성 오류: {e}")
    return False

def get_user_from_db(username):
    if db:
        try:
            doc = db.collection('users').document(username).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"DB 사용자 조회 오류: {e}")
    return None

def add_bookmark_to_db(username, bookmark):
    if db:
        try:
            db.collection('bookmarks').add({
                'username': username,
                'bookmark_id': bookmark['id'],
                'title': bookmark['title'],
                'college': bookmark['college'],
                'department': bookmark['department'],
                'date': bookmark['date'],
                'link': bookmark['link'],
                'added_date': bookmark['added_date']
            })
            return True
        except Exception as e:
            print(f"DB 즐겨찾기 추가 오류: {e}")
    return False

def get_bookmarks_from_db(username):
    if db:
        try:
            docs = db.collection('bookmarks').where('username', '==', username).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"DB 즐겨찾기 조회 오류: {e}")
    return []

def extract_notice_summary(content):
    summary = {
        'deadline': None,
        'location': None,
        'reward': None,
        'cost': None,
        'contact': None,
        'requirements': [],
        'important_dates': [],
        'key_points': []
    }
    
    if not content:
        return summary
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        deadline_patterns = [
            r'마감.*?([0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})',
            r'접수.*?([0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})',
            r'신청.*?([0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})',
            r'까지.*?([0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})',
            r'([0-9]{1,2}월\s*[0-9]{1,2}일).*?까지',
            r'([0-9]{1,2}/[0-9]{1,2}).*?까지'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, line)
            if match and not summary['deadline']:
                summary['deadline'] = match.group(1)
                break
        
        location_keywords = ['장소', '위치', '강의실', '호실', '건물', '캠퍼스', '층']
        for keyword in location_keywords:
            if keyword in line and not summary['location']:
                parts = line.split(keyword)
                if len(parts) > 1:
                    location_part = parts[1].strip()
                    location_match = re.search(r'[^\n.!?]*', location_part)
                    if location_match:
                        summary['location'] = location_match.group().strip()[:50]
                        break
        
        reward_patterns = [
            r'(다드림포인트\s*[0-9,]+\s*포인트)',
            r'(장학금\s*[0-9,]+\s*원)',
            r'(상금\s*[0-9,]+\s*원)',
            r'(포인트\s*[0-9,]+)',
            r'(학점\s*[0-9]+)',
            r'(수료증)',
            r'(인증서)',
            r'(봉사시간\s*[0-9]+시간)'
        ]
        
        for pattern in reward_patterns:
            match = re.search(pattern, line)
            if match and not summary['reward']:
                summary['reward'] = match.group(1)
                break
        
        cost_patterns = [
            r'(참가비\s*[0-9,]+\s*원)',
            r'(수강료\s*[0-9,]+\s*원)',
            r'(비용\s*[0-9,]+\s*원)',
            r'(무료)',
            r'(무료참가)',
            r'([0-9,]+원)'
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, line)
            if match and not summary['cost']:
                summary['cost'] = match.group(1)
                break
        
        contact_patterns = [
            r'(문의.*?[0-9]{2,4}-[0-9]{3,4}-[0-9]{4})',
            r'(연락처.*?[0-9]{2,4}-[0-9]{3,4}-[0-9]{4})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, line)
            if match and not summary['contact']:
                summary['contact'] = match.group(1)
                break
        
        date_pattern = r'([0-9]{1,2}월\s*[0-9]{1,2}일|[0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})'
        dates = re.findall(date_pattern, line)
        for date in dates:
            if date not in summary['important_dates'] and len(summary['important_dates']) < 3:
                summary['important_dates'].append(date)
        
        if any(keyword in line for keyword in ['필수', '중요', '주의', '반드시', '꼭']):
            if len(line) < 100 and line not in summary['key_points'] and len(summary['key_points']) < 3:
                summary['key_points'].append(line)
    
    return summary

def crawl_notice_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
            element.decompose()
        
        content_selectors = [
            '.board_view_content',
            '.view_content', 
            '.content_view',
            '.board-content',
            '.post-content',
            '.article-content',
            '.notice-content',
            '.view-content',
            '.txt_area',
            '.board_txt'
        ]
        
        content = ''
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(strip=True, separator='\n')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = '\n'.join(lines)
                if len(content) > 100:
                    break
        
        if not content or len(content) < 50:
            content = soup.get_text(strip=True, separator='\n')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
        
        unwanted_texts = ['본문 바로가기', '주메뉴 바로가기', 'MAIL', '학사정보', '교직원포탈', 'KU Service', 'Popup']
        for unwanted in unwanted_texts:
            content = content.replace(unwanted, '')
        
        summary = extract_notice_summary(content)
        
        return {
            'content': content[:1000] if content else '내용을 찾을 수 없습니다.',
            'summary': summary
        }
        
    except Exception as e:
        return {
            'content': f'내용을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'summary': {}
        }

def update_notices_data():
    print(f"[{datetime.now()}] 공지사항 데이터 업데이트 시작...")
    try:
        print(f"[{datetime.now()}] 공지사항 데이터 업데이트 완료")
    except Exception as e:
        print(f"[{datetime.now()}] 공지사항 업데이트 실패: {str(e)}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

def load_notices():
    try:
        with open('kku_glocal_all_notices.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            with open('../kku_glocal_all_notices.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSIONS:
        return SESSIONS[session_id]
    return None

@app.get("/api/colleges")
async def get_colleges():
    notices = load_notices()
    colleges = list(notices.keys())
    return {
        "success": True,
        "colleges": colleges
    }

@app.get("/api/departments/{college}")
async def get_departments(college: str):
    notices = load_notices()
    if college in notices:
        departments = list(notices[college].keys())
        return {
            "success": True,
            "college": college,
            "departments": departments
        }
    raise HTTPException(status_code=404, detail="학부를 찾을 수 없습니다.")

@app.get("/api/notices/{college}/{department}")
async def get_notices(college: str, department: str):
    notices = load_notices()
    if college in notices and department in notices[college]:
        filtered_notices = [
            notice for notice in notices[college][department]
            if notice['title'] not in ['HOME', '글로컬캠퍼스', '서울캠퍼스']
        ]
        return {
            "success": True,
            "college": college,
            "department": department,
            "notices": filtered_notices
        }
    raise HTTPException(status_code=404, detail="학과를 찾을 수 없습니다.")

@app.get("/api/all-notices")
async def get_all_notices():
    notices = load_notices()
    return {
        "success": True,
        "data": notices
    }

@app.get("/api/notice/{college}/{department}/{notice_id}")
async def get_notice_detail(college: str, department: str, notice_id: int):
    notices = load_notices()
    if college in notices and department in notices[college]:
        dept_notices = notices[college][department]
        if 0 <= notice_id < len(dept_notices):
            notice = dept_notices[notice_id]
            return {
                "success": True,
                "college": college,
                "department": department,
                "notice_id": notice_id,
                "notice": notice
            }
    raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")

@app.post("/api/notice-content")
async def get_notice_content(data: NoticeContent):
    if not data.url:
        raise HTTPException(status_code=400, detail="URL이 필요합니다.")
    
    result = crawl_notice_content(data.url)
    
    return {
        "success": True,
        "content": result.get('content', ''),
        "summary": result.get('summary', {})
    }

@app.get("/api/search")
async def search_notices(q: str = ""):
    if not q:
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")
    
    notices = load_notices()
    results = []
    
    for college, departments in notices.items():
        for department, dept_notices in departments.items():
            for i, notice in enumerate(dept_notices):
                if notice['title'] not in ['HOME', '글로컬캠퍼스', '서울캠퍼스'] and q.lower() in notice['title'].lower():
                    results.append({
                        **notice,
                        'college': college,
                        'notice_id': i
                    })
    
    return {
        "success": True,
        "query": q,
        "count": len(results),
        "results": results
    }

@app.post("/api/register")
async def register(user_data: UserRegister):
    if user_data.username in USERS:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    
    # Firebase에 사용자 데이터 저장
    user_profile = {
        'username': user_data.username,
        'password': user_data.password,
        'name': user_data.name,
        'email': user_data.email,
        'department': user_data.department,
        'student_id': user_data.student_id or '',
        'join_date': '2025-11-03'
    }
    
    if create_user_in_db(user_data.username, user_profile):
        print(f"✅ Firebase에 사용자 {user_data.username} 저장 성공")
    
    # 메모리에도 저장 (백업)
    USERS[user_data.username] = user_data.password
    USER_PROFILES[user_data.username] = {
        'name': user_data.name,
        'email': user_data.email,
        'department': user_data.department,
        'student_id': user_data.student_id or '',
        'join_date': '2025-11-03'
    }
    
    return {
        "success": True,
        "message": "회원가입이 완료되었습니다."
    }

@app.post("/api/login")
async def login(user_data: UserLogin):
    if user_data.username in USERS and USERS[user_data.username] == user_data.password:
        session_id = f"session_{user_data.username}_{int(time.time())}"
        SESSIONS[session_id] = user_data.username
        
        response = JSONResponse({
            "success": True,
            "message": "로그인 성공",
            "user": user_data.username
        })
        response.set_cookie("session_id", session_id, httponly=True)
        return response
    
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

@app.post("/api/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    
    response = JSONResponse({
        "success": True,
        "message": "로그아웃 되었습니다."
    })
    response.delete_cookie("session_id")
    return response

@app.get("/api/user")
async def get_user(request: Request):
    current_user = get_current_user(request)
    if current_user:
        return {
            "success": True,
            "user": current_user,
            "logged_in": True
        }
    
    return {
        "success": True,
        "logged_in": False
    }

@app.get("/api/profile")
async def get_profile(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    profile = USER_PROFILES.get(current_user, {})
    
    return {
        "success": True,
        "profile": {
            "username": current_user,
            **profile
        }
    }

@app.get("/api/bookmarks")
async def get_bookmarks(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    bookmarks = USER_BOOKMARKS.get(current_user, [])
    
    return {
        "success": True,
        "bookmarks": bookmarks
    }

@app.post("/api/bookmarks")
async def toggle_bookmark(bookmark_data: BookmarkData, request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    if current_user not in USER_BOOKMARKS:
        USER_BOOKMARKS[current_user] = []
    
    existing_bookmark = next((b for b in USER_BOOKMARKS[current_user] if b['id'] == bookmark_data.id), None)
    
    if existing_bookmark:
        USER_BOOKMARKS[current_user] = [b for b in USER_BOOKMARKS[current_user] if b['id'] != bookmark_data.id]
        return {
            "success": True,
            "action": "removed",
            "message": "즐겨찾기에서 제거되었습니다."
        }
    else:
        bookmark = {
            'id': bookmark_data.id,
            'title': bookmark_data.title,
            'college': bookmark_data.college,
            'department': bookmark_data.department,
            'date': bookmark_data.date,
            'link': bookmark_data.link,
            'added_date': '2025-11-03'
        }
        USER_BOOKMARKS[current_user].append(bookmark)
        return {
            "success": True,
            "action": "added",
            "message": "즐겨찾기에 추가되었습니다."
        }

@app.delete("/api/bookmarks/{bookmark_id}")
async def remove_bookmark(bookmark_id: str, request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    if current_user in USER_BOOKMARKS:
        USER_BOOKMARKS[current_user] = [
            b for b in USER_BOOKMARKS[current_user] if b['id'] != bookmark_id
        ]
    
    return {
        "success": True,
        "message": "즐겨찾기에서 삭제되었습니다."
    }

if __name__ == '__main__':
    schedule.every().day.at("00:00").do(update_notices_data)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("🔖 매일 오전 00:00에 공지사항 자동 업데이트 예약됨")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)