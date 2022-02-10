on / off 가 있는 구성요소의 반복 on / off 를 통해 연속 눌림을 감지할 수 있는 통합구성요소 입니다.

---

## - 설치 방법

###

수동설치

- 소스코드를 다운로드 받은 후 HA 내부의 custom_components 경로에 extend_switch 폴더를 넣어주고 재시작


HACS

- HACS 의 custom repository에 https://github.com/oukene/extend_switch 주소를 integration 으로 추가 후 설치



설치 후 통합구성요소 추가하기에서 extend switch 검색 하여 설치한 후 구성 옵션 변경을 통해서 추가 가능합니다. 

추가 한 후 다시 읽어오기 필수!


연속 누름 최대 횟수 이상 눌려지게 되면 최대 횟수로 고정입니다.

ex) 최대 횟수가 2로 되어있으면 10번을 눌러도 2로 실행


![settings.jpg](https://github.com/oukene/extend_switch/blob/main/images/settings.jpg?raw=true)
![settings2.jpg](https://github.com/oukene/extend_switch/blob/main/images/settings2.jpg?raw=true)



<br><br>
---
History
<br>
v1.0.0 - 2022.02.10 - 최초 작성<br>
v1.1.0 - 2022.02.10 - 연속 눌림 최대 횟수 추가<br>

---
<br><br><br>

