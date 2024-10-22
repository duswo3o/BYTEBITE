# 팝콘 긱 (Popcorn Geek)


### 👉 [POPCORNGEEK](https://popcorngeek.store/)
### 👉 [BYTEBITE SA문서](https://www.notion.so/SA-10c7d4611a6f8042ad00f01ea317b42e)

<br><br>

## 1️⃣ 프로젝트 개요
OTT 사용이 증가하면서 많은 사람들이 영화를 쉽게 소비하게 되었습니다. 
OTT 별로 자체 제작 콘텐츠 등이 증가하며 현대 사회의 빠질 수 없는 문화의 한 축을 담담하고 있습니다.
오랜만에 만난 친구 혹은 처음 보는 사람들과 아이스브레이킹을 위해  관심사를 공유하며 영화에 대한 이야기를 나누는 경우가 많습니다. 
당시에 자신이 본 영화에 대한 감정이나 느낌을 기억하고 기록하고 싶어하는 사람들을 위해 기획하게 되었습니다.

---

<br><br>

## 2️⃣ TEAM BYTEBITE

| 이름  | 역할      | 업무         |
|-----|---------|------------|
| 박연재 | 팀장      | 유저 CRUD, 팔로우, 이메일 인증, 리뷰 긍부정분석, 리뷰/댓글 신고, redis, celery, 계정 관련 커멘드  |
| 서재일 | 부팀장     | DB관리 커맨드, 결제 관련 기능, 검색, 보고싶어요/관심없어요, AI 추천 태깅. Django admin  |
| 정성원 | 아이디어 뱅크 | 스포일러, 팔로잉 리뷰, 비공개 리뷰, 배포,  Docker, CICD  |
| 윤찬민 | 서기      |  리뷰 CRUD, 댓글 CRUD, 소셜로그인, 말투변경, 리뷰/댓글 좋아요, 개인정보처리방침/이용약관 |

<br><br>

## 3️⃣ 프로젝트 일정
| 날짜            | 업무                 |
|---------------|--------------------|
| 09.23 ~ 09.27 | 기획 및 문서작성          |
| 09.27 ~ 10.03 | MVP 기능 구현          |
| 09.27 ~ 10.15 | 배포                 |
| 09.30 ~ 10.15 | 프론트엔드              |
| 10.03 ~ 10.19 | 추가기능 구현 및 프론트엔드 수정 |
| 10.16 ~ 10.18 | 1차 유저테스트           |
| 10.16 ~ 10.20 | 유저테스트 기반 오류수정      |
| 10.21 ~ 10.22 | 2차 유저테스트           |
| 10.21 ~ 10.23 | 발표준비 및 결과보고서 작성    |
| 10.24         | 최종발표               |

<br><br>

---

<br><br>

## 4️⃣ 기능 소개
### 👥 회원
```
- 회원가입, 로그인, 로그아웃, 회원탈퇴 기능을 제공합니다
- 카카오, 구글, 네이버 간편 로그인이 가능합니다.
- 회원정보를 수정할 수 있습니다
- 패스워드를 변경할 수 있습니다
- 다른 유저의 프로필을 볼 수 있습니다
- 다른 유저를 팔로우 할 수 있습니다
```

### 🎬 영화
```
- 메인페이지에서 박스오피스 순위, 평균 평점이 높은 순, 보고싶어요가 많은 영화를 볼 수 있습니다
- 검색 단어와 카테고리(영화, 영화인, 회원)를 기준으로 원하는 데이터를 검색할 수 있습니다
- 회원이 특정 영화에 대해 점수를 줄 수 있습니다. 점수 구간은 0.1~5.0점 입니다.
- 특정 영화의 상세정보를 볼 수 있습니다. 영화의 제목, 장르, 평균 평점, 개봉일, 상영시간, 관람등급, 줄거리 등을 표시합니다
- 특정 영화에 대해 보고싶어요/관심없어요를 등록할 수 있습니다
```


