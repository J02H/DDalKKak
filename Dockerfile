FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY backend/ ./backend/
COPY kku_glocal_all_notices.json .
COPY notices_by_college/ ./notices_by_college/

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행
CMD ["python", "backend/app.py"]