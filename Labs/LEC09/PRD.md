

# [PRD] 소닉 애니메이션 뷰어 (Sonic Animation Viewer)

## 1. 프로젝트 개요

- **문서명**: PRD.md
- **구현 파일**: `sonic_animation_viewer.py` (단일 파이썬 파일)
- **사용 리소스**: `sonic-sprite.png` (단일 스프라이트 시트, 프로젝트 폴더의 실제 파일명)
- **개발 환경 / 라이브러리**: Python 3.x / `pico2d`
- **캔버스 크기**: 1200 x 600 픽셀
- **목표**: 스프라이트 시트에 포함된 소닉의 모든 동작을 순차 탐색하여, 지정된 반복 횟수(5회)와 휴식 시간(1초)을 두고 무한 반복 재생하는 뷰어 제작

---

## 2. 세부 요구사항

### 2.1 기능적 요구사항

1. **전체 동작 순회**: 스프라이트 시트에 정의된 모든 모션을 누락 없이 차례대로 재생한다.
2. **반복 및 휴식 규칙**:
   - 한 동작당 5회 풀 사이클(5회 완독) 재생
   - 5회 완독 직후 1.0초 대기(정지 상태 유지)
   - 1초 경과 후 다음 동작의 첫 프레임부터 재생 시작
   - 마지막 동작이 끝나면 첫 번째 동작으로 돌아가 무한 루프 수행
3. **화면 시인성 개선**:
   - 스프라이트를 기본 크기의 4배(`SCALE = 4`)로 확대하여 렌더링한다. 프레임이 캔버스 안에 들어오지 않으면 캔버스 안에 온전히 표시되는 가장 큰 배율을 사용한다.
   - 모든 동작은 시작할 때 캐릭터 위치를 캔버스 중앙 `(600, 300)`으로 초기화하고 오른쪽 방향으로 출발한다.
   - 1200 x 600 캔버스에서 캐릭터와 배경의 대비가 충분하도록 배경색을 설정한다.
4. **이동 애니메이션**:
   - 프레임 변화와 화면 위치 변화를 실제 경과 시간 기준으로 함께 진행한다.
   - `idle`과 `action_10`은 제자리 동작이며, 모든 동작은 시작 시 중앙에서 출발한다.
   - `walk`, `run`, `skid_push`, `action_06`~`action_09`는 각 동작의 속도로 수평 이동한다. 동작별 속도는 애니메이션 데이터에 기록한다.
   - 수평 이동은 캐릭터의 확대된 프레임 전체가 캔버스 안에 머물도록 한다. 오른쪽 경계에 닿으면 왼쪽 경계에서, 왼쪽 경계에 닿으면 오른쪽 경계에서 같은 방향으로 이어서 이동한다.
   - `jump_roll`은 수평 이동과 동시에 한 사이클 동안 부드러운 포물선형 점프 궤적을 따라 움직이고, 사이클 끝에 시작 높이로 착지한다.
   - 각 동작의 1초 대기 중에는 마지막 프레임과 현재 위치를 유지하며 이동을 멈춘다.
5. **이벤트 제어**:
   - `ESC` 키 입력 또는 창 닫기 버튼(`SDL_QUIT`) 클릭 시 안전하게 캔버스 종료

### 2.2 기술적 제약사항

- 단일 스크립트 파일(`sonic_animation_viewer.py`) 원칙 준수
- 캔버스 크기는 `1200 x 600` 픽셀로 고정
- 스프라이트 시트의 10개 동작, 총 76프레임을 아래 목록과 같은 순서로 처리
- 잦은 커밋과 단계별 검증을 위해 최소 20단계 이상의 세분화된 단계로 점진 개발

---

## 3. 핵심 아키텍처 및 데이터 규격

### 3.1 좌표계 주의사항 (`pico2d`)

- `pico2d`의 `clip_draw(left, bottom, width, height, x, y, w, h)`는 **좌하단(Bottom-Left)**이 원점 `(0, 0)`입니다.
- 일반 이미지 편집기(좌상단 기준)의 좌표를 쓸 경우 변환 필요:
  $$
  \text{bottom} = \text{Image\_Height} - \text{Top} - \text{Height}
  $$

### 3.2 애니메이션 데이터 구조

```python
# 동작 정의 리스트 템플릿
# 아래 프레임 좌표는 형식 설명용 예시이며, 실제 스프라이트 시트 좌표로 교체한다.
ANIMATIONS = [
    {
        "name": "idle",
        "frames": [
            # (left, bottom, width, height)
            (0, 400, 40, 50),
            (40, 400, 40, 50),
            (80, 400, 40, 50),
        ],
        "fps": 10,
        "movement": "stationary",  # stationary, horizontal, jump
        "speed": 0,
        "jump_height": 0
    },
    # 추가 동작들...
]
```

