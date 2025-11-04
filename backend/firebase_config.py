import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Firebase 초기화
def init_firebase():
    if not firebase_admin._apps:
        # 서비스 계정 키 파일 경로
        key_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-key.json')
        
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
        else:
            # 환경변수에서 설정 읽기
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": "ddalkkak-a4842",
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            })
        
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Firestore 클라이언트 가져오기
def get_db():
    return init_firebase()