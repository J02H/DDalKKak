# AWS EC2 서버 설정 가이드

## 1단계: AWS 계정 생성 및 EC2 인스턴스 생성

### 1.1 AWS 계정 생성
1. [AWS 콘솔](https://aws.amazon.com/ko/) 접속
2. "AWS 계정 생성" 클릭
3. 이메일, 비밀번호 입력
4. 신용카드 등록 (12개월 무료)

### 1.2 EC2 인스턴스 생성
1. **AWS 콘솔 로그인** → **EC2** 검색
2. **인스턴스 시작** 클릭
3. **설정값**:
   - **이름**: `DDalKKak-Server`
   - **AMI**: `Ubuntu Server 22.04 LTS (HVM)`
   - **인스턴스 유형**: `t2.micro` (무료)
   - **키 페어**: 새로 생성 → `DDalKKak-key.pem` 다운로드
   - **보안 그룹**: 새로 생성
     - SSH (22): 내 IP
     - HTTP (80): 0.0.0.0/0
     - HTTPS (443): 0.0.0.0/0

## 2단계: SSH 접속 설정

### 2.1 키 파일 권한 설정
```bash
# 다운로드한 키 파일 권한 변경
chmod 400 ~/Downloads/DDalKKak-key.pem
```

### 2.2 SSH 접속
```bash
# EC2 인스턴스의 퍼블릭 IP 확인 후
ssh -i ~/Downloads/DDalKKak-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3단계: 서버 배포

### 3.1 로컬에서 배포 실행
```bash
cd /Users/j02h/Desktop/DDalKKak
./full-deploy.sh
```

### 3.2 옵션 선택
- **옵션 2** 선택 (서버 배포)
- **서버 IP**: EC2 퍼블릭 IP 입력
- **사용자명**: `ubuntu` 입력

## 4단계: 접속 확인
- 웹사이트: `http://YOUR_EC2_PUBLIC_IP`

## 💡 주의사항
- EC2 인스턴스 중지하면 퍼블릭 IP 변경됨
- 고정 IP 필요시 Elastic IP 할당
- 12개월 후 요금 발생 (t2.micro 기준 월 $8-10)

## 🔒 SSL 설정 (선택사항)
도메인 있을 경우:
```bash
./setup-ssl.sh
```