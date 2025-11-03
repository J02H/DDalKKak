from fastapi import FastAPI, HTTPException, Request, Depends
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
from typing import Optional, Dict, List

app = FastAPI(title="DDalKKak API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 간단한 사용자 데이터
USERS = {
    'admin': 'admin123',
    'student': 'student123',
    'test': 'test123'
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
    'test': {
        'name': '테스트',
        'email': 'test@kku.ac.kr',
        'department': '소프트웨어학과',
        'student_id': '202098765',
        'join_date': '2024-09-01'
    }
}

USER_BOOKMARKS = {}
USER_SESSIONS = {}

# Pydantic 모델들
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    email: str
    department: str
    student_id: Optional[str] = None

class BookmarkRequest(BaseModel):
    id: str
    title: str
    college: str
    department: str
    date: str
    link: str

class NoticeContentRequest(BaseModel):
    url: str

# JSON 데이터 로드
def load_notices():
    try:
        with open('kku_glocal_all_notices.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 세션 관리
def get_current_user(request: Request) -> Optional[str]:
    session_id = request.cookies.get("session_id")
    if session_id and session_id in USER_SESSIONS:
        return USER_SESSIONS[session_id]
    return None

def require_auth(request: Request) -> str:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user

@app.get("/api/colleges")
async def get_colleges():
    """모든 학부 목록 반환"""
    notices = load_notices()
    colleges = list(notices.keys())
    return {"success": True, "colleges": colleges}

@app.get("/api/departments/{college}")
async def get_departments(college: str):
    """특정 학부의 학과 목록 반환"""
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
    """특정 학과의 공지사항 반환"""
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
    """모든 공지사항 반환"""
    notices = load_notices()
    return {"success": True, "data": notices}

@app.get("/api/notice/{college}/{department}/{notice_id}")
async def get_notice_detail(college: str, department: str, notice_id: int):
    """특정 공지사항 상세 정보 반환"""
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

@app.get("/api/search")
async def search_notices(q: str):
    """공지사항 검색"""
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
async def register(request: RegisterRequest):
    """회원가입"""
    if not all([request.username, request.password, request.name, request.email, request.department]):
        raise HTTPException(status_code=400, detail="모든 필수 항목을 입력해주세요.")
    
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    
    USERS[request.username] = request.password
    USER_PROFILES[request.username] = {
        'name': request.name,
        'email': request.email,
        'department': request.department,
        'student_id': request.student_id or '',
        'join_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    return {"success": True, "message": "회원가입이 완료되었습니다."}

@app.post("/api/login")
async def login(request: LoginRequest):
    """로그인"""
    if request.username in USERS and USERS[request.username] == request.password:
        session_id = f"session_{request.username}_{int(time.time())}"
        USER_SESSIONS[session_id] = request.username
        
        response = JSONResponse({
            "success": True,
            "message": "로그인 성공",
            "user": request.username
        })
        response.set_cookie("session_id", session_id, httponly=True)
        return response
    
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

@app.post("/api/logout")
async def logout(request: Request):
    """로그아웃"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in USER_SESSIONS:
        del USER_SESSIONS[session_id]
    
    response = JSONResponse({"success": True, "message": "로그아웃 되었습니다."})
    response.delete_cookie("session_id")
    return response

@app.get("/api/user")
async def get_user(request: Request):
    """현재 로그인된 사용자 정보"""
    user = get_current_user(request)
    if user:
        return {"success": True, "user": user, "logged_in": True}
    return {"success": True, "logged_in": False}

@app.get("/api/profile")
async def get_profile(request: Request):
    """사용자 프로필 정보"""
    username = require_auth(request)
    profile = USER_PROFILES.get(username, {})
    
    return {
        "success": True,
        "profile": {"username": username, **profile}
    }

@app.get("/api/bookmarks")
async def get_bookmarks(request: Request):
    """사용자 즐겨찾기 목록"""
    username = require_auth(request)
    bookmarks = USER_BOOKMARKS.get(username, [])
    return {"success": True, "bookmarks": bookmarks}

@app.post("/api/bookmarks")
async def toggle_bookmark(bookmark: BookmarkRequest, request: Request):
    """즐겨찾기 토글"""
    username = require_auth(request)
    
    if username not in USER_BOOKMARKS:
        USER_BOOKMARKS[username] = []
    
    existing_bookmark = next((b for b in USER_BOOKMARKS[username] if b['id'] == bookmark.id), None)
    
    if existing_bookmark:
        USER_BOOKMARKS[username] = [b for b in USER_BOOKMARKS[username] if b['id'] != bookmark.id]
        return {"success": True, "action": "removed", "message": "즐겨찾기에서 제거되었습니다."}
    else:
        bookmark_data = {
            **bookmark.dict(),
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        USER_BOOKMARKS[username].append(bookmark_data)
        return {"success": True, "action": "added", "message": "즐겨찾기에 추가되었습니다."}

@app.delete("/api/bookmarks/{bookmark_id}")
async def remove_bookmark(bookmark_id: str, request: Request):
    """즐겨찾기 삭제"""
    username = require_auth(request)
    
    if username in USER_BOOKMARKS:
        USER_BOOKMARKS[username] = [
            b for b in USER_BOOKMARKS[username] if b['id'] != bookmark_id
        ]
    
    return {"success": True, "message": "즐겨찾기에서 삭제되었습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)