### 📝 리뷰
```
- 특정 영화에 대한 리뷰를 작성할 수 있습니다
- 리뷰 작성시 말투변경 기능을 제공합니다 (조선시대 말투, 평론가 말투, MZ 말투)
- 리뷰에 대한 댓글을 작성할 수 있습니다
- 본인이 작성한 리뷰나 댓글을 수정 및 삭제할 수 있습니다
- 리뷰와 댓글에 좋아요를 남길 수 있습니다. 중복은 불가능하며 다시 좋아요를 누르면 좋아요가 취소됩니다
- 리뷰와 댓글을 신고할 수 있습니다. 스포일러 신고와 부적절한 표현신고가 있으며 중복해서 신고는 불가능합니다
- 리뷰 및 댓글 작성시 스포일러 포함을 선택할 수 있습니다. 스포일러를 포함하면 글이 스포일러 방지 처리가 됩니다
- 나만 볼 수 있는 리뷰를 작성할 수 있습니다
- 팔로우한 사람의 리뷰만 볼 수 있습니다
```

### 🍿제품
```
- 상품의 목록을 사용자에게 보여줍니다. 상품의 목록은 django admin 계정에서 추가할 수 있습니다
- 상품의 정보를 사용자에게 보여줍니다, 구매페이지로 이동할 수 있습니다
- 상품을 선택하고 구매할 수 있습니다. 구매자의 이름과 배송받을 주소를 입력하여 카카오페이로 결제를 진행할 수 있습니다
```

<br><br>
<br><br>

## 5️⃣ 주요 기능 소개
### 🏙️ KMDB API를 사용한 데이터베이스 구성
- MDB의 api는 단순히 영화에 대한 정보를 담고있었기 때문에 박스오피스 순위를 활용할 수 없음
- 영진위의 api를 통해 박스오피스 순위에 대한 정보를 가져온 뒤 기존 데이터베이스와 연결

<br>

### 🤖 AI 태깅
- openai의 api를 사용하여 영화의 제목, 줄거리, 장르를 기반으로 영화에 대한 느낌을 태그로 생성
> Issue
> - 비용문제로 모든 영화에 대해서 적용할 수 없었음
> 
> Solution
> - admin page에서 미리 태그 추가
> - 특정 영화에 대해 분류한 태그를 활용하여 추가

<br>

### 📨 이메일 인증
- 로그인시 이메일 본인인증, 비활성화 계정의 로그인 시도시에 활성화 이메일 전송, 신고 이메일
- Celery를 사용해서 이메일을 비동기적으로 발송

> Celery 사용 이유
> - 사용자 경험 개선: 이메일 발송을 백그라운드에서 처리해 사용자에게 빠른 응답을 제공.
>   - 성능 향상: 이메일 발송으로 인한 서버 부하를 분산하고, 대규모 발송을 효율적으로 처리.
>   - 에러 핸들링 및 재시도: 실패한 작업을 자동으로 재시도해 안정성을 높임.
>   - 백그라운드 작업 처리: 이메일 외 다른 작업들도 비동기적으로 처리 가능.
>   - 확장성: 워커를 추가해 이메일 발송량이 많아져도 효율적으로 처리.
>   - 서버 응답 시간 단축: 서버 응답 시간을 빠르게 유지할 수 있음.
>   
> 브로커로 Redis 사용
> - 빠른 성능: Redis는 메모리 기반 데이터베이스로 매우 빠름. 메시지 전송과 큐 처리 속도가 뛰어나 대량의 작업을 효율적으로 처리할 수 있음.
> - 간단한 설정: Redis는 설정이 간단하고, Celery와의 통합이 쉬움. 별도의 복잡한 설정 없이 빠르게 사용할 수 있음.
> - 신뢰성: Redis는 데이터를 메모리에 저장하고 디스크에 주기적으로 저장하는 방식으로 높은 신뢰성을 제공.
> - 스케일링: Redis는 수평 확장성이 뛰어나며, 다양한 클러스터 구성을 통해 성능을 확장할 수 있습니다.
> - 경량화: Redis는 상대적으로 적은 리소스를 사용하며, 높은 성능을 유지하는 동시에 시스템 자원을 효율적으로 관리함.
> 

<br>

### 🗣️ 리뷰 말투변경
- OPENAI를 통해 사용자가 입력한 리뷰를 스타일에 맞춰 변환해주는 기능을 수행하며, 조선시대, 평론가, MZ세대 스타일로 변경할 수 있습니다.
> 기대효과 
> - 사용자 참여도 증가 : 말투를 다양하게 변경할 수 있는 옵션이 리뷰 작성 자체를 하나의 재미있는 활동으로 만들어, 사용자들이 자발적으로 더 많은 리뷰를 작성할 가능성이 커집니다  또한 읽는 재미를 더해, 다른 사용자들이 리뷰를 읽는 과정에서도 흥미를 느끼게 만듭니다.
>
> 모델 : 4o-mini 선정 이유
> - 보다 성능적으로 우수한 모델이 있었지만 요청 처리 속도가 평균 5초 정도로 필요 이상의 시간이 소요 되었고 비용 또한 mini 모델 보다 10배 이상 발생하였다 그러나 결과의 큰차이가 없었고  mini 모델 사용후 1초 미만의 처리 속도와 사용자 편의성 및 비용 
고려 최종 mini 모델로 선정하게 되었습니다 
> 


