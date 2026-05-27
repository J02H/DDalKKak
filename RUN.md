# DDalKKak 실행 가이드

## 로컬에서 한 번에 실행

```bash
npm install          # 루트 devDependency(concurrently) 설치
npm run install:all  # backend, frontend 의존성 설치
npm run dev          # backend + frontend 동시 실행
```

## 개별 실행

### backend (Next.js)

```bash
cd backend
npm install
npm run dev
```

### frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

## 접속 주소

| 서비스 | 주소 |
|---|---|
| frontend | http://localhost:5173 |
| backend | http://localhost:3000 |
| health check | http://localhost:3000/api/health |

health check 응답 예시:
```json
{
  "status": "ok",
  "message": "DDalKKak backend is running"
}
```

---

## 배포 가이드

> 지금 당장 커스텀 도메인을 구매할 필요 없음.  
> Vercel / Render / Netlify / Railway 등이 제공하는 기본 도메인으로 먼저 배포.

### 추천 배포 구조

| 서비스 | 플랫폼 | 기본 도메인 예시 |
|---|---|---|
| frontend | Vercel 또는 Netlify | `https://ddalkkak.vercel.app` |
| backend | Vercel 또는 Render | `https://ddalkkak-api.onrender.com` |

> Next.js backend는 Vercel 배포가 가장 간단함.  
> React/Vite frontend는 Vercel 또는 Netlify 모두 가능.

### 배포 시 설정해야 할 환경변수

**frontend** (Vercel/Netlify 대시보드에서 설정):

```
VITE_API_BASE_URL=https://배포된-backend-주소
```

예시:
```
VITE_API_BASE_URL=https://ddalkkak-api.onrender.com
```

**backend** (현재는 없음. DB/인증 추가 시 설정):
```
# DATABASE_URL=...
```

### CORS 주의사항

로컬 개발에서는 Vite proxy를 사용하므로 CORS 문제 없음.

배포 환경에서 frontend와 backend 도메인이 다를 경우, backend API에서 CORS를 허용해야 함.

초기 테스트 (임시):
```ts
// backend/app/api/health/route.ts
export async function GET() {
  return Response.json(
    { status: "ok", message: "DDalKKak backend is running" },
    { headers: { "Access-Control-Allow-Origin": "*" } }
  );
}
```

운영 환경 (보안 강화):
```ts
{ headers: { "Access-Control-Allow-Origin": "https://배포된-frontend-주소" } }
```

### 커스텀 도메인이 필요한 시점

- 배포가 먼저 성공한 뒤
- 기능이 정상 동작하고
- 프로젝트 이름과 API 구조가 어느 정도 확정된 뒤

그때 커스텀 도메인을 구매해도 전혀 늦지 않음.

---

## 검증 체크리스트

### 로컬

- [ ] 루트에서 `npm install` 성공
- [ ] 루트에서 `npm run install:all` 성공
- [ ] 루트에서 `npm run dev` 실행 시 backend + frontend 동시 시작
- [ ] `http://localhost:3000` — backend 응답 확인
- [ ] `http://localhost:3000/api/health` — JSON 응답 확인
- [ ] `http://localhost:5173` — frontend 화면에서 **Backend connected** 표시

### 배포 준비

- [ ] `VITE_API_BASE_URL` 환경변수로 backend 주소 교체 가능
- [ ] 코드에 `localhost` 하드코딩 없음
- [ ] RUN.md에 배포 환경변수 설정 방법 기재됨

---

## TODO (나중에 할 것)

- [ ] 실제 API 기능 추가 (backend)
- [ ] DB 연결 (Supabase, PlanetScale 등)
- [ ] 인증 추가 (NextAuth 등)
- [ ] 배포 후 CORS origin 명확히 제한
- [ ] 커스텀 도메인 연결
- [ ] CI/CD 설정 (GitHub Actions 등)
