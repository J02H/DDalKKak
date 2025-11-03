from flask import Flask, jsonify, request, session
from flask_cors import CORS
import json
import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'ddalkkak-secret-key-2024'
CORS(app, supports_credentials=True)  # 세션 쿠키 지원

# 간단한 사용자 데이터 (실제로는 데이터베이스 사용)
USERS = {
    'admin': 'admin123',
    'student': 'student123',
    'test': 'test123'
}

# 사용자 프로필 데이터
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

# 사용자별 즐겨찾기 (메모리 저장)
USER_BOOKMARKS = {}

# 공지사항 요약 정보 추출 함수
def extract_notice_summary(content):
    """공지사항 내용에서 중요 정보 추출"""
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
            
        # 마감일/기한 추출
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
        
        # 장소 추출
        location_keywords = ['장소', '위치', '강의실', '호실', '건물', '캠퍼스', '층']
        for keyword in location_keywords:
            if keyword in line and not summary['location']:
                # 키워드 다음 내용 추출
                parts = line.split(keyword)
                if len(parts) > 1:
                    location_part = parts[1].strip()
                    # 첫 번째 문장이나 의미있는 부분만 추출
                    location_match = re.search(r'[^\n.!?]*', location_part)
                    if location_match:
                        summary['location'] = location_match.group().strip()[:50]
                        break
        
        # 보상/혜택 추출
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
        
        # 비용 추출
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
        
        # 연락처 추출
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
        
        # 중요 날짜들 추출
        date_pattern = r'([0-9]{1,2}월\s*[0-9]{1,2}일|[0-9]{4}[.-][0-9]{1,2}[.-][0-9]{1,2})'
        dates = re.findall(date_pattern, line)
        for date in dates:
            if date not in summary['important_dates'] and len(summary['important_dates']) < 3:
                summary['important_dates'].append(date)
        
        # 핵심 포인트 추출 (짧고 중요한 문장들)
        if any(keyword in line for keyword in ['필수', '중요', '주의', '반드시', '꼭']):
            if len(line) < 100 and line not in summary['key_points'] and len(summary['key_points']) < 3:
                summary['key_points'].append(line)
    
    return summary

# 공지사항 내용 크롤링 및 요약 함수
def crawl_notice_content(url):
    """공지사항 내용을 크롤링하여 요약 정보 반환"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 요소들 제거
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
            element.decompose()
        
        # 공지사항 내용 추출
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
        
        # 내용이 없으면 전체 페이지에서 추출
        if not content or len(content) < 50:
            content = soup.get_text(strip=True, separator='\n')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
        
        # 불필요한 텍스트 제거
        unwanted_texts = ['본문 바로가기', '주메뉴 바로가기', 'MAIL', '학사정보', '교직원포탈', 'KU Service', 'Popup']
        for unwanted in unwanted_texts:
            content = content.replace(unwanted, '')
        
        # 요약 정보 추출
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

# 전체 공지사항 데이터 업데이트 함수
def update_notices_data():
    """매일 공지사항 데이터 업데이트"""
    print(f"[{datetime.now()}] 공지사항 데이터 업데이트 시작...")
    try:
        # 여기에 실제 크롤링 로직 추가 (기존 크롤러 사용)
        # 현재는 로그만 출력
        print(f"[{datetime.now()}] 공지사항 데이터 업데이트 완료")
    except Exception as e:
        print(f"[{datetime.now()}] 공지사항 업데이트 실패: {str(e)}")

# 스케줄러 실행 함수
def run_scheduler():
    """백그라운드에서 스케줄러 실행"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

# JSON 데이터 로드
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

@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    """모든 학부 목록 반환"""
    notices = load_notices()
    colleges = list(notices.keys())
    return jsonify({
        'success': True,
        'colleges': colleges
    })

