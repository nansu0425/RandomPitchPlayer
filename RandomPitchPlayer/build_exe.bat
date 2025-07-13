@echo off
chcp 65001 > nul
echo ====================================
echo RandomPitchPlayer EXE 빌드 시작
echo ====================================
echo.

echo 1단계: 필요한 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo 패키지 설치 실패!
    pause
    exit /b 1
)

echo.
echo 2단계: 릴리즈 모드로 설정 중...
python build_tool.py
if errorlevel 1 (
    echo 릴리즈 모드 설정 실패!
    pause
    exit /b 1
)

echo.
echo 3단계: EXE 파일 빌드 중...
python build_exe.py
if errorlevel 1 (
    echo EXE 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ====================================
echo 빌드 완료!
echo dist 폴더에서 확인하세요.
echo ====================================
pause