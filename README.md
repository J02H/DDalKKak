# DDalKKak

Next.js(backend)
Devcontainer 기반으로 개발 환경 구성됨.

## 폴더 구조
- web -> next.js 프로젝트 + react native for web
- mobile(아직 추가안됨) expo + react native 프로젝트
- pacakges -> web + mobile 공통 UI 컴포넌트, 공유로직
    - api -> api 관련 로직 (모바일 및 웹에서 공유사용하기위해 api 따로 개발)
    - utils -> 공통 유틸로직
    - components -> gluestack ui 및 개인 커스텀 컴포넌트들 (버튼, 셀렉트박스 등등 자세한건 gluestack ui 참고)