<br>

### 💸 결제 서비스
- 결제 검증을 거친 후 사용자에게 확인 메일 전송
> PortOne
> - API 및 SDK를 통해 간편하게 웹사이트나 애플리케이션에 결제 시스템을 연동할 수 있음
> - PG사들과 연동된 결제 처리뿐 아니라, 결제 보안, 결제 내역 관리, 환불 처리 등 다양한 관리 기능을 제공하여 결제 운영을 효율적으로 관리할 수 있음
> 
> 카카오페이
> - 카카오페이는 사용자가 많고 접근성이 뛰어나며, 결제 과정이 간편함
> 

<br>

### 🌤️ 리뷰 긍부정 분석
- 리뷰를 입력하면 사용자가 입력한 리뷰의 내용이 긍정인지 부정인지 판별하는 기능입니다
> Transfomer 사용 이유
> - 문맥 이해: 셀프 어텐션 메커니즘을 통해 문장 내 모든 단어 간의 관계를 파악하여 더 정확한 문맥 이해가 가능함.
> - 양방향 처리: 문장을 양방향으로 처리하여 앞뒤 문맥을 모두 고려할 수 있어, 의미를 더 잘 이해함.
> - 장기 의존성 처리: 먼 거리의 단어들 간의 관계도 효과적으로 파악할 수 있음.
> - 병렬 처리: RNN이나 LSTM과 달리 병렬 처리로 학습 속도가 빠르고 효율적임.
> - 전이 학습 가능: 대규모 데이터로 사전 학습 후, 적은 데이터로도 높은 성능을 발휘할 수 있음.
> 
> 모델 선정
> - ELECTRA는 BERT와 비교하여 훨씬 적은 학습 자원으로도 유사한 성능을 낼 수 있음. 학습 과정에서 모든 토큰을 활용하므로 더 빠르게 학습할 수 있으며, 이는 특히 자원 제한이 있는 환경에서 유리함.<br>
⇒ 자원 제한이 있는 환경과 빠른 학습을 위해 KoELECTRA 모델 사용
> 
> 학습
> - PyTorch는 동적 계산 그래프, GPU 가속, Hugging Face 라이브러리와의 통합, 직관적인 코드 작성 등을 통해 트랜스포머 모델을 효과적이고 유연하게 구현할 수 있는 환경을 제공함. 이러한 이유로 트랜스포머 모델을 PyTorch에서 사용하는 것이 일반적임.
> - 학습설정
>   - 라벨링이 된 30,000개의 데이터를 이용하여 학습 진행 
>   - batch_size=4, epoch=2로 설정
> - 모델 정확도
>   - 89.40%


<br>

### 💬 소셜로그인
- 사용자가 별도의 아이디와 비밀번호를 생성하지 않고, 이미 가입된 소셜 네트워크 서비스( Google, Naver, Kakao 등)의 계정을 사용해 popcorngeek 에 로그인할 수 있도록 하는 인증 방식입니다.
> 소셜 로그인을 선택한 이유
> - 편의성: 사용자 입장에서 별도의 비밀번호 없이 쉽게 로그인할 수 있습니다.
> - 보안성: 비밀번호를 입력하지 않으므로 비밀번호 유출 위험이 줄어듭니다.
> - 소셜 미디어와의 연결성: 소셜 플랫폼에서 제공하는 사용자 정보를 활용할 수 있습니다.
> 
> 주요 인증방식
> - 사용자의 데이터를 안전하게 관리할 수 있는 OAuth 2.0 방식으로 소셜 서버에서 사용자를 인증하고 token 을 받아 사용자의 정보를 우리 서버로 가져옵니다. 추후 웹 모바일 등 다양한 플렛폼 확장성을 위해 JWT을 재 발급하여 사용자 인증을 진행합니다 
>


<br>


