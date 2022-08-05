# Example Project For Django-Ninja
## Introduce
> 이 프로젝트는 django 와 django-ninja를 활용하여 간단한 진료 예약 API를 구현한 예제 프로젝트 입니다. 

## Dependencies
- python@3.9
- dependency managing by `poetry` [🔗](https://python-poetry.org/)
- web framework by `django` [🔗](https://www.djangoproject.com/)
- api build by `django-ninja` [🔗](https://django-ninja.rest-framework.com/)
- containing database by `docker` [🔗](https://www.docker.com/)

## How to run
1. run database container
```shell
sh mysql/run.sh
```
2. runserver with database migrate
```shell
poetry shell
poetry update
sh run.sh
```
## Test
```shell
python manage.py test
```

## Product Structure
```
├── README.md
├── account                             // 계정 & 인증 관련 app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py                       // 모델
│   ├── schemas.py                      // pydantic schema
│   ├── tests.py                        // test
│   └── views.py                        // api endpoints
├── config                              // django project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── utils                           // 공용 유틸 함수
│   │   ├── __init__.py                  
│   │   ├── permissions.py              // 인증 관련 유틸 함수
│   │   ├── schemas.py                  // 공통 pydantic schemas
│   │   └── utils.py                    // 각종 유틸 함수
│   └── wsgi.py
├── healthcare                          // 진료 예약 app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── management                      // json 데이터를 db에 입력하기 위한 커스텀 커맨드
│   │   └── commands
│   │       └── migrate-base-data.py
│   ├── mappers                         // entity model -> pydantic schema 맵퍼 함수
│   │   ├── __init__.py
│   │   ├── diagnosis_request.py
│   │   └── doctor.py
│   ├── migrations
│   ├── models.py                       // 모델
│   ├── schemas                         // pydantic schema 
│   │   ├── __init__.py
│   │   ├── diagnosis_request.py
│   │   └── doctor.py
│   ├── tests                           // test
│   │   ├── __init__.py
│   │   ├── doctor_test_data.py
│   │   ├── test_diagnosis_request.py
│   │   └── test_doctor.py
│   ├── utils.py                        // 진료 예약 app 전용 유틸함수들
│   └── views                           // api endpoints
│       ├── __init__.py
│       ├── diagnosis_request.py
│       └── doctor.py
├── manage.py
├── mysql                               // mysql container
│   └── run.sh
├── poetry.lock
├── pyproject.toml
└── run.sh                              // run server with data migration
```
## Auth
1. 회원가입시 입력한 id와 pw로 로그인 API`(api/auth/login)` 호출
2. 응답받은 토큰을 이용 하여 인증이 필요한 API 접근시 헤더에 `{"Authorization": "Bearer {로그인시 받은 토큰값}"}`를 추가하여 요청
3. 각 API에서 요구하는 회원 role `(ex. 진료 요청시 로그인된 회원은 "PATIENT"여야함 // 의사 등록시 로그인된 회원은 "DOCTOR"여야함)` 이어야 정상적으로 호출 가능
4. Swagger 사용시 우측 상단 "Authorize"에 토큰 입력하면 됨 (자물쇠가 잠기면 성공!)
<img width="1653" alt="image" src="https://user-images.githubusercontent.com/58629967/182991763-bb1cf3e7-aa35-4b5d-9301-79dc396d7972.png">
5. HTTP 요청시 인증 예시

```
curl -X 'POST' \
  'http://127.0.0.1:8000/api/diagnosis-request/request' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOi@@@@@@@@@@@.#################.$$$$$$$$$$$$$$$$$$$$$$$$$' \
  -H 'Content-Type: application/json' \
  -d '{
  "doctor_id": 55,
  "request_at": "2022-01-15T09:00:00Z"
}
```

## API Doc with Swagger
API 명세는 Swagger를 통해 관리합니다. \
서버 실행 후 `http://127.0.0.1:8000/api/docs` 로 접근하면 각 API 엔드포인트에 대한 상세 명세를 확인할 수 있습니다.
![image](https://user-images.githubusercontent.com/58629967/183001398-971e2a3c-6b56-4f89-bbf9-59a5aacccb60.png)