각 `frames` 좌표는 PNG의 투명 여백을 제외한 실제 프레임 경계이며, `clip_draw`의 좌하단 좌표계로 저장한다. 애니메이션은 매 프레임 10 FPS로 재생한다. 각 동작 데이터에는 이름, 프레임 좌표, FPS, 이동 유형, 수평 이동 속도, 점프 최고 높이를 기록한다. 정지 그림·제목·크레딧은 동작에 포함하지 않는다.

| 순서 | 동작 이름 | 프레임 수 | 이동 유형 | 속도 / 점프 높이 |
|---:|---|---:|---|---:|
| 1 | idle | 11 | 제자리 | 0 |
| 2 | walk | 12 | 수평 | 100 px/s |
| 3 | run | 6 | 수평 | 220 px/s |
| 4 | jump_roll | 9 | 수평 + 점프 | 140 px/s, 높이 120 px |
| 5 | skid_push | 6 | 수평 | 80 px/s |
| 6 | action_06 | 6 | 수평 | 140 px/s |
| 7 | action_07 | 6 | 수평 | 180 px/s |
| 8 | action_08 | 8 | 수평 | 100 px/s |
| 9 | action_09 | 8 | 수평 | 120 px/s |
| 10 | action_10 | 4 | 제자리 포즈 | 0 |

`horizontal` 동작은 프레임 박스의 최대 너비를 기준으로 경계를 계산해 반대편 경계에서 같은 방향으로 이어서 이동한다. `jump` 동작은 사이클 경과 비율 `p`에 대해 `y = baseline + jump_height * sin(πp)` 궤적을 사용한다. 모든 동작은 시작할 때 중심 좌표 `(600, 300)`와 오른쪽 방향으로 초기화한다. 1초 대기 중에는 위치 상태를 갱신하지 않는다.

애니메이션 재생 시각과 위치 갱신 시각은 실제 경과 시간으로 각각 계산한다. 화면 갱신은 초당 약 60회 수행하고, 프레임은 동작별 10 FPS에 맞춰 변경한다.

### 3.3 완료 기준

- 캔버스가 정확히 `1200 x 600` 픽셀로 열린다.
- 위 동작 목록에 등록된 모든 동작이 기재된 순서대로 빠짐없이 재생된다.
- 각 동작은 한 프레임 묶음을 처음부터 끝까지 재생하는 것을 1회로 하여 정확히 5회 재생된다.
- 5회 재생 직후 마지막 프레임을 유지한 채 1.0초 대기한 다음, 다음 동작의 첫 프레임을 재생한다.
- 마지막 동작 뒤에는 첫 번째 동작부터 같은 순서를 무한 반복한다.
- 모든 동작은 시작할 때 `(600, 300)`에서 오른쪽 방향으로 출발한다. 수평 이동 프레임 전체가 캔버스 안에 머물며, 한쪽 경계에 닿으면 반대쪽에서 같은 방향으로 이어진다.
- 걷기·달리기 등 이동 동작은 프레임 전환 중에도 실제 경과 시간에 따라 위치가 부드럽게 바뀐다.
- 점프는 사이클마다 시작 높이에서 출발해 정해진 높이까지 상승하고 같은 높이로 착지한다.
- 대기 중 마지막 프레임과 화면 위치가 고정된다.
- `ESC` 키 또는 창 닫기 입력으로 프로그램이 정상 종료된다.

[실행] ──> Canvas 생성 및 리소스 로드
          │
          ▼
   [Main Loop 시작]
          │
          ├─> (1) Event 처리 (ESC / 창 닫기)
          ├─> (2) 경과 시간으로 이동 위치와 Frame 인덱스를 갱신
          ├─> (3) 현재 Frame을 SCALE 배율로 렌더링
          │      └─> 1회 루프 완독 시: cycle_count += 1
          ├─> (4) IF cycle_count >= 5:
          │         ├─ 1초 딜레이/타이머 대기
          │         ├─ cycle_count = 0, frame_index = 0
          │         └─ action_index = (action_index + 1) % 전체동작수
          │
          └─> Loop 반복


## 4. 단계별 구현 및 커밋 로드맵 (28 Steps)

- **Step 01**

  - Git: `chore: init canvas and setup clean exit`
  - 내용: `open_canvas(1200, 600)` 및 `close_canvas()` 기본 구조 작성
- **Step 02**

  - Git: `feat: implement main event loop`
  - 내용: SDL 이벤트 처리 및 `ESC` 키 종료 핸들러 구현
