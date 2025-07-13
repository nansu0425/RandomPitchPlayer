"""
RandomPitchPlayer 타이머 관리자
정확한 타이밍 제어를 담당하는 폴링 기반 타이머
"""
import threading
import time
import queue
from config import TIMER_SLEEP_MS, INTERVAL_UPDATE_FREQUENCY


class TimerManager:
    """RandomPitchPlayer 타이밍 제어를 관리하는 클래스"""
    
    def __init__(self, ui_queue, debug_manager, pitch_selector):
        self.ui_queue = ui_queue
        self.debug_manager = debug_manager
        self.pitch_selector = pitch_selector
        
        # 타이밍 관련 변수들
        self.is_running = False
        self.timer_thread = None
        self.current_interval = 1.0
        self.next_update_time = 0
        self.last_update_time = 0
        self.update_sequence = 0
    
    def start_timer(self, interval):
        """타이머 시작"""
        if self.is_running:
            return False
            
        self.current_interval = interval
        self.is_running = True
        self.update_sequence = 0
        self.last_update_time = time.time()
        
        # 타이머 스레드 시작
        self.timer_thread = threading.Thread(target=self._timer_worker, daemon=True)
        self.timer_thread.start()
        
        if self.debug_manager.debug_mode:
            print(f"[TIMER] RandomPitchPlayer 타이머 시작 - 간격: {interval:.3f}초")
        
        return True
    
    def stop_timer(self):
        """타이머 정지"""
        self.is_running = False
        
        # 스레드 종료 대기 (최대 1초)
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1.0)
        
        if self.debug_manager.debug_mode:
            print("[TIMER] RandomPitchPlayer 타이머 정지")
    
    def update_interval(self, new_interval):
        """실행 중 간격 업데이트"""
        if new_interval != self.current_interval:
            self.current_interval = new_interval
            if self.debug_manager.debug_mode:
                print(f"[TIMER] 간격 변경: {new_interval:.3f}초")
    
    def _timer_worker(self):
        """별도 스레드에서 폴링 방식 타이밍 제어"""
        # 첫 번째 업데이트 시간 설정
        self.next_update_time = time.time() + self.current_interval
        
        while self.is_running:
            current_time = time.time()
            
            # 설정된 간격이 지났는지 확인 (폴링)
            if current_time >= self.next_update_time:
                self._trigger_update(current_time)
            
            # CPU 사용률 최적화를 위한 짧은 대기
            time.sleep(TIMER_SLEEP_MS / 1000.0)
    
    def _trigger_update(self, current_time):
        """업데이트 트리거"""
        self.update_sequence += 1
        
        # 목표 출력 시간 (원래 예정된 시간)
        target_output_time = self.next_update_time
        
        # 음정 선택 (중복 방지)
        from config import SCALE_COLORS
        selected_pitch = self.pitch_selector.get_next_pitch()
        pitch_color = SCALE_COLORS[selected_pitch]
        
        if self.debug_manager.debug_mode:
            print(f"[TRIGGER] {selected_pitch} 음정 트리거 - 목표시간: {target_output_time:.3f}")
        
        # UI 업데이트를 큐에 추가
        self.ui_queue.put({
            'pitch': selected_pitch,
            'color': pitch_color,
            'target_time': target_output_time,
            'sequence': self.update_sequence
        })
        
        # 간격값 업데이트 확인 (INTERVAL_UPDATE_FREQUENCY 초마다)
        if current_time - self.last_update_time > INTERVAL_UPDATE_FREQUENCY:
            self.last_update_time = current_time
        
        # 다음 업데이트 시간 계산 (정확한 간격 유지)
        self.next_update_time = target_output_time + self.current_interval