### 🛰️ 배포
- 확장성, 비용 효울성, 안정성, 다양한 서비스 통합 기능을 고려하여 **AWS** 사용
> Amazon Route 53
>- 도메인 이름을 효율적으로 관리하고, 글로벌 사용자를 위한 빠르고 신뢰성 높은 접속 제공
>- 트래픽 라우팅 기능으로 애플리케이션 성능 최적화 가능
>- DNS 서버 가용성과 복구 기능 제공
> 
> Amazon CloudFront CDN
>- 글로벌 엣지 네트워크를 통해 빠른 콘텐츠 배포 제공
>- 캐시를 통해 트래픽 부하 분산 및 성능 최적화
>- HTTPS 지원으로 보안 강화
> 
> Amazon Certificate Manager
>- SSL/TLS 인증서를 손쉽게 생성 및 관리하여 보안 강화
>- 자동 갱신 기능으로 인증서 관리 부담 감소
>- HTTPS를 통한 데이터 암호화로 보안 강화
> 
> Amazon S3 Bucket
>- 확장성 있는 스토리지로 무제한 파일 저장 가능
>- 높은 내구성과 가용성으로 데이터 안정성 보장
>- 데이터 백업 및 복구에 용이
>
> Amazon EC2
> - 서버 용량을 유연하게 확장 및 축소 가능
> - 다양한 OS 및 애플리케이션 환경에서 사용 가능
> 
> Docker
> - 개발 및 배포 환경의 일관성을 유지하여 오류 감소
> - 애플리케이션의 이식성과 확장성 제공
> - 리소스 효율성을 극대화하여 서버 비용 절감
> 
> GitHub Actions (CI/CD)
> - 코드 변경 시 자동으로 빌드와 테스트 실행 가능
> - CI/CD 파이프라인을 통해 배포 속도 향상 및 오류 감소



<br>


### 🎓 관련법률
- 관련법률 (개인정보 처리방침)
> 서비스를 운영하며 이용자의 개인정보의 관한 법률조치로 popcorngeek 서비스에 맞는 개인정보 처리방침및 이용약관을 만들어 
푸터에 게시함에 따라 이용자는 필요시 법률 및 약관 확인을 가능하게 하였습니다 

<br><br>

---

<br><br>

## 6️⃣ API 리스트

