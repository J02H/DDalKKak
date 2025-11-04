# 딸깍 (DDalKKak) - 건국대 글로컬캠퍼스 공지사항

🌐 **공식 사이트**: [www.ddalkkak.net](https://www.ddalkkak.net) (예정)

건국대학교 충주(글로컬캠퍼스) 각 학과의 공지사항을 한 곳에서 확인할 수 있는 서비스입니다.

## 📁 프로젝트 구조

```
DDalKKak/
├── kku_glocal_all_notices.json    # 크롤링된 데이터
├── backend/
│   ├── app.py                      # Flask API 서버
│   └── requirements.txt            # Python 의존성
└── frontend/
    └── index.html                  # 웹 인터페이스
```

## 🚀 실행 방법

### 💻 로컬 테스트
```bash
./deploy.sh
```
실행 후 http://localhost 에서 확인

### 🌍 AWS EC2 배포
```bash
./deploy-aws.sh
```

### 🔒 SSL 인증서 (선택사항)
```bash
./setup-ssl.sh
```

## 📊 수집 데이터

**6개 학부, 31개 학과**
- 디자인대학 (6개 학과)
- 과학기술대학 (5개 학과) 
- 의과대학 (2개 학과)
- 의료생명대학 (7개 학과)
- 인문사회융합대학 (10개 학과)
- KU자유전공학부 (1개 학부)

## 🔧 API 엔드포인트

- `GET /api/colleges` - 모든 학부 목록
- `GET /api/departments/<college>` - 특정 학부의 학과 목록
- `GET /api/notices/<college>/<department>` - 특정 학과 공지사항
- `GET /api/notice/<college>/<department>/<notice_id>` - 공지사항 상세 정보
- `GET /api/all-notices` - 모든 공지사항
- `GET /api/search?q=검색어` - 공지사항 검색

## 🚀 서버 배포 가이드

### 💻 로컬 테스트
```bash
./deploy.sh
```
실행 후 http://localhost 에서 확인

### 🌍 Linux 서버 배포

#### 1단계: 서버 준비
```bash
# 서버에 접속 후
wget https://raw.githubusercontent.com/J02H/DDalKKak/main/server-setup.sh
chmod +x server-setup.sh
./server-setup.sh
```

#### 2단계: 프로젝트 배포
```bash
# 터미널 재시작 또는
newgrp docker

# 프로젝트 클론
git clone https://github.com/J02H/DDalKKak.git
cd DDalKKak

# 배포 실행
./deploy.sh
```

#### 3단계: 도메인 연결
```bash
# 도메인 설정 (ddalkkak.net)
./setup-ssl.sh ddalkkak.net
```

**AWS Route 53 도메인 설정:**
1. AWS Route 53에서 `ddalkkak.net` 도메인 구매
2. Hosted Zone에서 A 레코드 추가:
   - `ddalkkak.net` → 서버 IP
   - `www.ddalkkak.net` → 서버 IP
3. DNS 전파 확인: `./check-dns.sh`
4. 도메인 배포: `./deploy-domain.sh`

### 🔧 유지보수 명령어

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart

# 서비스 중지
docker-compose down

# 데이터 업데이트
python3 kku_glocal_crawler.py
docker-compose restart backend
```

## ✨ 주요 기능

- 🔍 **실시간 검색**: 공지사항 제목 검색
- 📱 **반응형 디자인**: 모바일/데스크톱 지원
- 🏫 **학부별 분류**: 체계적인 데이터 구조
- 📊 **통계 정보**: 학과별 공지사항 개수 표시
- 📄 **상세 페이지**: 공지사항 클릭 시 상세 정보 제공
- 🎯 **키워드 요약**: 공지사항 내용을 키워드 기반으로 요약
- 📤 **공유 기능**: 공지사항 정보 공유
- 🐳 **Docker 배포**: 간편한 서버 배포

## 🌐 배포 환경

- **프론트엔드**: Nginx (정적 파일 서빙)
- **백엔드**: Flask (Python)
- **컨테이너**: Docker & Docker Compose
- **프록시**: Nginx (API 프록시)
