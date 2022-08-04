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
1. database setting
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
