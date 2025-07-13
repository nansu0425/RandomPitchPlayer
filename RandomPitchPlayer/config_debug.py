"""
RandomPitchPlayer 개발/디버그용 설정 파일
이 파일을 config.py로 복사하여 디버그 빌드를 만드세요.

사용법:
1. 릴리즈 배포 시: config_release.py를 config.py로 복사
2. 개발/디버그 시: config_debug.py를 config.py로 복사
"""

# 빌드 모드 설정 - 디버그 모드
RELEASE_MODE = False  # 디버그 모드 활성화

# 디버그 모드 설정
DEBUG_MODE = True
ENABLE_CONSOLE_LOGS = True       # 콘솔 로그 출력 활성화
ENABLE_DEBUG_UI = True           # 디버그 UI 요소 활성화
ENABLE_PERFORMANCE_ANALYSIS = True  # 성능 분석 기능 활성화

# 음정 설정 (Pitch Settings)
SCALES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# 색상 매핑
SCALE_COLORS = {
    'C': '#FF0000',  # 빨간색
    'D': '#FF8C00',  # 주황색
    'E': '#FFD700',  # 황금색
    'F': '#32CD32',  # 라임그린
    'G': '#00CED1',  # 청록색
    'A': '#4169E1',  # 로얄블루
    'B': '#8A2BE2'   # 블루바이올렛
}

# UI 설정
DEFAULT_WINDOW_SIZE = "800x600"
DEFAULT_INTERVAL = 1.0
MIN_INTERVAL = 0.1
MAX_INTERVAL = 60.0

# BPM 메트로놈 설정
DEFAULT_BPM = 60        # 기본 BPM (분당 60비트 = 1초마다)
MIN_BPM = 30           # 최소 BPM (2초 간격)
MAX_BPM = 300          # 최대 BPM (0.2초 간격)
BPM_MODE_ENABLED = True # BPM 모드 기본 활성화

# 지속 시간 설정 (Duration Settings)
DEFAULT_DURATION_MINUTES = 5    # 기본 지속 시간 (분)
MIN_DURATION_MINUTES = 1        # 최소 지속 시간 (분)
MAX_DURATION_MINUTES = 60       # 최대 지속 시간 (분)
DURATION_MODE_ENABLED = True    # 지속 시간 모드 기본 활성화
UNLIMITED_DURATION = 0          # 무제한 시간 (0분으로 설정)
REMAINING_TIME_UPDATE_MS = 1000 # 남은 시간 업데이트 간격 (밀리초)

# 전원 관리 설정 (Power Management Settings)
PREVENT_SLEEP_MODE = True       # 실행 중 절전 모드 방지
PREVENT_SCREEN_SAVER = True     # 실행 중 화면 보호기 방지
KEEP_DISPLAY_ON = True          # 실행 중 화면 켜짐 유지
POWER_THREAD_UPDATE_MS = 30000  # 전원 상태 유지 갱신 간격 (30초)

# TTS (Text-to-Speech) 설정
TTS_ENABLED = True              # TTS 기능 활성화
TTS_RATE = 150                  # 말하기 속도 (기본: 200, 범위: 50-300)
TTS_VOLUME = 0.8                # TTS 볼륨 (0.0 ~ 1.0)
TTS_VOICE_INDEX = 0             # 음성 인덱스 (0: 기본, 1: 대안)
TTS_LANGUAGE_KOREAN = False     # 한국어 음성 사용 여부 (False: 영어)

# 음정별 TTS 텍스트 매핑
TTS_PITCH_TEXTS = {
    'C': '도',      # C = 도
    'D': '레',      # D = 레  
    'E': '미',      # E = 미
    'F': '파',      # F = 파
    'G': '솔',      # G = 솔
    'A': '라',      # A = 라
    'B': '시'       # B = 시
}

# TTS 영어 텍스트 (한국어 TTS가 없을 때)
TTS_PITCH_TEXTS_EN = {
    'C': 'C',       # C
    'D': 'D',       # D
    'E': 'E',       # E  
    'F': 'F',       # F
    'G': 'G',       # G
    'A': 'A',       # A
    'B': 'B'        # B
}

# 폰트 설정 (음정 표시를 더 크게)
DEFAULT_FONT_SIZE = 240  # 음정 표시 폰트 크기
MIN_FONT_SIZE = 120      
MAX_FONT_SIZE = 400      
FONT_SCALE_FACTOR = 0.20 # 창 크기 대비 폰트 크기 비율
KOREAN_FONTS = ['맑은 고딕', 'Malgun Gothic', '굴림', 'Gulim', 'Arial Unicode MS']

# 타이밍 설정
TIMER_SLEEP_MS = 1
UI_QUEUE_CHECK_MS = 2
RENDER_CHECK_MS = 5
FONT_UPDATE_DELAY_MS = 500
INTERVAL_UPDATE_FREQUENCY = 0.5

# 디버깅 설정 (디버그 모드에서는 활성화)
MAX_TIMING_LOGS = 200    # 로그 저장 활성화
MAX_PROCESSED_UPDATES = 3

# 윈도우 리사이즈 설정
RESIZE_THRESHOLD = 50
FONT_SIZE_CHANGE_THRESHOLD = 5

# 디버그 모드 실행 알림
print("RandomPitchPlayer - 개발/디버그 모드로 실행 중...")