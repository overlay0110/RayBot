# RayBot

RayBot은 지메일, 깃허브, 애플계정 등 각각 16자리의 안전한 비밀번호를 생성해서 관리하기 위해 만듬 todo, 크롤링, 번역은 덤으로 추가함

# Environment
|제목|상세|
|------|---|
|Python|3.9.2|
|python-telegram-bot|13.14|
|googletrans|4.0.0rc1|
|beautifulsoup4|4.11.2|

# Work
* 텔레그램 봇 연동
  * python-telegram-bot를 사용해서 연동함

* 서버에 POST 요청하고 response 받음

* 안전한 비밀번호 생성 및 찾기

* 할일 등록,삭제,보기

* 최신영화, 뉴스 등 크롤링
  * beautifulsoup4를 사용

* 구글 번역기 연동
  * googletrans를 사용
