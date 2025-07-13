"""
RandomPitchPlayer 전원 관리자
화면 보호기 및 절전 모드 방지 담당
"""
import threading
import time
import platform
from config import *

# Windows API 사용을 위한 임포트
_power_api_available = False
_ctypes_available = False

try:
    import ctypes
    from ctypes import wintypes
    _ctypes_available = True
    
    if platform.system() == 'Windows':
        # Windows 전원 관리 상수들
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        ES_AWAYMODE_REQUIRED = 0x00000040
        
        # kernel32.dll 함수들
        kernel32 = ctypes.windll.kernel32
        _power_api_available = True
        
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print("[POWER] Windows 전원 관리 API 사용 가능")
    else:
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print("[POWER] Windows가 아닌 시스템 - 전원 관리 기능 제한적")
            
except ImportError as e:
    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
        print(f"[POWER] 전원 관리 라이브러리 임포트 실패: {e}")


class PowerManager:
    """RandomPitchPlayer 전원 관리를 담당하는 클래스"""
    
    def __init__(self):
        self.prevent_sleep = PREVENT_SLEEP_MODE
        self.prevent_screen_saver = PREVENT_SCREEN_SAVER
        self.keep_display_on = KEEP_DISPLAY_ON
        self.update_interval = POWER_THREAD_UPDATE_MS / 1000.0  # 초 단위로 변환
        
        # 전원 관리 활성화 상태
        self.is_active = False
        self.power_thread = None
        self.stop_thread = False
        
        # 원래 전원 설정 백업 (복원용)
        self.original_execution_state = None
        
        self.power_available = _power_api_available and _ctypes_available
        
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            if self.power_available:
                print("[POWER] PowerManager 초기화 완료 - Windows 전원 관리 활성화")
            else:
                print("[POWER] PowerManager 초기화 완료 - 전원 관리 기능 비활성화")
    
    def start_power_management(self):
        """전원 관리 시작"""
        if not self.power_available or self.is_active:
            return
        
        try:
            # Windows 전원 상태 설정
            execution_state = ES_CONTINUOUS
            
            if self.prevent_sleep:
                execution_state |= ES_SYSTEM_REQUIRED
            
            if self.keep_display_on:
                execution_state |= ES_DISPLAY_REQUIRED
            
            if self.prevent_screen_saver:
                execution_state |= ES_AWAYMODE_REQUIRED
            
            # 전원 상태 설정 적용
            result = kernel32.SetThreadExecutionState(execution_state)
            
            if result != 0:
                self.original_execution_state = result
                self.is_active = True
                self.stop_thread = False
                
                # 주기적으로 전원 상태 갱신하는 스레드 시작
                self.power_thread = threading.Thread(target=self._power_maintenance_thread, daemon=True)
                self.power_thread.start()
                
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[POWER] 전원 관리 시작 - 절전모드 방지: {self.prevent_sleep}, 화면보호 방지: {self.prevent_screen_saver}")
            else:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print("[POWER] 전원 상태 설정 실패")
                    
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[POWER] 전원 관리 시작 실패: {e}")
    
    def stop_power_management(self):
        """전원 관리 정지"""
        if not self.power_available or not self.is_active:
            return
        
        try:
            # 스레드 정지
            self.stop_thread = True
            if self.power_thread and self.power_thread.is_alive():
                self.power_thread.join(timeout=1.0)
            
            # 원래 전원 상태로 복원
            kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            
            self.is_active = False
            self.original_execution_state = None
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[POWER] 전원 관리 정지 - 시스템 기본 절전 설정으로 복원")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[POWER] 전원 관리 정지 실패: {e}")
    
    def _power_maintenance_thread(self):
        """전원 상태를 주기적으로 갱신하는 백그라운드 스레드"""
        while not self.stop_thread:
            try:
                # 전원 상태 갱신
                execution_state = ES_CONTINUOUS
                
                if self.prevent_sleep:
                    execution_state |= ES_SYSTEM_REQUIRED
                
                if self.keep_display_on:
                    execution_state |= ES_DISPLAY_REQUIRED
                
                if self.prevent_screen_saver:
                    execution_state |= ES_AWAYMODE_REQUIRED
                
                kernel32.SetThreadExecutionState(execution_state)
                
                # 다음 갱신까지 대기
                time.sleep(self.update_interval)
                
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[POWER] 전원 상태 갱신 오류: {e}")
                break
    
    def toggle_prevent_sleep(self, enabled):
        """절전 모드 방지 토글"""
        self.prevent_sleep = enabled
        if self.is_active:
            # 이미 활성화된 상태면 재시작
            self.stop_power_management()
            self.start_power_management()
    
    def toggle_prevent_screen_saver(self, enabled):
        """화면 보호기 방지 토글"""
        self.prevent_screen_saver = enabled
        if self.is_active:
            # 이미 활성화된 상태면 재시작
            self.stop_power_management()
            self.start_power_management()
    
    def toggle_keep_display_on(self, enabled):
        """화면 켜짐 유지 토글"""
        self.keep_display_on = enabled
        if self.is_active:
            # 이미 활성화된 상태면 재시작
            self.stop_power_management()
            self.start_power_management()
    
    def is_power_management_active(self):
        """전원 관리 활성화 상태 반환"""
        return self.is_active
    
    def is_power_management_available(self):
        """전원 관리 기능 사용 가능 여부 반환"""
        return self.power_available
    
    def get_power_status_info(self):
        """현재 전원 관리 상태 정보 반환"""
        if not self.power_available:
            return "전원 관리: 사용 불가"
        
        if not self.is_active:
            return "전원 관리: 비활성화"
        
        status_parts = []
        if self.prevent_sleep:
            status_parts.append("절전방지")
        if self.prevent_screen_saver:
            status_parts.append("화면보호방지")
        if self.keep_display_on:
            status_parts.append("화면유지")
        
        return f"전원 관리: {', '.join(status_parts)} 활성화"
    
    def cleanup(self):
        """전원 관리 리소스 정리"""
        try:
            self.stop_power_management()
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[POWER] 전원 관리 리소스 정리 완료")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[POWER] 전원 관리 리소스 정리 오류: {e}")


# 전역 전원 매니저 인스턴스
_power_manager_instance = None

def get_power_manager():
    """전원 매니저 싱글톤 인스턴스 반환"""
    global _power_manager_instance
    if _power_manager_instance is None:
        _power_manager_instance = PowerManager()
    return _power_manager_instance