@app.route('/api/departments/<college>', methods=['GET'])
def get_departments(college):
    """특정 학부의 학과 목록 반환"""
    notices = load_notices()
    if college in notices:
        departments = list(notices[college].keys())
        return jsonify({
            'success': True,
            'college': college,
            'departments': departments
        })
    return jsonify({
        'success': False,
        'message': '학부를 찾을 수 없습니다.'
    }), 404

@app.route('/api/notices/<college>/<department>', methods=['GET'])
def get_notices(college, department):
    """특정 학과의 공지사항 반환"""
    notices = load_notices()
    if college in notices and department in notices[college]:
        # 네비게이션 메뉴 항목 필터링
        filtered_notices = [
            notice for notice in notices[college][department]
            if notice['title'] not in ['HOME', '글로컬캠퍼스', '서울캠퍼스']
        ]
        return jsonify({
            'success': True,
            'college': college,
            'department': department,
            'notices': filtered_notices
        })
    return jsonify({
        'success': False,
        'message': '학과를 찾을 수 없습니다.'
    }), 404

@app.route('/api/all-notices', methods=['GET'])
def get_all_notices():
    """모든 공지사항 반환"""
    notices = load_notices()
    return jsonify({
        'success': True,
        'data': notices
    })

@app.route('/api/notice/<college>/<department>/<int:notice_id>', methods=['GET'])
def get_notice_detail(college, department, notice_id):
    """특정 공지사항 상세 정보 반환"""
    notices = load_notices()
    if college in notices and department in notices[college]:
        dept_notices = notices[college][department]
        if 0 <= notice_id < len(dept_notices):
            notice = dept_notices[notice_id]
            return jsonify({
                'success': True,
                'college': college,
                'department': department,
                'notice_id': notice_id,
                'notice': notice
            })
    return jsonify({
        'success': False,
        'message': '공지사항을 찾을 수 없습니다.'
    }), 404

@app.route('/api/notice-content', methods=['POST'])
def get_notice_content():
    """공지사항 내용 크롤링 및 요약"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({
            'success': False,
            'message': 'URL이 필요합니다.'
        }), 400
    
    result = crawl_notice_content(url)
    
    return jsonify({
        'success': True,
        'content': result.get('content', ''),
        'summary': result.get('summary', {})
    })

@app.route('/api/search', methods=['GET'])
def search_notices():
    """공지사항 검색"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({
            'success': False,
            'message': '검색어를 입력해주세요.'
        }), 400
    
    notices = load_notices()
    results = []
    
    for college, departments in notices.items():
        for department, dept_notices in departments.items():
            for i, notice in enumerate(dept_notices):
                # 네비게이션 메뉴 항목 제외
                if notice['title'] not in ['HOME', '글로컬캠퍼스', '서울캠퍼스'] and query in notice['title'].lower():
                    results.append({
                        **notice,
                        'college': college,
                        'notice_id': i
                    })
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })

