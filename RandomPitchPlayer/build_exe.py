"""
RandomPitchPlayer EXE 빌드 스크립트
PyInstaller를 사용하여 Windows 데스크탑 실행 파일(.exe)을 생성합니다.

요구사항:
- Python 3.7 이상
- PyInstaller (pip install pyinstaller)
- tkinter (보통 Python과 함께 설치됨)

사용법:
1. 릴리즈 모드로 설정: python build_tool.py (옵션 1 선택)
2. EXE 빌드 실행: python build_exe.py
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

# 빌드 설정
APP_NAME = "RandomPitchPlayer"
APP_VERSION = "1.0"
MAIN_SCRIPT = "main.py"
ICON_FILE = "icon.ico"  # 아이콘 파일 (선택사항)

# 빌드 디렉토리
BUILD_DIR = "build"
DIST_DIR = "dist"
SPEC_FILE = f"{APP_NAME}.spec"

def check_dependencies():
    """필수 의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    # Python 버전 확인
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print(f"❌ Python 3.7 이상이 필요합니다. 현재 버전: {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # PyInstaller 확인
    try:
        result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PyInstaller 버전: {result.stdout.strip()}")
        else:
            raise Exception("PyInstaller 실행 실패")
    except Exception as e:
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("   설치 명령: pip install pyinstaller")
        return False
    
    # 메인 스크립트 확인
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ 메인 스크립트 '{MAIN_SCRIPT}'를 찾을 수 없습니다.")
        return False
    else:
        print(f"✅ 메인 스크립트: {MAIN_SCRIPT}")
    
    return True

def check_release_mode():
    """릴리즈 모드 확인"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RELEASE_MODE = True' in content:
                print("✅ 릴리즈 모드로 설정됨")
                return True
            else:
                print("⚠️  현재 디버그 모드입니다.")
                print("   릴리즈 모드로 변경하려면: python build_tool.py (옵션 1 선택)")
                response = input("그래도 계속 진행하시겠습니까? (y/N): ")
                return response.lower() in ['y', 'yes']
    except Exception as e:
        print(f"❌ config.py 파일 확인 실패: {e}")
        return False

def clean_build_dirs():
    """이전 빌드 디렉토리 정리"""
    print("🧹 이전 빌드 파일 정리 중...")
    
    dirs_to_clean = [BUILD_DIR, DIST_DIR, "__pycache__"]
    files_to_clean = [SPEC_FILE]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   삭제됨: {dir_name}/")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   삭제됨: {file_name}")

def create_icon():
    """기본 아이콘 생성 (아이콘 파일이 없는 경우)"""
    if not os.path.exists(ICON_FILE):
        print(f"⚠️  아이콘 파일 '{ICON_FILE}'이 없습니다. 기본 아이콘을 사용합니다.")
        return None
    else:
        print(f"✅ 아이콘 파일: {ICON_FILE}")
        return ICON_FILE

def build_exe():
    """PyInstaller를 사용하여 EXE 파일 빌드"""
    print("🔨 EXE 파일 빌드 시작...")
    
    # PyInstaller 명령어 구성
    cmd = [
        'pyinstaller',
        '--onefile',  # 단일 실행 파일로 생성
        '--windowed',  # 콘솔 창 숨김 (GUI 앱)
        '--name', APP_NAME,  # 실행 파일 이름
        '--distpath', DIST_DIR,  # 출력 디렉토리
        '--workpath', BUILD_DIR,  # 임시 빌드 디렉토리
        '--clean',  # 빌드 전 캐시 정리
    ]
    
    # 아이콘 추가 (있는 경우)
    icon_path = create_icon()
    if icon_path:
        cmd.extend(['--icon', icon_path])
    
    # 추가 옵션들
    cmd.extend([
        '--add-data', 'config.py;.',  # config.py 포함
        '--hidden-import', 'tkinter',  # tkinter 명시적 포함
        '--hidden-import', 'tkinter.font',  # tkinter.font 포함
        '--hidden-import', 'pyttsx3',  # pyttsx3 포함 (TTS용)
        '--hidden-import', 'pyttsx3.drivers',  # pyttsx3 드라이버 포함
        '--hidden-import', 'pyttsx3.drivers.sapi5',  # Windows SAPI5 드라이버
        '--noconsole',  # 콘솔 창 완전히 숨김
    ])
    
    # 메인 스크립트 추가
    cmd.append(MAIN_SCRIPT)
    
    print(f"빌드 명령어: {' '.join(cmd)}")
    print()
    
    # PyInstaller 실행
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller 빌드 성공!")
        if result.stdout:
            print("빌드 출력:")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ PyInstaller 빌드 실패!")
        print("오류 출력:")
        print(e.stderr)
        return False
    
    return True

def verify_build():
    """빌드 결과 확인"""
    exe_path = Path(DIST_DIR) / f"{APP_NAME}.exe"
    
    if exe_path.exists():
        file_size = exe_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ EXE 파일 생성 성공!")
        print(f"   파일 경로: {exe_path}")
        print(f"   파일 크기: {file_size_mb:.1f} MB")
        
        # 실행 파일 테스트 여부 묻기
        response = input("\n생성된 EXE 파일을 테스트하시겠습니까? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("🚀 EXE 파일 실행 중...")
            try:
                subprocess.Popen([str(exe_path)])
                print("✅ EXE 파일이 실행되었습니다.")
            except Exception as e:
                print(f"❌ EXE 파일 실행 실패: {e}")
        
        return True
    else:
        print("❌ EXE 파일이 생성되지 않았습니다.")
        return False

def create_installer_info():
    """설치 정보 파일 생성"""
    info_content = f"""
{APP_NAME} v{APP_VERSION}
============================

설치 및 사용 방법:
1. {APP_NAME}.exe 파일을 원하는 위치에 복사
2. 바로가기를 만들어 바탕화면에 배치 (선택사항)
3. 더블클릭으로 실행

시스템 요구사항:
- Windows 7 이상
- 약 {Path(DIST_DIR) / f'{APP_NAME}.exe'}의 파일 크기만큼의 디스크 공간

특징:
- 설치 없이 바로 실행 가능한 단일 실행 파일
- 별도의 Python 설치 불필요
- 모든 필요한 라이브러리가 포함됨

문제 해결:
- Windows Defender 경고: 서명되지 않은 실행 파일에 대한 일반적인 경고입니다.
  "추가 정보" -> "실행"을 클릭하여 실행할 수 있습니다.
- 실행 오류: 파일을 다른 위치로 이동해보거나 관리자 권한으로 실행해보세요.

빌드 날짜: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    info_file = Path(DIST_DIR) / "README.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print(f"📄 설치 정보 파일 생성: {info_file}")

def main():
    """메인 함수"""
    print("=" * 60)
    print(f"🎵 {APP_NAME} EXE 빌드 도구 v{APP_VERSION}")
    print("=" * 60)
    print()
    
    # 1. 의존성 확인
    if not check_dependencies():
        print("\n❌ 의존성 확인 실패. 빌드를 중단합니다.")
        return 1
    
    print()
    
    # 2. 릴리즈 모드 확인
    if not check_release_mode():
        print("\n❌ 빌드를 중단합니다.")
        return 1
    
    print()
    
    # 3. 이전 빌드 정리
    clean_build_dirs()
    print()
    
    # 4. EXE 빌드
    if not build_exe():
        print("\n❌ EXE 빌드 실패!")
        return 1
    
    print()
    
    # 5. 빌드 결과 확인
    if not verify_build():
        print("\n❌ 빌드 검증 실패!")
        return 1
    
    # 6. 설치 정보 생성
    create_installer_info()
    
    print()
    print("🎉 EXE 빌드가 완료되었습니다!")
    print(f"📂 배포 파일: {DIST_DIR}/ 폴더를 확인하세요.")
    print()
    print("배포 방법:")
    print(f"1. {DIST_DIR}/ 폴더의 모든 파일을 압축")
    print("2. 사용자에게 배포")
    print("3. 사용자는 압축 해제 후 .exe 파일 실행")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nEnter 키를 눌러 종료...")
    sys.exit(exit_code)