# 팝콘 긱 (Popcorn Geek)

## 프로젝트 개요
팝콘 긱은 사용자가 영화를 리뷰하고 토론할 수 있는 웹 플랫폼입니다. OTT 플랫폼의 증가로 영화를 쉽게 접할 수 있게 되었으며, 이 플랫폼은 사용자들이 영화를 보고 남기는 생각을 기록하고 공유할 수 있는 공간을 제공합니다.

### 목표
OTT 플랫폼의 성장과 영화가 현대 문화에서 차지하는 비중이 커짐에 따라, 팝콘 긱은 사용자가 본 영화에 대한 감정을 기록하고 다른 사람들과 의견을 나눌 수 있는 공간을 제공합니다.

## 팀 소개
- **팀명**: ByteBite
- **팀원**:
  - 박연재 (팀장 - 프론트엔드/백엔드)
  - 서재일 (부팀장 - 프론트엔드/백엔드)
  - 정성원 (아이디어 뱅크 - 프론트엔드/백엔드)
  - 윤찬민 (배포 - 프론트엔드/백엔드)
 
## 팀 소개 2
| Member      | Role                  |
|-------------|-----------------------|
| 박연재 | 팀장 - 프론트엔드/백엔드 |
| 서재일    | 부팀장 - 프론트엔드/백엔드 |
| 정성원| 아이디어 뱅크 - 프론트엔드/백엔드 |
| 윤찬민| 배포 - 프론트엔드/백엔드 |


## 프로젝트 일정
- **초기 기획**: 2023년 3월 13일
- **MVP 기능 구현**: 2024년 9월 27일
- **유저 테스트 & 오류 수정**: 2024년 10월 3일 ~ 2024년 10월 18일
- **최종 제출**: 2024년 10월 23일

## 주요 기능
1. **영화 점수 매기기**: 사용자가 0.1점에서 5.0점 사이의 점수를 줄 수 있습니다.
2. **리뷰 시스템**: 사용자가 리뷰를 남길 수 있으며, 긍정 또는 부정 리뷰로 표시됩니다.
3. **유저 프로필**: 사용자가 리뷰를 관리하고 팔로워 및 영화 선호도를 관리할 수 있습니다.
4. **소셜 로그인**: 구글, 카카오, 네이버를 통한 소셜 로그인을 지원합니다.

---

## API 리스트

### 계정 관련 API
- **로그인**: `POST /api/v1/accounts/signin/`  
- **로그아웃**: `POST /api/v1/accounts/signout/`  
- **회원가입**: `POST /api/v1/accounts/`  
- **프로필 페이지**: `GET /api/v1/accounts/<int:user_pk>/`

### 영화 관련 API
- **영화 상세 정보**: `GET /api/v1/movies/<int:movie_pk>/`
- **영화 검색**: `GET /api/v1/movies/search/`
- **영화 점수 수정**: `PUT /api/v1/movies/<int:movie_pk>/score/`
- **보고 싶어요/관심 없어요 표시**: `POST /api/v1/movies/<int:movie_pk>/`

### 리뷰 관련 API
- **리뷰 작성**: `POST /api/v1/reviews/<int:movie_pk>/`
- **리뷰 수정**: `PUT /api/v1/reviews/<int:reviews_pk>/`
- **리뷰 삭제**: `DELETE /api/v1/reviews/<int:pk>/`
- **리뷰 좋아요**: `POST /api/v1/reviews/likes/<int:review_id>/`
- **리뷰 신고**: `POST /api/v1/reviews/report/review/<int:review_id>/`

### 댓글 관련 API
- **댓글 작성**: `POST /api/v1/reviews/<int:reviews_pk>/comments/`
- **댓글 수정**: `PUT /api/v1/reviews/<int:reviews_pk>/comments/<int:pk>/`
- **댓글 삭제**: `DELETE /api/v1/reviews/<int:reviews_pk>/comments/<int:pk>/`
- **댓글 좋아요**: `POST /api/v1/reviews/likes/comment/<int:comment_id>/`
- **댓글 신고**: `POST /api/v1/reviews/report/comment/<int:comment_id>/`

### 상품 관련 API
- **상품 목록 조회**: `GET /api/v1/products/`
- **상품 상세페이지 조회**: `GET /api/v1/products/<int:product_pk>/`
- **상품 결제**: `GET /api/v1/products/payments/`

---

## 문제 해결

### 문제 1: **잘못된 점수 저장**
- **문제**: 사용자가 입력한 점수가 올바르게 저장되지 않음.
- **해결 방법**: 백엔드에서 유효성 검사를 확인하고 점수가 0.1에서 5.0 사이로 제한되었는지 확인하십시오.

### 문제 2: **리뷰 삭제 실패**
- **문제**: 즐겨찾기에 추가된 리뷰가 삭제되지 않음.
- **해결 방법**: 리뷰를 삭제하기 전에 즐겨찾기에서 먼저 제거하십시오.

### 문제 3: **로그인 문제**
- **문제**: 회원가입 후 사용자가 로그인을 할 수 없음.
- **해결 방법**: 이메일 인증이 정상적으로 작동하는지 확인하고 데이터베이스 문제를 점검하십시오.

### 문제 4: **느린 페이지 로딩 속도**
- **문제**: 영화 상세 페이지가 너무 느리게 로딩됨.
- **해결 방법**: 백엔드에서 쿼리를 최적화하고 이미지에 대한 지연 로딩을 추가하십시오.

---

## 스크린샷 및 와이어프레임

### 1. **홈페이지 와이어프레임**
<img src="https://example.com/homepage_wireframe.png" alt="홈페이지 와이어프레임" width="600">

### 2. **영화 상세 페이지**
<img src="https://example.com/movie_detail_wireframe.png" alt="영화 상세 와이어프레임" width="600">

---

## 사용 기술

### 프론트엔드
- **HTML, CSS, JavaScript**
- **Axios**를 사용한 API 요청

### 백엔드
- **Python** & **Django**
- **Django-rest-framework**

### 데이터베이스
- **PostgreSQL**

### 기타 도구
- **AWS EC2** 서버 호스팅
- **Nginx**를 통한 로드 밸런싱
- **Docker**를 사용한 컨테이너화

---

## 버전 관리 및 협업
- **버전 관리**: Git, GitHub에 호스팅.
- **협업 도구**: Notion, Slack.

## 배포
- **배포 환경**: AWS EC2, Docker 및 Gunicorn을 사용한 백엔드 처리.
- **정적 파일 서비스**: AWS S3 및 AWS CloudFront.

---

## 지원 및 피드백
프로젝트 지원 또는 피드백을 제공하려면 [GitHub](https://github.com/duswo3o/BYTEBITE) duswo3o님께 연락 부탁드립니다.

---

