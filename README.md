# RandomPitchPlayer 🎵

> **무작위 음정 연습을 위한 시각적 & 음성 가이드 프로그램**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

RandomPitchPlayer는 음정 훈련과 연습을 위한 Python 기반 데스크탑 애플리케이션입니다. 무작위로 음정(C, D, E, F, G, A, B)을 표시하고 음성으로 안내하여 효과적인 음정 연습을 도와줍니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **무작위 음정 표시**: 7개 음정(C, D, E, F, G, A, B)을 랜덤하게 표시
- **컬러 코딩**: 각 음정마다 고유한 색상으로 시각적 구분
- **음성 안내(TTS)**: Google Text-to-Speech를 활용한 고품질 음성 가이드
- **BPM 메트로놈**: 정확한 박자 연습을 위한 메트로놈 기능

### ⚙️ 고급 기능
- **듀얼 타이밍 모드**: 초 단위 또는 BPM 설정 지원
- **지속 시간 설정**: 연습 시간 제한 및 무제한 모드
- **전원 관리**: 연습 중 절전 모드 및 화면 보호기 방지
- **실시간 상태 표시**: 남은 시간, 전원 상태, TTS 상태 모니터링

## 🖼️ 스크린샷

### 메인 화면
```
┌─────────────────────────────────────────┐
│              RandomPitchPlayer          │
│                                         │
│                   C                     │  ← 현재 음정 (큰 글씨)
│                (빨간색)                  │
│                                         │
│         남은 시간: 4분 23초              │
│     😴 전원 관리: 대기 중               │
│     🎤 TTS: 대기 중 (gTTS 영어)         │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │         타이밍 모드:                ││
│  │    ( ) 초 단위  (●) BPM (메트로놈)  ││
│  │                                     ││
│  │        BPM (분당 비트): [60]        ││
│  │     지속 시간 (분, 0=무제한): [5]   ││
│  │        ☑ 음성 안내 (TTS)           ││
│  │                                     ││
│  │    60 BPM - 느림 (Lento)           ││
│  │                                     ││
│  │     [시작]  [정지]  [로그출력]      ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## 🚀 설치 및 실행

### 방법 1: 릴리즈 다운로드 (권장)
1. [Releases](../../releases) 페이지에서 최신 버전 다운로드
2. ZIP 파일 압축 해제
3. `RandomPitchPlayer.exe` 실행

### 방법 2: 소스코드에서 빌드

#### 필수 요구사항
- Python 3.7 이상
- Windows 7 이상

#### 설치 단계
```bash
# 1. 저장소 클론
git clone https://github.com/your-username/RandomPitchPlayer.git
cd RandomPitchPlayer

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 프로그램 실행
python main.py
```

#### EXE 빌드 (선택사항)
```bash
# 1. 릴리즈 모드로 설정
python build_tool.py
# 옵션 1 선택: 릴리즈 모드

# 2. EXE 파일 빌드
python build_exe.py

# 3. 결과물 확인
# dist/RandomPitchPlayer.exe 생성됨
```

## 🛠️ 기술 스택

### 프로그래밍 언어 & 프레임워크
- **Python 3.7+**: 메인 개발 언어
- **tkinter**: GUI 프레임워크 (Python 기본 포함)

### 주요 라이브러리
- **gTTS (Google Text-to-Speech)**: 고품질 음성 합성
- **pygame**: 오디오 재생 엔진
- **PyInstaller**: EXE 빌드 도구

### 시스템 통합
- **Windows Power Management API**: 절전 모드 제어
- **Threading**: 비동기 작업 처리
- **임시 파일 시스템**: TTS 오디오 캐싱

## 📁 프로젝트 구조

```
RandomPitchPlayer/
├── 📄 main.py                    # 메인 애플리케이션 진입점
├── 📄 config.py                  # 현재 설정 (빌드 시 생성)
├── 📄 config_debug.py            # 개발/디버그 설정
├── 📄 config_release.py          # 릴리즈/배포 설정
├── 📄 requirements.txt           # Python 의존성 목록
├── 📄 .gitignore                 # Git 무시 파일 목록
│
├── 🎵 Core Modules/
│   ├── 📄 ui_manager.py          # UI 관리 및 렌더링
│   ├── 📄 tts_manager.py         # TTS 음성 안내 시스템
│   ├── 📄 timer_manager.py       # 정밀 타이밍 제어
│   ├── 📄 pitch_selector.py      # 음정 선택 로직
│   ├── 📄 power_manager.py       # 전원 관리 시스템
│   ├── 📄 debug_manager.py       # 디버깅 및 성능 분석
│   └── 📄 timing_utils.py        # BPM 계산 유틸리티
│
├── 🔨 Build System/
│   ├── 📄 build_tool.py          # 빌드 모드 전환 도구
│   ├── 📄 build_exe.py           # PyInstaller EXE 빌드
│   ├── 📄 build_exe.bat          # Windows 배치 빌드
│   ├── 📄 build_exe.ps1          # PowerShell 빌드 스크립트
│   └── 📄 BUILD_README.md        # 빌드 가이드 문서
│
└── 📁 Generated/ (빌드 시 생성)
    ├── build/                    # PyInstaller 임시 파일
    ├── dist/                     # 최종 EXE 및 배포 파일
    └── random_pitch_tts_*/       # TTS 임시 오디오 캐시
