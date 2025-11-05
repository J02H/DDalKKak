import os
import firebase_admin
from firebase_admin import credentials, db, auth

# Firebase 초기화
def init_firebase():
    # 이미 초기화돼 있으면 다시 하지 않음
    if not firebase_admin._apps:
        # 서비스 계정 키 파일 경로 (/app/backend 기준 상위 디렉터리)
        key_path = os.path.join(os.path.dirname(__file__), '..', 'ddalkkak-firebase-key.json')

        # 서비스 계정 JSON 파일로부터 자격 증명 생성
        cred = credentials.Certificate(key_path)

        # Realtime Database URL (환경변수 우선)
        database_url = os.getenv(
            "FIREBASE_DATABASE_URL",
            "https://ddalkkak-e1c8e-default-rtdb.firebaseio.com/"
        )

        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

    # 여기서 db 모듈을 돌려주면, 다른 코드에서 db.reference(...) 형태로 사용 가능
    return db


# app.py 가 import 하는 함수
def get_db():
    """
    기존 코드 호환용 래퍼 함수.
    FastAPI 코드에서 get_db()를 호출하면,
    내부적으로 Firebase를 초기화하고 db 모듈을 반환.
    """
    return init_firebase()