@app.route('/api/register', methods=['POST'])
def register():
    """회원가입"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')
    department = data.get('department')
    student_id = data.get('student_id')
    
    # 입력 값 검증
    if not all([username, password, name, email, department]):
        return jsonify({
            'success': False,
            'message': '모든 필수 항목을 입력해주세요.'
        }), 400
    
    # 중복 아이디 검사
    if username in USERS:
        return jsonify({
            'success': False,
            'message': '이미 사용 중인 아이디입니다.'
        }), 400
    
    # 사용자 등록
    USERS[username] = password
    USER_PROFILES[username] = {
        'name': name,
        'email': email,
        'department': department,
        'student_id': student_id or '',
        'join_date': '2025-11-03'
    }
    
    return jsonify({
        'success': True,
        'message': '회원가입이 완료되었습니다.'
    })

@app.route('/api/login', methods=['POST'])
def login():
    """로그인"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return jsonify({
            'success': True,
            'message': '로그인 성공',
            'user': username
        })
    
    return jsonify({
        'success': False,
        'message': '아이디 또는 비밀번호가 잘못되었습니다.'
    }), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """로그아웃"""
    session.pop('user', None)
    return jsonify({
        'success': True,
        'message': '로그아웃 되었습니다.'
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    """현재 로그인된 사용자 정보"""
    if 'user' in session:
        return jsonify({
            'success': True,
            'user': session['user'],
            'logged_in': True
        })
    
    return jsonify({
        'success': True,
        'logged_in': False
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """사용자 프로필 정보"""
    if 'user' not in session:
        return jsonify({
            'success': False,
            'message': '로그인이 필요합니다.'
        }), 401
    
    username = session['user']
    profile = USER_PROFILES.get(username, {})
    
    return jsonify({
        'success': True,
        'profile': {
            'username': username,
            **profile
        }
    })

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """사용자 즐겨찾기 목록"""
    if 'user' not in session:
        return jsonify({
            'success': False,
            'message': '로그인이 필요합니다.'
        }), 401
    
    username = session['user']
    bookmarks = USER_BOOKMARKS.get(username, [])
    
    return jsonify({
        'success': True,
        'bookmarks': bookmarks
    })

@app.route('/api/bookmarks', methods=['POST'])
def toggle_bookmark():
    """즐겨찾기 토글 (추가/제거)"""
    if 'user' not in session:
        return jsonify({
            'success': False,
            'message': '로그인이 필요합니다.'
        }), 401
    
    data = request.get_json()
    username = session['user']
    
    if username not in USER_BOOKMARKS:
        USER_BOOKMARKS[username] = []
    
    bookmark_id = data.get('id')
    
    # 기존 즐겨찾기 체크
    existing_bookmark = next((b for b in USER_BOOKMARKS[username] if b['id'] == bookmark_id), None)
    
    if existing_bookmark:
        # 제거
        USER_BOOKMARKS[username] = [b for b in USER_BOOKMARKS[username] if b['id'] != bookmark_id]
        return jsonify({
            'success': True,
            'action': 'removed',
            'message': '즐겨찾기에서 제거되었습니다.'
        })
    else:
        # 추가
        bookmark = {
            'id': data.get('id'),
            'title': data.get('title'),
            'college': data.get('college'),
            'department': data.get('department'),
            'date': data.get('date'),
            'link': data.get('link'),
            'added_date': '2025-11-03'
        }
        USER_BOOKMARKS[username].append(bookmark)
        return jsonify({
            'success': True,
            'action': 'added',
            'message': '즐겨찾기에 추가되었습니다.'
        })

@app.route('/api/bookmarks/<bookmark_id>', methods=['DELETE'])
def remove_bookmark(bookmark_id):
    """즐겨찾기 삭제"""
    if 'user' not in session:
        return jsonify({
            'success': False,
            'message': '로그인이 필요합니다.'
        }), 401
    
    username = session['user']
    
    if username in USER_BOOKMARKS:
        USER_BOOKMARKS[username] = [
            b for b in USER_BOOKMARKS[username] if b['id'] != bookmark_id
        ]
    
    return jsonify({
        'success': True,
        'message': '즐겨찾기에서 삭제되었습니다.'
    })

@app.route('/api/update-files', methods=['POST'])
def update_files():
    """서버 파일 업데이트"""
    try:
        data = request.get_json()
        
        # HTML 파일 업데이트
        if 'html' in data:
            with open('/usr/share/nginx/html/index.html', 'w', encoding='utf-8') as f:
                f.write(data['html'])
        
        # 백엔드 파일 업데이트
        if 'backend' in data:
            with open('backend/app.py', 'w', encoding='utf-8') as f:
                f.write(data['backend'])
        
        return jsonify({
            'success': True,
            'message': '파일 업데이트 완료'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'업데이트 실패: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 매일 오전 00:00에 공지사항 업데이트 스케줄 등록
    schedule.every().day.at("00:00").do(update_notices_data)
    
    # 스케줄러 백그라운드 실행
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("🔖 매일 오전 00:00에 공지사항 자동 업데이트 예약됨")
    
    app.run(debug=True, host='0.0.0.0', port=8080)