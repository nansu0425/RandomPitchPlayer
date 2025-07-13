"""
RandomPitchPlayer - 랜덤 음정 플레이어
BPM 메트로놈 기능을 포함한 메인 애플리케이션
"""
import tkinter as tk
import time
import queue
from config import *
from pitch_selector import PitchSelector
from debug_manager import DebugManager
from timer_manager import TimerManager
from ui_manager import UIManager
from timing_utils import TimingUtils
from power_manager import get_power_manager
from tts_manager import get_tts_manager


class RandomPitchPlayer:
    """RandomPitchPlayer 메인 애플리케이션 클래스"""
    
    def __init__(self, master):
        self.master = master
        
        # UI 큐
        self.ui_queue = queue.Queue()
        
        # 컴포넌트 초기화
        self.debug_manager = DebugManager()
        self.pitch_selector = PitchSelector()
        self.ui_manager = UIManager(master, self.debug_manager)
        self.timer_manager = TimerManager(self.ui_queue, self.debug_manager, self.pitch_selector)
        self.power_manager = get_power_manager()  # 전원 매니저 추가
        self.tts_manager = get_tts_manager()      # TTS 매니저 추가
        self.tts_manager.set_master(master)       # tkinter 마스터 설정
        
        # 상태 변수
        self.is_running = False
        self.current_interval = DEFAULT_INTERVAL
        self.current_bpm = DEFAULT_BPM
        
        # 지속 시간 관리 변수들
        self.duration_minutes = DEFAULT_DURATION_MINUTES
        self.session_start_time = 0
        self.duration_end_time = 0
        self.is_duration_limited = True
        
        # UI 설정 완료
        self._setup_ui_commands()
        self._start_background_tasks()
    
    def _setup_ui_commands(self):
        """UI 명령어 설정"""
        self.ui_manager.set_button_commands(
            start_command=self.start_playing,
            stop_command=self.stop_playing,
            debug_command=self.print_debug_info if not RELEASE_MODE else None
        )
    
    def _start_background_tasks(self):
        """백그라운드 작업 시작"""
        self._check_ui_queue()
        self._check_duration_timer()  # 지속 시간 체크 추가
        if not RELEASE_MODE:  # 릴리즈 모드에서는 렌더링 체크 비활성화
            self._check_rendering_completion()
    
    def start_playing(self):
        """음정 재생 시작"""
        if self.is_running:
            return
        
        # 초기화
        self.debug_manager.start_session()
        self.pitch_selector.reset()
        
        # 간격값, BPM, 지속 시간 설정
        self.current_interval = self.ui_manager.get_interval_value()
        self.current_bpm = self.ui_manager.get_current_bpm()
        self.duration_minutes = self.ui_manager.get_duration_minutes()
        
        if self.current_interval <= 0:
            self.ui_manager.set_display_text("오류", "black")
            return
        
        # 지속 시간 설정
        self.session_start_time = time.time()
        self.is_duration_limited = self.duration_minutes > 0
        
        if self.is_duration_limited:
            self.duration_end_time = self.session_start_time + (self.duration_minutes * 60)
        else:
            self.duration_end_time = 0
            self.ui_manager.clear_remaining_time()  # 무제한일 때는 남은 시간 표시 지우기
        
        # 상태 변경
        self.is_running = True
        self.ui_manager.set_button_states(start_enabled=False, stop_enabled=True)
        
        # 전원 관리 시작 (절전 모드 및 화면 보호기 방지)
        if PREVENT_SLEEP_MODE or PREVENT_SCREEN_SAVER or KEEP_DISPLAY_ON:
            self.power_manager.start_power_management()
            # UI 상태 업데이트
            self.ui_manager.update_power_status_display()
        
        # 타이머 시작
        self.timer_manager.start_timer(self.current_interval)
        
        # 첫 번째 음정 표시
        self._display_first_pitch()
        
        # 로그 출력 (릴리즈 모드에서는 출력하지 않음)
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            mode = self.ui_manager.get_current_mode()
            duration_text = f"{self.duration_minutes}분" if self.is_duration_limited else "무제한"
            
            if mode == "bpm":
                tempo_desc = TimingUtils.get_bpm_description(self.current_bpm)
                print(f"[APP] RandomPitchPlayer 시작 - BPM: {self.current_bpm} ({tempo_desc}) = {self.current_interval:.3f}초 간격, 지속시간: {duration_text}")
            else:
                print(f"[APP] RandomPitchPlayer 시작 - 목표 간격: {self.current_interval:.3f}초, 지속시간: {duration_text}")
    
    def stop_playing(self):
        """음정 재생 정지"""
        self.is_running = False
        
        # 타이머 정지
        self.timer_manager.stop_timer()
        
        # 전원 관리 정지 (시스템 기본 절전 설정으로 복원)
        self.power_manager.stop_power_management()
        # UI 상태 업데이트
        self.ui_manager.update_power_status_display()
        
        # TTS 음성 안내 정지 (안전한 호출)
        if hasattr(self.tts_manager, 'stop_speech'):
            try:
                self.tts_manager.stop_speech()
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] TTS 음성 정지 오류: {e}")
        
        # UI 상태 복원
        self.ui_manager.set_button_states(start_enabled=True, stop_enabled=False)
        self.ui_manager.set_display_text("STOP", "black")
        self.ui_manager.clear_remaining_time()  # 남은 시간 표시 지우기
        
        # 지속 시간 초기화
        self.session_start_time = 0
        self.duration_end_time = 0
        self.is_duration_limited = False
        
        # 디버그 정보 자동 출력 (릴리즈 모드에서는 출력하지 않음)
        if ENABLE_PERFORMANCE_ANALYSIS and not RELEASE_MODE:
            self.debug_manager.print_comprehensive_analysis(self.current_interval)
    
    def print_debug_info(self):
        """디버그 정보 출력 (릴리즈 모드에서는 아무것도 하지 않음)"""
        if not RELEASE_MODE:
            self.debug_manager.print_comprehensive_analysis(self.current_interval)
    
    def _display_first_pitch(self):
        """첫 번째 음정 표시"""
        first_pitch = self.pitch_selector.get_next_pitch()
        first_color = SCALE_COLORS[first_pitch]
        
        actual_time = self.ui_manager.update_pitch_display(first_pitch, first_color)
        self.debug_manager.record_display_event(first_pitch, time.time(), actual_time, self.current_interval)
        
        # TTS 음성 안내 추가 - 메인 스레드에서 처리하도록 지연 실행
        if TTS_ENABLED:
            try:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] 첫 음정 TTS 예약 - 음정: {first_pitch}")
                # tkinter.after를 사용하여 메인 스레드에서 TTS 처리
                self.master.after(50, lambda: self._delayed_tts(first_pitch))
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] 첫 음정 TTS 예약 완료")
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] TTS 음성 안내 오류 (첫 음정): {e}")
                    print(f"[MAIN] 오류 타입: {type(e).__name__}")
        else:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[MAIN] TTS가 비활성화되어 있음 (TTS_ENABLED: {TTS_ENABLED})")
        
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print(f"[PLAY] {first_pitch} 첫 출력")
    
    def _delayed_tts(self, pitch):
        """지연된 TTS 처리 (메인 스레드에서 실행)"""
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print(f"[TTS] _delayed_tts 호출됨 - 음정: {pitch}")
            print(f"[TTS] TTS 매니저 상태 - enabled: {self.tts_manager.tts_enabled if self.tts_manager else None}")
            print(f"[TTS] 사용 가능한 메소드들:")
            if self.tts_manager:
                methods = [method for method in dir(self.tts_manager) if not method.startswith('_')]
                for method in methods:
                    if 'speak' in method.lower():
                        print(f"[TTS]   - {method}")
        
        if hasattr(self.tts_manager, 'speak_pitch_sync_main_thread'):
            try:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] speak_pitch_sync_main_thread 호출 시작")
                self.tts_manager.speak_pitch_sync_main_thread(pitch)
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] speak_pitch_sync_main_thread 호출 완료")
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] 메인 스레드 TTS 오류: {e}")
                    print(f"[MAIN] 오류 타입: {type(e).__name__}")
                    import traceback
                    print(f"[MAIN] 오류 상세: {traceback.format_exc()}")
                # 대안으로 비동기 방식 시도
                try:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[MAIN] 대안으로 비동기 TTS 시도")
                    self.tts_manager.speak_pitch_async(pitch)
                except Exception as e2:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[MAIN] 비동기 TTS 오류: {e2}")
        else:
            # 기존 비동기 방식 사용
            try:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] speak_pitch_sync_main_thread 없음, 비동기 방식 사용")
                self.tts_manager.speak_pitch_async(pitch)
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[MAIN] TTS 음성 안내 오류: {e}")
    
    def _check_ui_queue(self):
        """UI 큐 처리"""
        processed_count = 0
        
        try:
            while processed_count < MAX_PROCESSED_UPDATES:
                # 큐에서 UI 업데이트 요청 가져오기 (논블로킹)
                update_data = self.ui_queue.get_nowait()
                
                selected_pitch = update_data['pitch']
                pitch_color = update_data['color']
                target_time = update_data['target_time']
                sequence = update_data['sequence']
                
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[UPDATE] {selected_pitch} UI업데이트 요청 - 목표시간: {target_time:.3f}")
                
                # UI 업데이트 수행
                actual_time = self.ui_manager.update_pitch_display(selected_pitch, pitch_color)
                
                # TTS 음성 안내 추가 - 메인 스레드에서 처리하도록 지연 실행
                if TTS_ENABLED:
                    try:
                        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                            print(f"[MAIN] UI 큐 TTS 예약 - 음정: {selected_pitch}")
                        # tkinter.after를 사용하여 메인 스레드에서 TTS 처리
                        self.master.after(50, lambda p=selected_pitch: self._delayed_tts(p))
                        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                            print(f"[MAIN] UI 큐 TTS 예약 완료")
                    except Exception as e:
                        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                            print(f"[MAIN] TTS 음성 안내 오류 (큐 처리): {e}")
                            print(f"[MAIN] 오류 타입: {type(e).__name__}")
                else:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[MAIN] TTS가 비활성화되어 있음 (TTS_ENABLED: {TTS_ENABLED})")
                
                # 렌더링 완료 대기 목록에 추가 (릴리즈 모드에서는 건너뜀)
                if not RELEASE_MODE:
                    self.debug_manager.add_pending_update(sequence, selected_pitch, pitch_color, target_time)
                
                # 간격값 및 BPM 업데이트
                new_interval = self.ui_manager.get_interval_value()
                new_bpm = self.ui_manager.get_current_bpm()
                
                if new_interval != self.current_interval:
                    self.current_interval = new_interval
                    self.current_bpm = new_bpm
                    self.timer_manager.update_interval(new_interval)
                
                processed_count += 1
                    
        except queue.Empty:
            pass  # 큐가 비어있으면 계속 진행
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[ERROR] UI 큐 처리 오류: {e}")
        
        # UI 큐 체크 반복
        self.master.after(UI_QUEUE_CHECK_MS, self._check_ui_queue)
    
    def _check_rendering_completion(self):
        """렌더링 완료 확인 (릴리즈 모드에서는 실행되지 않음)"""
        if RELEASE_MODE:
            return
            
        if not self.is_running:
            self.master.after(RENDER_CHECK_MS, self._check_rendering_completion)
            return
        
        try:
            completed_updates = []
            
            for sequence, update_info in self.debug_manager.pending_updates.items():
                expected_text = update_info['pitch']
                target_time = update_info['target_time']
                
                # 실제 화면에 반영되었는지 확인
                if self.ui_manager.check_rendering_completion(expected_text):
                    # 렌더링 완료! 실제 출력 시간 기록
                    actual_render_time = time.time()
                    self.debug_manager.record_display_event(
                        expected_text, target_time, actual_render_time, self.current_interval
                    )
                    completed_updates.append(sequence)
                    
                    if ENABLE_CONSOLE_LOGS:
                        print(f"[DONE] {expected_text} 렌더링 완료 확인 - 화면반영시간: {actual_render_time:.3f}")
            
            # 완료된 업데이트 제거
            for sequence in completed_updates:
                self.debug_manager.complete_pending_update(sequence)
            
            # 디버그 정보 업데이트 (BPM 정보 포함)
            if ENABLE_DEBUG_UI:
                debug_text = self.debug_manager.get_debug_summary()
                self.ui_manager.update_debug_info(debug_text)
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS:
                print(f"[ERROR] 렌더링 확인 오류: {e}")
        
        # 렌더링 완료 확인 반복
        self.master.after(RENDER_CHECK_MS, self._check_rendering_completion)
    
    def _duration_completed(self):
        """지속 시간 완료 처리"""
        if self.is_running:
            self.stop_playing()
            # 중지 버튼을 눌렀을 때와 동일한 텍스트로 표시
            # stop_playing()에서 이미 "STOP"을 표시하므로 추가 텍스트 설정 불필요
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[APP] 지속 시간 {self.duration_minutes}분 완료 - 자동 정지")
    
    def _check_duration_timer(self):
        """지속 시간 확인 및 남은 시간 업데이트"""
        if self.is_running and self.is_duration_limited:
            current_time = time.time()
            
            if current_time >= self.duration_end_time:
                # 지속 시간 완료
                self._duration_completed()
            else:
                # 남은 시간 계산 및 표시
                remaining_seconds = self.duration_end_time - current_time
                self.ui_manager.update_remaining_time(remaining_seconds)
        
        # 다음 체크 예약 (1초마다)
        self.master.after(REMAINING_TIME_UPDATE_MS, self._check_duration_timer)
    
    def on_closing(self):
        """앱 종료 시 정리"""
        try:
            # 먼저 재생 정지
            self.stop_playing()
            
            # TTS 리소스 우선 정리 (COM 객체 문제 방지)
            if hasattr(self, 'tts_manager') and hasattr(self.tts_manager, 'cleanup'):
                try:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print("[MAIN] TTS 리소스 정리 시작")
                    self.tts_manager.cleanup()
                    # TTS 정리 후 짧은 대기
                    time.sleep(0.1)
                except Exception as e:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[MAIN] TTS 리소스 정리 오류 (무시됨): {e}")
            
            # 전원 관리 리소스 정리
            if hasattr(self, 'power_manager') and hasattr(self.power_manager, 'cleanup'):
                try:
                    self.power_manager.cleanup()
                except Exception as e:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[MAIN] 전원 관리 정리 오류: {e}")
            
            # 추가 정리 시간 확보
            time.sleep(0.05)
            
        except Exception as e:
            # 종료 시 모든 오류 무시
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[MAIN] 종료 처리 오류 (무시됨): {e}")
        finally:
            # 최종 tkinter 종료
            try:
                self.master.destroy()
            except:
                pass


# 하위 호환성을 위한 별칭
MusicScaleApp = RandomPitchPlayer


def main():
    """메인 함수"""
    root = tk.Tk()
    app = RandomPitchPlayer(root)
    
    # 종료 이벤트 처리
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()