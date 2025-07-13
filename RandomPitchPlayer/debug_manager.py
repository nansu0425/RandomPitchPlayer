"""
RandomPitchPlayer 디버그 및 성능 분석 관리자
타이밍 로그, 지연 분석, 성능 측정 담당
"""
import time
from config import DEBUG_MODE, MAX_TIMING_LOGS, ENABLE_CONSOLE_LOGS, ENABLE_PERFORMANCE_ANALYSIS, RELEASE_MODE


class DebugManager:
    """RandomPitchPlayer 디버깅 및 성능 분석을 관리하는 클래스"""
    
    def __init__(self):
        self.debug_mode = DEBUG_MODE
        self.enable_logs = ENABLE_CONSOLE_LOGS
        self.enable_performance = ENABLE_PERFORMANCE_ANALYSIS
        
        # 릴리즈 모드에서는 데이터 저장도 최소화
        if RELEASE_MODE:
            self.timing_logs = []
            self.actual_display_times = []
            self.target_display_times = []
            self.display_intervals = []
            self.interval_delays = []
            self.pending_updates = {}
        else:
            self.timing_logs = []
            
            # 측정 데이터
            self.actual_display_times = []
            self.target_display_times = []
            self.display_intervals = []
            self.interval_delays = []
            self.pending_updates = {}
        
        self.start_time = 0
        self.render_check_count = 0
    
    def start_session(self):
        """디버깅 세션 시작"""
        if not RELEASE_MODE:
            self.clear_all_data()
            self.start_time = time.time()
            if self.enable_logs:
                print(f"\n[START] RandomPitchPlayer 세션 시작")
    
    def clear_all_data(self):
        """모든 측정 데이터 초기화"""
        if RELEASE_MODE:
            return  # 릴리즈 모드에서는 아무것도 하지 않음
            
        self.timing_logs.clear()
        self.actual_display_times.clear()
        self.target_display_times.clear()
        self.display_intervals.clear()
        self.interval_delays.clear()
        self.pending_updates.clear()
        self.render_check_count = 0
    
    def log_timing_event(self, event_type, expected_time=None, actual_time=None, sequence=None):
        """타이밍 이벤트 로그 기록"""
        if RELEASE_MODE or not self.debug_mode:
            return
            
        timestamp = time.time()
        log_entry = {
            'type': event_type,
            'timestamp': timestamp,
            'relative_time': timestamp - self.start_time if self.start_time else 0,
            'expected_time': expected_time,
            'actual_time': actual_time,
            'sequence': sequence
        }
        
        if expected_time and actual_time:
            log_entry['delay'] = actual_time - expected_time
            
        self.timing_logs.append(log_entry)
        
        # 로그가 너무 많이 쌓이지 않도록 제한
        if len(self.timing_logs) > MAX_TIMING_LOGS:
            self.timing_logs = self.timing_logs[-MAX_TIMING_LOGS//2:]
    
    def record_display_event(self, pitch_text, target_time, actual_render_time, current_interval):
        """실제 화면 출력 이벤트 기록"""
        if RELEASE_MODE:
            return  # 릴리즈 모드에서는 기록하지 않음
            
        self.actual_display_times.append(actual_render_time)
        self.target_display_times.append(target_time)
        
        # 이전 출력과의 간격 계산
        if len(self.actual_display_times) > 1:
            prev_time = self.actual_display_times[-2]
            actual_interval = actual_render_time - prev_time
            interval_delay = actual_interval - current_interval
            
            self.display_intervals.append(actual_interval)
            self.interval_delays.append(interval_delay)
            
            if self.enable_logs:
                print(f"[PLAY] {pitch_text} 음정출력 - 간격: {actual_interval:.3f}s, 목표: {current_interval:.3f}s, 지연: {interval_delay:.3f}s")
        else:
            if self.enable_logs:
                print(f"[PLAY] {pitch_text} 첫 출력")
    
    def add_pending_update(self, sequence, pitch, color, target_time):
        """대기 중인 업데이트 추가"""
        if RELEASE_MODE:
            return
            
        self.pending_updates[sequence] = {
            'pitch': pitch,
            'color': color,
            'target_time': target_time,
            'request_time': time.time()
        }
    
    def complete_pending_update(self, sequence):
        """대기 중인 업데이트 완료 처리"""
        if RELEASE_MODE or sequence not in self.pending_updates:
            return
            
        del self.pending_updates[sequence]
    
    def get_debug_summary(self):
        """디버그 요약 정보 반환"""
        if RELEASE_MODE:
            return ""
            
        if not self.interval_delays:
            return "지연: 0.000s | 평균: 0.000s | 대기중: 0"
        
        last_delay = self.interval_delays[-1]
        avg_delay = sum(self.interval_delays[-5:]) / min(5, len(self.interval_delays))
        pending_count = len(self.pending_updates)
        
        return f"지연: {last_delay:.3f}s | 평균: {avg_delay:.3f}s | 대기중: {pending_count}"
    
    def print_comprehensive_analysis(self, current_interval):
        """종합 성능 분석 결과 출력"""
        if RELEASE_MODE or not self.enable_performance:
            return
            
        print("\n=== RandomPitchPlayer 성능 분석 ===")
        print(f"총 음정 변경 횟수: {len(self.interval_delays)}")
        print(f"목표 간격: {current_interval:.3f}초")
        print(f"대기 중인 렌더링: {len(self.pending_updates)}개")
        
        if self.interval_delays:
            self._print_delay_analysis()
        
        if self.pending_updates:
            self._print_pending_updates()
        
        if self.display_intervals:
            self._print_interval_analysis()
        
        self._print_recent_details()
    
    def _print_delay_analysis(self):
        """지연 분석 출력"""
        if RELEASE_MODE:
            return
            
        avg_delay = sum(self.interval_delays) / len(self.interval_delays)
        max_delay = max(self.interval_delays)
        min_delay = min(self.interval_delays)
        
        delays_over_100ms = [d for d in self.interval_delays if d > 0.1]
        delays_over_500ms = [d for d in self.interval_delays if d > 0.5]
        delays_over_1s = [d for d in self.interval_delays if d > 1.0]
        
        print(f"\n[STATS] 실제 렌더링 기반 지연 분석:")
        print(f"  평균 지연: {avg_delay:.3f}초")
        print(f"  최대 지연: {max_delay:.3f}초")
        print(f"  최소 지연: {min_delay:.3f}초")
        print(f"  100ms 이상 지연: {len(delays_over_100ms)}회")
        print(f"  500ms 이상 지연: {len(delays_over_500ms)}회")
        print(f"  1초 이상 지연: {len(delays_over_1s)}회")
        
        if delays_over_500ms:
            print(f"  심각한 지연들: {[f'{d:.3f}s' for d in delays_over_500ms]}")
    
    def _print_pending_updates(self):
        """대기 중인 업데이트 정보 출력"""
        if RELEASE_MODE:
            return
            
        print(f"\n[WAIT] 현재 대기 중인 렌더링:")
        for seq, info in self.pending_updates.items():
            wait_time = time.time() - info['request_time']
            print(f"  순서 {seq}: {info['pitch']} (대기시간: {wait_time:.3f}s)")
    
    def _print_interval_analysis(self):
        """간격 분석 출력"""
        if RELEASE_MODE:
            return
            
        avg_interval = sum(self.display_intervals) / len(self.display_intervals)
        max_interval = max(self.display_intervals)
        min_interval = min(self.display_intervals)
        
        print(f"\n[TIME] 실제 출력 간격 분석:")
        print(f"  평균 실제 간격: {avg_interval:.3f}초")
        print(f"  최대 실제 간격: {max_interval:.3f}초")
        print(f"  최소 실제 간격: {min_interval:.3f}초")
    
    def _print_recent_details(self):
        """최근 간격들 상세 출력"""
        if RELEASE_MODE:
            return
            
        print(f"\n[LIST] 최근 10개 간격 상세:")
        recent_count = min(10, len(self.interval_delays))
        for i in range(recent_count):
            idx = len(self.interval_delays) - recent_count + i
            actual_interval = self.display_intervals[idx] if idx < len(self.display_intervals) else 0
            delay = self.interval_delays[idx]
            print(f"  {i+1:2d}. 실제간격: {actual_interval:.3f}s, 지연: {delay:.3f}s")