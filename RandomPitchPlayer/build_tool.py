"""
RandomPitchPlayer 빌드 스크립트
릴리즈/디버그 모드를 쉽게 전환할 수 있는 스크립트
"""
import shutil
import os

def build_release():
    """릴리즈 모드로 빌드"""
    try:
        shutil.copy2('config_release.py', 'config.py')
        print("✅ 릴리즈 모드로 설정되었습니다.")
        print("   - 모든 로그 기능 비활성화")
        print("   - 디버그 UI 요소 제거")
        print("   - 성능 분석 기능 비활성화")
        print("   - 최적화된 실행 모드")
    except Exception as e:
        print(f"❌ 릴리즈 빌드 실패: {e}")

def build_debug():
    """디버그 모드로 빌드"""
    try:
        shutil.copy2('config_debug.py', 'config.py')
        print("✅ 디버그 모드로 설정되었습니다.")
        print("   - 모든 로그 기능 활성화")
        print("   - 디버그 UI 요소 표시")
        print("   - 성능 분석 기능 활성화")
        print("   - 개발자 도구 사용 가능")
    except Exception as e:
        print(f"❌ 디버그 빌드 실패: {e}")

def show_current_mode():
    """현재 빌드 모드 확인"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'RELEASE_MODE = True' in content:
                print("🏗️  현재 모드: 릴리즈 (Release)")
            elif 'RELEASE_MODE = False' in content:
                print("🔧 현재 모드: 디버그 (Debug)")
            else:
                print("❓ 현재 모드: 알 수 없음")
    except Exception as e:
        print(f"❌ 모드 확인 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 50)
    print("🎵 RandomPitchPlayer 빌드 도구")
    print("=" * 50)
    
    show_current_mode()
    print()
    
    while True:
        print("옵션을 선택하세요:")
        print("1. 릴리즈 모드로 빌드 (배포용)")
        print("2. 디버그 모드로 빌드 (개발용)")
        print("3. 현재 모드 확인")
        print("4. 종료")
        print()
        
        choice = input("선택 (1-4): ").strip()
        
        if choice == '1':
            build_release()
        elif choice == '2':
            build_debug()
        elif choice == '3':
            show_current_mode()
        elif choice == '4':
            print("👋 빌드 도구를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")
        
        print()

if __name__ == "__main__":
    main()