👉 [popcorngeek API 명세서](https://www.notion.so/fff7d4611a6f815f8d13cfe71de9dd3d?v=fff7d4611a6f819ea9a4000c586cccbc&pvs=4)

### 계정 관련 API

- **회원가입**: `POST` `/api/v1/accounts/`  
- **회원정보 수정**: `PUT` `/api/v1/accounts/`
- **회원탈퇴**: `DELETE` `/api/v1/accounts/`
- **비밀번호 수정**: `PUT` `/api/v1/accounts/password`
- **로그인**: `POST` `/api/v1/accounts/signin/`  
- **로그아웃**: `POST` `/api/v1/accounts/signout/`  
- **프로필 페이지**: `GET` `/api/v1/accounts/<str:nickname>/`
- **팔로우**: `POST` `/api/v1/accounts/<str:nickname>/follow`
- **토큰 재발급**: `POST` `api/v1/accounts/token/refresh/`
- **이메일 인증 확인**: `POST` `api/v1/accounts/<uidb64>/<str:token>/`
- **소셜 로그인**: `POST` `api/v1/accounts/social/login/<str:provider>/`
- **소셜 콜백**: `POST` `api/v1/accounts/social/callback/<str:provider>/`

### 영화 관련 API
- **영화 메인페이지**: `GET` `/api/v1/movies/`
- **영화 검색**: `GET` `/api/v1/movies/search/`
- **영화 점수 수정**: `PUT` `/api/v1/movies/<int:movie_pk>/score/`
- **영화 상세 정보**: `GET` `/api/v1/movies/<int:movie_pk>/`
- **보고 싶어요/관심 없어요 표시**: `POST` `/api/v1/movies/<int:movie_pk>/`

### 리뷰 관련 API
- **리뷰 작성**: `POST` `/api/v1/reviews/<int:movie_pk>/`
- **리뷰 수정**: `PUT` `/api/v1/reviews/<int:reviews_pk>/`
- **리뷰 삭제**: `DELETE` `/api/v1/reviews/<int:pk>/`
- **리뷰 상세**: `GET` `/api/v1/reviews/<int:pk>/`
- **리뷰 좋아요**: `POST` `/api/v1/reviews/likes/<int:review_id>/`
- **리뷰 신고**: `POST` `/api/v1/reviews/report/review/<int:review_id>/`
- **댓글 작성**: `POST` `/api/v1/reviews/<int:reviews_pk>/comments/`
- **댓글 수정**: `PUT` `/api/v1/reviews/<int:reviews_pk>/comments/<int:pk>/`
- **댓글 삭제**: `DELETE` `/api/v1/reviews/<int:reviews_pk>/comments/<int:pk>/`
- **댓글 상세**: `GET` `api/v1/reviews/<int:review_pk>/comments/<int:pk>/`
- **댓글 좋아요**: `POST` `/api/v1/reviews/likes/comment/<int:comment_id>/`
- **댓글 신고**: `POST` `/api/v1/reviews/report/comment/<int:comment_id>/`
- **리뷰 말투변경**: `POST` `api/v1/transform-review/`
- **리뷰 긍부정분석**: `POST` `api/v1/reviews/sentiment/<int:movie_pk>/`

### 상품 관련 API
- **상품 목록 조회**: `GET` `/api/v1/products/`
- **상품 상세페이지 조회**: `GET` `/api/v1/products/<int:product_pk>/`
- **상품 결제**: `GET` `/api/v1/products/payments/`

<br><br>

---

<br><br>

## 7️⃣ 트러블 슈팅

👉 [popcorngeek 프로젝트 트러블슈팅🤯](https://www.notion.so/10d7d4611a6f807fb44cf42a2ee19412?pvs=4)


<br><br>

## 8️⃣ 사용 기술 및 의사결정

<details>
  <summary>🖥️ 프론트엔드</summary>
    <ul>
      <li>HTML</li>
      <li>CSS</li>
      <li>JavaScript</li>
      <li>Axios</li>
    </ul>
</details>

<details>
  <summary>📀 백엔드</summary>
    <ul>
      <li>Python</li>
      <li>Django</li>
      <li>Django-rest-framework</li>
      <li>
        <details>
        <summary>JWT</summary>
          웹 뿐만 아니라 모바일 등 다양한 플랫폼 강의 인증을 통합할 수 있기 때문에 추후의 확장성을 고려하여 선택
        </details>
      </li>
      <li>
        <details>
        <summary>PostgresSQL</summary>
          SQLite는 소규모 프로젝트에 적합하지만, 대규모 애플리케이션에서는 확장성, 동시성, 보안 등의 한계가 있음.
          복잡한 요구 사항이나 확장성을 고려할 때 다른 데이터베이스로 변경하는 것이 적합하다 판단함.<br>
          Django와의 호환성 문제로 PostgresSQL 사용 결정
        </details>
      </li>
      <li>
        <details>
        <summary>API</summary>
          <ul>
            <li>OPENAI : 사용자가 리뷰 및 댓글 작성 시에 말투 변경 기능을 사용할 수 있도록  OPENAI를 사용한다</li>
            <li>kofic(영화진흥위원회) : 특정 영화의 최근 일주일 간 박스오피스 순위와 작일 기준 박스오피스 순위를 활용할 수 있다</li>
            <li>KMDB(한국영화데이터베이스) : 영화진흥위위원회의 영화 상세정보에는 영화의 줄거리를 제공하지 않아 영화의 줄거리와 기타 영화의 정보를 사용하기 위해 KMDB의 데이터를 사용한다.</li>
            <li>Social(kakao, naver, google) : kakao, naver, google Api 를 사용해 각 서비스의 사용자 정보를 받아 인증을하고 로그인 및 회원가입을 진행한다.</li>
          </ul>
        </details>
      </li>
      <li>
        <details>
        <summary>ML</summary>
          <ul>
            <li>Transformer : KoELECTRA는 한국어 자연어 처리(NLP) 작업에 특화된 ELECTRA 기반의 사전 학습된 언어 모델이다. 특히, KoELECTRA는 한국어 텍스트 분류, 감성 분석, 질의 응답 등 다양한 작업에서 높은 성능을 보여주는 모델로, 전통적인 BERT 모델과 비교해 훈련 속도와 자원 효율성이 더 뛰어납니다. 감성 분석(긍정/부정 분석) 같은 텍스트 분류 작업에 많이 사용된다</li>
            <li>scikit-learn: 모델 학습을 위해 데이터셋 분할, 성능 평가 등에 사용한다. 모델 학습 시, 훈련 데이터와 검증 데이터를 나누어 학습 성능을 평가한다</li>
            <li>PyTorch
              <ul>
                <li>transfomer 라이브러리는 통해 KoELECTRA 모델을 활용할 때, PyTorch는 모델 학습, 딥러닝 모델의 가중치 업데이트, 백워드 전파(backpropagation), 모델 추론 등을 수행</li>
                <li>모델 학습 과정에서 GPU 혹은 CPU를 사용하여 모델의 가중치 업데이트</li>
                <li>모델 평가 과정에서 torch.no_grid()를 사용하여 그래디언트 계산을 비활성화 하고, 평가 모드에서 모델을 실행</li>
                <li>훈련된 모델을 사용하여 새 데이터를 입력으로 받아 긍부정 예측을 할 때, 그래디언트를 비활성화 하여 모델을 사용</li>
              </ul>
            </li>
          </ul>
        </details>
      </li>
      <li>
        <details>
        <summary>Oauth</summary>
          사용자 자격 증명을 안전하게 처리하며, 타사 애플리케이션들(google,kakao,naver)이 자원 소유자의 권한을 대신 받아 제한된 접근 권한을 부여할 수 있는 인증 및 권한 부여 프로토콜
        </details>
      </li>
    </ul>
</details>

<details>
  <summary>⚙️ 버전관리</summary>
    <ul>
      <li>Git</li>
    </ul>
</details>

<details>
  <summary>💬 협업도구</summary>
    <ul>
      <li>GitHub</li>
      <li>Slack</li>
      <li>Notion</li>
      <li>Figma</li>
    </ul>
</details>

<details>
  <summary>📡 배포</summary>
    <ul>
      <li>
        <details>
        <summary>AWS EC2</summary>
          유연한 클라우드 기반의 가상 서버를 제공하며 애플리케이션을 안정적으로 호스팅하고 트래픽 증가에 따라 자원을 쉽게 확장할 수 있다. 
        </details>
      </li>
      <li>
        <details>
        <summary>AWS Route 53</summary>
          클라우드 기반 도메인 이름 시스템(DNS) 웹 서비스로, 인터넷 트래픽을 안정적으로 관리하고 EC2, CloudFront 등 다양한 AWS 리소스와의 연결을 쉽게 설정할 수 있다. 
        </details>
      </li>
      <li>
        <details>
        <summary>AWS CloudFront</summary>
          콘텐츠를 빠르게 제공하는 CDN 서비스로, 프론트 서버를 배포할 수 있다. 
        </details>
      </li>
      <li>
        <details>
        <summary>AWS S3 bucket</summary>
          객체 스토리지 서비스로, 데이터를 안전하게 저장하고 프론트엔드 서버에 필요한 파일들을 제공할 수 있다 
        </details>
      </li>
      <li>
        <details>
        <summary>Docker</summary>
          <ul>
            <li>애플리케이션을 컨테이너화하여 개발 및 운영 환경 간의 일관성을 유지하면서 손쉬운 배포와 관리를 가능하게 한다. </li>
            <li>각각의 서비스(웹 서버, 데이터베이스 등)를 독립된 컨테이너로 운영할 수 있어 시스템 간 의존성을 줄인다.</li>
          </ul>
        </details>
      </li>
      <li>
        <details>
        <summary>Gunicorn</summary>
          파이썬 웹 애플리케이션을 위한 고성능 WSGI 서버로, 다중 프로세스를 활용해 여러 요청을 동시에 처리하여 백엔드 성능을 높인다.
        </details>
      </li>
      <li>
        <details>
        <summary>Nginx</summary>
          리버스 프록시 및 웹 서버로서 클라이언트 요청을 효율적으로 관리하고, 정적 파일을 빠르게 제공하며, 로드 밸런싱을 통해 서버 부하를 분산시켜 성능을 최적화한다.
        </details>
      </li>
    </ul>
</details>

<br><br>

## 9️⃣ 서비스 아키텍쳐
<details>
  <summary>🏗️ 서비스 아키텍쳐</summary>
    <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2Fa9e43394-2674-4fe7-9d51-feba33ccd47d%2Fimage.png?table=block&id=6be40bb0-915b-478b-a16d-7f282566ef03&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=2000&userId=&cache=v2" alt="pocorngeek 서비스 아키텍쳐" width="600">
</details>
<details>
  <summary>🌊 프로세스 플로우</summary>
    <ul>
      <li>
        <details>
          <summary>Accounts</summary>
            <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2F624f0369-7a6c-4953-9769-d833a0cf8d7a%2Fimage.png?table=block&id=acc118c1-97bb-4225-befb-48ec0c686b5c&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=1150&userId=&cache=v2" alt="accounts 프로세스 플로우" width="600">
        </details>
      </li>
      <li>
        <details>
          <summary>MVP</summary>
            <ul>
              <li>
                <details>
                  <summary>Movie</summary>
                    <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2F125a3bf4-ebdd-47dd-8849-1dafdd8472f0%2Fimage.png?table=block&id=a5056d10-26de-4c9f-9e16-a35f72374384&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=1250&userId=&cache=v2" alt="movie 프로새스 플로우" width="600">
                </details>
              </li>
              <li>
                <details>
                  <summary>Review</summary>
                    <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2F0482706a-99b3-40ad-aad5-476f87e56c7c%2Fimage.png?table=block&id=ea0e7ea2-fca8-4c53-a60d-372f9a1df9f0&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=1250&userId=&cache=v2" alt="review 프로새스 플로우" width="600">
                </details>
              </li>
              <li>
                <details>
                  <summary>Comment</summary>
                    <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2F0b60b37f-e006-402f-871a-2b58ff4242ba%2Fimage.png?table=block&id=809f416c-83a9-44c9-8e82-b14a4489c9aa&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=1340&userId=&cache=v2" alt="comment 프로새스 플로우" width="600">
                </details>
              </li>
            </ul>
        </details>
      </li>
      <li>
        <details>
          <summary>Products</summary>
            <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2Faef9dde3-693e-4d31-a47e-07577efd2f91%2Fimage.png?table=block&id=5eacfb22-27bb-43e4-8eef-ddd1492b9037&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=2000&userId=&cache=v2" alt="accounts 프로세스 플로우" width="600">
        </details>
      </li>
    </ul>
</details>
<details>
  <summary>🖼️ 와이어프레임</summary>
    <img src="https://teamsparta.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F83c75a39-3aba-4ba4-a792-7aefe4b07895%2F8b4d0f85-e083-4408-a28f-f05aa8976f91%2Fimage.png?table=block&id=c64029fb-bd2a-4eea-a321-196a1874309b&spaceId=83c75a39-3aba-4ba4-a792-7aefe4b07895&width=2000&userId=&cache=v2" alt="pocorngeek 와이어프레임" width="600">
</details>
<details>
  <summary>🧩 ERD</summary>
    <img src="https://file.notion.so/f/f/c2dcaa6a-ff06-4818-8972-a7d3e38f3c6b/5956955b-ee72-419f-8c87-516e50e83ae4/image.png?table=block&id=871d04fd-5b59-4550-9100-91487d95c2a7&spaceId=c2dcaa6a-ff06-4818-8972-a7d3e38f3c6b&expirationTimestamp=1729677600000&signature=OtCCx7NnHZ9185hViv6VeJq7rxg8wmcYuNMQHLSEyAE&downloadName=image.png" alt="pocorngeek ERD" width="600">
</details>

<br><br>

## 🔟 프로젝트 파일 구조

```
📦 
├─ .gitattributes
├─ .github
│  └─ workflows
│     ├─ django_cd.yml
│     └─ django_ci.yml
├─ .gitignore
├─ README.md
├─ accounts
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ management
│  │  └─ commands
│  │     ├─ create_bot.py
│  │     └─ delete_user.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_user_followings.py
│  │  ├─ 0003_user_deactivate_time.py
│  │  ├─ 0004_alter_user_deactivate_time.py
│  │  ├─ 0005_alter_user_deactivate_time.py
│  │  ├─ 0006_alter_user_deactivate_time.py
│  │  ├─ 0006_user_admonition_alter_user_deactivate_time.py
│  │  ├─ 0007_alter_user_deactivate_time.py
│  │  ├─ 0007_user_is_suspended_user_suspended_time_and_more.py
│  │  ├─ 0008_alter_user_deactivate_time.py
│  │  ├─ 0008_merge_20241009_0328.py
│  │  ├─ 0009_alter_user_deactivate_time.py
│  │  ├─ 0010_alter_user_deactivate_time.py
│  │  ├─ 0010_merge_20241010_1221.py
│  │  ├─ 0011_alter_user_deactivate_time.py
│  │  ├─ 0012_merge_20241012_1958.py
│  │  ├─ 0013_alter_user_deactivate_time.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ tasks.py
│  ├─ templates
│  │  └─ accounts
│  │     └─ account_active_email.html
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ docker-compose.yml
├─ front
│  ├─ BYTEBITE.png
│  ├─ accounts
│  │  ├─ accounts.js
│  │  ├─ password.html
│  │  ├─ payment.js
│  │  ├─ privacy.html
│  │  ├─ profile.html
│  │  ├─ service.html
│  │  ├─ signin.html
│  │  ├─ signup.html
│  │  ├─ style.css
│  │  ├─ updateprofile.html
│  │  └─ withdraw.html
│  ├─ movies
│  │  ├─ details.html
│  │  ├─ mainpage.html
│  │  ├─ movies.js
│  │  ├─ search.css
│  │  └─ search.html
│  ├─ products
│  │  ├─ basket.css
│  │  ├─ basket.html
│  │  ├─ basket.js
│  │  ├─ details.css
│  │  ├─ details.html
│  │  ├─ details.js
│  │  ├─ payment.css
│  │  ├─ products.css
│  │  ├─ products.html
│  │  └─ products.js
│  └─ style.css
├─ manage.py
├─ movies
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ management
│  │  └─ commands
│  │     ├─ dailydb.py
│  │     ├─ initialdb.py
│  │     └─ tagging.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_staff_alter_movie_title.py
│  │  ├─ 0003_movie_staffs_alter_genre_name_alter_staff_name_cd_and_more.py
│  │  ├─ 0004_rename_avg_rating_movie_rating.py
│  │  ├─ 0005_remove_movie_rating_rating.py
│  │  ├─ 0006_ranking_movie_pk.py
│  │  ├─ 0007_alter_ranking_movie_pk.py
│  │  ├─ 0008_movie_prodyear.py
│  │  ├─ 0009_rename_prodyear_movie_prodyear.py
│  │  ├─ 0010_alter_ranking_movie_pk.py
│  │  ├─ 0011_movie_release_date.py
│  │  ├─ 0012_alter_ranking_movie_pk.py
│  │  ├─ 0013_remove_movie_prodyear_movie_poster.py
│  │  ├─ 0014_alter_ranking_movie_pk.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ popcorngeek
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ celery.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ products
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_purchasedproduct_rename_title_product_name.py
│  │  ├─ 0003_purchasedproduct_address_purchasedproduct_address2_and_more.py
│  │  ├─ 0004_rename_amount_purchasedproduct_price_and_more.py
│  │  ├─ 0005_product_consumer.py
│  │  ├─ 0006_alter_product_consumer.py
│  │  ├─ 0007_purchasedproduct_quantity.py
│  │  ├─ 0008_alter_purchasedproduct_merchant_uid.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ tasks.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ requirements.txt
├─ reviews
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ management
│  │  └─ commands
│  │     ├─ create_reviews.py
│  │     └─ unsuspend_user.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_remove_comments_updated_at_alter_comments_author.py
│  │  ├─ 0003_comments_updated_at_alter_comments_author.py
│  │  ├─ 0004_rename_comments_comment_rename_reviews_review.py
│  │  ├─ 0005_remove_review_updated_at_review_movie_and_more.py
│  │  ├─ 0006_like.py
│  │  ├─ 0007_remove_like_created_at.py
│  │  ├─ 0008_alter_like_comment_alter_like_review_alter_like_user.py
│  │  ├─ 0009_report.py
│  │  ├─ 0010_review_is_spoiler.py
│  │  ├─ 0011_comment_is_spoiler.py
│  │  ├─ 0012_review_is_positive.py
│  │  ├─ 0013_report_report_type.py
│  │  ├─ 0014_review_followers_only_review_private.py
│  │  ├─ 0015_remove_review_followers_only.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ permissions.py
│  ├─ sentiment_analysis.py
│  ├─ sentiment_analysis_model
│  │  ├─ config.json
│  │  ├─ model.safetensors
│  │  ├─ special_tokens_map.json
│  │  ├─ tokenizer.json
│  │  ├─ tokenizer_config.json
│  │  ├─ training_args.bin
│  │  └─ vocab.txt
│  ├─ serializers.py
│  ├─ tasks.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
└─ static
   ├─ admin
   │  ├─ css
   │  ├─ img
   │  └─ js
   ├─ images
   ├─ pdf
   │  └─ 개인정보처리방침.pdf
   └─ rest_framework
      ├─ css
      ├─ docs
      ├─ fonts
      ├─ img
      └─ js
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)



---
## 지원 및 피드백
프로젝트 지원 또는 피드백을 제공하려면 [GitHub](https://github.com/duswo3o/BYTEBITE) duswo3o님께 연락 부탁드립니다.

---