```

## ⚙️ 설정 옵션

### TTS (음성 안내) 설정
```python
TTS_ENABLED = True                    # TTS 기능 활성화
TTS_LANGUAGE_KOREAN = False           # 언어 (False: 영어, True: 한국어)
TTS_VOLUME = 0.8                      # 음량 (0.0 ~ 1.0)
```

### 타이밍 설정
```python
DEFAULT_BPM = 60                      # 기본 BPM
DEFAULT_INTERVAL = 1.0                # 기본 간격 (초)
DEFAULT_DURATION_MINUTES = 5          # 기본 연습 시간 (분)
```

### 전원 관리 설정
```python
PREVENT_SLEEP_MODE = True             # 절전 모드 방지
PREVENT_SCREEN_SAVER = True           # 화면 보호기 방지
KEEP_DISPLAY_ON = True                # 화면 켜짐 유지
```

## 💡 사용 방법

### 1. 기본 연습
1. 프로그램 실행
2. BPM 또는 초 단위로 타이밍 설정
3. 지속 시간 설정 (0 = 무제한)
4. **[시작]** 버튼 클릭
5. 화면에 표시되는 음정을 따라 연습

### 2. 고급 설정
- **음성 안내**: 체크박스로 TTS on/off
- **BPM 모드**: 메트로놈처럼 정확한 박자 연습
- **컬러 코딩**: 각 음정마다 다른 색상으로 시각적 학습

### 3. 상태 모니터링
- **남은 시간**: 설정한 연습 시간 표시
- **전원 상태**: 절전 모드 방지 상태
- **TTS 상태**: 음성 안내 시스템 상태

## 🎵 음정 컬러 매핑

| 음정 | 색상 | 도레미 |
|------|------|--------|
| C | 🔴 빨간색 | 도 |
| D | 🟠 주황색 | 레 |
| E | 🟡 황금색 | 미 |
| F | 🟢 라임그린 | 파 |
| G | 🔵 청록색 | 솔 |
| A | 🟦 로얄블루 | 라 |
| B | 🟣 블루바이올렛 | 시 |

## 🐛 문제 해결

### Windows Defender 경고
- **문제**: "Windows에서 PC를 보호했습니다" 경고
- **해결**: "추가 정보" → "실행" 클릭
- **원인**: 서명되지 않은 실행 파일에 대한 일반적인 보안 경고

### TTS 음성이 들리지 않음
- 시스템 볼륨 확인
- 스피커/헤드셋 연결 확인
- 프로그램 내 TTS 체크박스 확인
- 인터넷 연결 확인 (gTTS는 온라인 필요)

### 빌드 오류
```bash
# 빌드 캐시 정리 후 재시도
rmdir /s build dist
python build_exe.py
```

## 🤝 기여하기

프로젝트에 기여를 원하신다면:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 개발 환경 설정
```bash
# 개발 모드로 설정
python build_tool.py
# 옵션 2 선택: 디버그 모드

# 디버그 모드에서 실행
python main.py
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사 인사

- **Google Text-to-Speech (gTTS)**: 고품질 음성 합성 제공
- **pygame**: 안정적인 오디오 재생 엔진
- **PyInstaller**: 간편한 EXE 빌드 솔루션
- **tkinter**: Python 기본 GUI 프레임워크

## 📞 연락처

프로젝트 관련 문의나 제안사항이 있으시면:

- GitHub Issues: [Create an issue](../../issues)
- GitHub Discussions: [Join the discussion](../../discussions)

---

**RandomPitchPlayer**로 효과적인 음정 연습하세요! 🎵