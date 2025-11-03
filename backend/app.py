from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 프론트엔드에서 접근 가능하도록

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
        return jsonify({
            'success': True,
            'college': college,
            'department': department,
            'notices': notices[college][department]
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
                if query in notice['title'].lower():
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)