- **Step 03**

  - Git: `feat: load sprite sheet image`
  - 내용: `load_image('sonic-sprite.png')` 및 기본 렌더링 확인
- **Step 04**

  - Git: `feat: add scaling factor for sprite visibility`
  - 내용: `SCALE` 상수 정의 및 화면 중앙 확대 출력 로직 추가
- **Step 05**

  - Git: `refactor: initialize animation data structure`
  - 내용: 프레임 튜플 및 애니메이션 딕셔너리 리스트 골격 정의
- **Step 06**

  - Git: `feat: clip single frame for action 1 (idle)`
  - 내용: 1번 모션(대기) 첫 프레임 좌표 `clip_draw` 슬라이싱
- **Step 07**

  - Git: `feat: animate action 1 frames`
  - 내용: 1번 모션의 전체 프레임 연속 재생 루프 구현
- **Step 08**

  - Git: `feat: track cycle completion count`
  - 내용: 1번 모션이 1회 완독될 때마다 카운터를 누적하는 로직 작성
- **Step 09**

  - Git: `feat: limit action 1 to 5 cycles`
  - 내용: 카운터가 5회에 도달했을 때 재생을 일시 멈추는 분기 처리
- **Step 10**

  - Git: `feat: implement 1 second pause timer`
  - 내용: 5회 재생 종료 후 1.0초간 멈추는 타이머 로직 적용
- **Step 11**

  - Git: `feat: extract sprite coordinates for action 2 (walk)`
  - 내용: 2번 모션(걷기) 프레임 좌표 목록 데이터 추가
- **Step 12**

  - Git: `feat: handle sequential transition between actions`
  - 내용: 1번 모션 1초 휴식 후 2번 모션으로 전환하는 로직 구현
- **Step 13**

  - Git: `feat: extract sprite coordinates for action 3 (run)`
  - 내용: 3번 모션(달리기) 좌표 데이터 추출 및 등록
- **Step 14**

  - Git: `feat: extract sprite coordinates for action 4 (jump/roll)`
  - 내용: 4번 모션(점프/구르기) 좌표 데이터 등록
- **Step 15**

  - Git: `feat: extract sprite coordinates for action 5 (skid/push)`
  - 내용: 5번 모션(급정지/밀기) 좌표 데이터 등록
- **Step 16**

  - Git: `feat: extract all remaining sprite actions`
  - 내용: 시트 내 나머지 모든 동작 좌표 전수 등록 완료
- **Step 17**

  - Git: `refactor: generalize action player loop`
  - 내용: 임의의 N개 동작을 자동으로 순차 처리하도록 재생 루프 일반화
- **Step 18**

  - Git: `feat: enable infinite loop playback`
  - 내용: 마지막 동작 종료 후 다시 0번 동작으로 순환하는 무한 루프 완성
- **Step 19**

  - Git: `feat: render on-screen status text`
  - 내용: 현재 동작 이름, 반복 횟수(1~5), 대기 상태 OSD 표시
- **Step 20**

  - Git: `fix: adjust sprite alignment and ground pivot`
  - 내용: 동작별 스프라이트 높낮이 차이로 인한 바닥 흔들림 보정
- **Step 21**

  - Git: `refactor: stabilize frame rate using delta time`
  - 내용: `delay()` 의존도를 줄이고 `get_time()` 기반 델타 타임 재생 적용
- **Step 22**

  - Git: `style: improve background grid and canvas contrast`
  - 내용: 캐릭터 실루엣 구분이 쉽도록 배경색 및 바닥 기준선 가이드 추가
- **Step 23**

  - Git: `test: handle edge cases and runtime verification`
  - 내용: 0프레임 예외 방어 및 전체 시퀀스 완주 테스트 수행
- **Step 24**

  - Git: `docs: finalize inline comments and code clean up`
  - 내용: 단일 파일 내 코드 정리, 독스트링 및 주석 문서화 마무리
- **Step 25**

  - Git: `feat: add per-action movement metadata`
  - 내용: 동작별 제자리·수평·점프 이동 유형과 속도 데이터 등록
- **Step 26**

  - Git: `feat: move walk and run while animating`
  - 내용: 실제 경과 시간으로 위치를 갱신하고 화면 경계에서 반대편으로 이어 이동
- **Step 27**

  - Git: `feat: add jump arc and preserve pause position`
  - 내용: 점프 궤적, 동작 시작 위치의 중앙 초기화, 대기 중 위치 고정 구현
- **Step 28**

  - Git: `test: verify animation and movement together`
  - 내용: 프레임 재생, 화면 경계 순환 이동, 동작 시작 위치 초기화, 점프 착지, 대기 위치 고정 검증
