"""
RandomPitchPlayer UI 관리자
tkinter UI 생성, 관리, 렌더링 담당
"""
import tkinter as tk
import tkinter.font as tkFont
import time
import queue
from config import *
from timing_utils import TimingUtils


class UIManager:
    """RandomPitchPlayer UI 생성 및 관리를 담당하는 클래스"""
    
    def __init__(self, master, debug_manager):
        self.master = master
        self.debug_manager = debug_manager
        
        # UI 관련 변수들
        self.pitch_label = None  # scale_label -> pitch_label
        self.debug_label = None
        self.remaining_time_label = None  # 남은 시간 표시 레이블 추가
        self.power_status_label = None  # 전원 상태 표시 레이블 추가
        self.tts_status_label = None    # TTS 상태 표시 레이블 추가
        self.interval_entry = None
        self.bpm_entry = None
        self.duration_entry = None  # 지속 시간 입력 필드 추가
        self.mode_var = None  # 'seconds' 또는 'bpm'
        self.tempo_label = None
        self.start_button = None
        self.stop_button = None
        self.debug_button = None  # 디버그 버튼 추가
        
        # 폰트 관련 변수들
        self.main_font = None
        self.current_font_size = DEFAULT_FONT_SIZE
        self.last_window_size = (800, 600)
        self.font_update_needed = False
        
        # 렌더링 관련
        self.current_pitch_display_time = 0  # scale -> pitch
        
        self._setup_window()
        self._create_font()
        self._create_ui()
        self._setup_events()
    
    def _setup_window(self):
        """윈도우 초기 설정"""
        if RELEASE_MODE:
            self.master.title("RandomPitchPlayer - 랜덤 음정 플레이어")
        else:
            self.master.title("RandomPitchPlayer - 랜덤 음정 플레이어 (디버그 모드)")
        self.master.geometry(DEFAULT_WINDOW_SIZE)
        self.master.state('zoomed')  # Windows에서 최대화
    
    def _create_font(self):
        """폰트 객체 생성"""
        try:
            available_fonts = list(tkFont.families())
            font_family = "Arial"  # 기본값
            
            for font in KOREAN_FONTS:
                if font in available_fonts:
                    font_family = font
                    break
                    
            self.main_font = tkFont.Font(family=font_family, size=self.current_font_size, weight="bold")
        except:
            self.main_font = tkFont.Font(family="Arial", size=self.current_font_size, weight="bold")
    
    def _create_ui(self):
        """UI 요소들 생성"""
        # 음정 표시 레이블
        self.pitch_label = tk.Label(
            self.master, 
            text="준비", 
            font=self.main_font, 
            fg="black",
            anchor="center",
            justify="center",
            wraplength=0
        )
        self.pitch_label.pack(pady=30, expand=True)

        # 남은 시간 표시 레이블
        self.remaining_time_label = tk.Label(
            self.master,
            text="",  # 초기에는 비워둡니다.
            font=("Arial", 16, "bold"),
            fg="red"
        )
        self.remaining_time_label.pack(pady=5)

        # 디버그 정보 표시 레이블 (릴리즈 모드에서는 생성하지 않음)
        if ENABLE_DEBUG_UI and not RELEASE_MODE:
            self.debug_label = tk.Label(
                self.master,
                text="RandomPitchPlayer 디버그 정보",
                font=("Arial", 10),
                fg="gray"
            )
            self.debug_label.pack()

        # 전원 상태 표시 레이블 생성
        self._create_power_status()

        # TTS 상태 표시 레이블 생성
        self._create_tts_status()

        # 컨트롤 패널
        self._create_control_panel()
    
    def _create_control_panel(self):
        """컨트롤 패널 생성"""
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.BOTTOM, pady=20)

        # 모드 선택 (초 단위 vs BPM)
        self._create_mode_selection(control_frame)
        
        # 입력 필드들
        self._create_input_fields(control_frame)
        
        # 템포 설명
        self._create_tempo_info(control_frame)

        # 버튼들
        self._create_buttons(control_frame)
    
    def _create_mode_selection(self, parent):
        """모드 선택 라디오 버튼 생성"""
        mode_frame = tk.Frame(parent)
        mode_frame.pack(pady=5)
        
        tk.Label(mode_frame, text="타이밍 모드:", font=("Arial", 12, "bold")).pack()
        
        self.mode_var = tk.StringVar()
        self.mode_var.set("bpm" if BPM_MODE_ENABLED else "seconds")
        
        radio_frame = tk.Frame(mode_frame)
        radio_frame.pack(pady=5)
        
        tk.Radiobutton(
            radio_frame, 
            text="초 단위", 
            variable=self.mode_var, 
            value="seconds",
            font=("Arial", 11),
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            radio_frame, 
            text="BPM (메트로놈)", 
            variable=self.mode_var, 
            value="bpm",
            font=("Arial", 11),
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=10)
    
    def _create_input_fields(self, parent):
        """입력 필드들 생성"""
        input_frame = tk.Frame(parent)
        input_frame.pack(pady=10)
        
        # 첫 번째 행: 타이밍 설정
        timing_row = tk.Frame(input_frame)
        timing_row.pack(pady=5)
        
        # 초 단위 입력
        self.seconds_frame = tk.Frame(timing_row)
        tk.Label(self.seconds_frame, text="간격 (초):", font=("Arial", 12)).pack()
        self.interval_entry = tk.Entry(self.seconds_frame, font=("Arial", 12), width=10)
        self.interval_entry.insert(0, str(DEFAULT_INTERVAL))
        self.interval_entry.bind('<KeyRelease>', self._on_interval_change)
        self.interval_entry.pack()
        
        # BPM 입력
        self.bpm_frame = tk.Frame(timing_row)
        tk.Label(self.bpm_frame, text="BPM (분당 비트):", font=("Arial", 12)).pack()
        self.bpm_entry = tk.Entry(self.bpm_frame, font=("Arial", 12), width=10)
        self.bpm_entry.insert(0, str(DEFAULT_BPM))
        self.bpm_entry.bind('<KeyRelease>', self._on_bpm_change)
        self.bpm_entry.pack()
        
        # 두 번째 행: 지속 시간 설정
        duration_row = tk.Frame(input_frame)
        duration_row.pack(pady=5)
        
        # 지속 시간 입력
        duration_frame = tk.Frame(duration_row)
        duration_frame.pack()
        tk.Label(duration_frame, text="지속 시간 (분, 0=무제한):", font=("Arial", 12)).pack()
        self.duration_entry = tk.Entry(duration_frame, font=("Arial", 12), width=10)
        self.duration_entry.insert(0, str(DEFAULT_DURATION_MINUTES))
        self.duration_entry.bind('<KeyRelease>', self._on_duration_change)
        self.duration_entry.pack()
        
        # 세 번째 행: TTS 설정
        tts_row = tk.Frame(input_frame)
        tts_row.pack(pady=5)
        
        # TTS 활성화 체크박스
        tts_frame = tk.Frame(tts_row)
        tts_frame.pack()
        
        self.tts_enabled_var = tk.BooleanVar()
        self.tts_enabled_var.set(TTS_ENABLED)
        
        tts_checkbox = tk.Checkbutton(
            tts_frame,
            text="음성 안내 (TTS)",
            variable=self.tts_enabled_var,
            font=("Arial", 11),
            command=self._on_tts_toggle
        )
        tts_checkbox.pack()

        # 초기 모드에 따라 표시
        self._update_input_visibility()
    
    def _create_tempo_info(self, parent):
        """템포 정보 표시"""
        self.tempo_label = tk.Label(
            parent, 
            text="보통 (Moderato)",
            font=("Arial", 10),
            fg="blue"
        )
        self.tempo_label.pack(pady=5)
    
    def _create_buttons(self, parent):
        """버튼들 생성"""
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame, 
            text="시작", 
            font=("Arial", 12),
            width=8
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame, 
            text="정지", 
            state=tk.DISABLED, 
            font=("Arial", 12),
            width=8
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 디버그 버튼 (릴리즈 모드에서는 생성하지 안음)
        if ENABLE_DEBUG_UI and not RELEASE_MODE:
            self.debug_button = tk.Button(
                button_frame,
                text="로그출력",
                font=("Arial", 12),
                width=8
            )
            self.debug_button.pack(side=tk.LEFT, padx=5)
    
    def _setup_events(self):
        """이벤트 바인딩 설정"""
        self.master.bind('<Configure>', self._on_window_resize)
        self.master.focus_set()
    
    def _on_mode_change(self):
        """모드 변경 시 처리"""
        self._update_input_visibility()
        self._sync_values()
    
    def _on_interval_change(self, event=None):
        """초 간격 변경 시 BPM 동기화"""
        if self.mode_var.get() == "seconds":
            try:
                interval = float(self.interval_entry.get())
                bpm = TimingUtils.interval_to_bpm(interval)
                self.bpm_entry.delete(0, tk.END)
                self.bpm_entry.insert(0, str(bpm))
                self._update_tempo_info(bpm)
            except ValueError:
                pass
    
    def _on_bpm_change(self, event=None):
        """BPM 변경 시 초 간격 동기화"""
        if self.mode_var.get() == "bpm":
            try:
                bpm = float(self.bpm_entry.get())
                interval = TimingUtils.bpm_to_interval(bpm)
                self.interval_entry.delete(0, tk.END)
                self.interval_entry.insert(0, str(interval))
                self._update_tempo_info(bpm)
            except ValueError:
                pass
    
    def _on_duration_change(self, event=None):
        """지속 시간 변경 시 처리"""
        try:
            duration = float(self.duration_entry.get())
            # 범위 검증
            if duration < 0:
                duration = 0
            elif duration > MAX_DURATION_MINUTES:
                duration = MAX_DURATION_MINUTES
                self.duration_entry.delete(0, tk.END)
                self.duration_entry.insert(0, str(duration))
        except ValueError:
            pass
    
    def _on_tts_toggle(self):
        """TTS 활성화/비활성화 토글"""
        global TTS_ENABLED  # global 선언을 맨 앞으로 이동
        
        try:
            from tts_manager import get_tts_manager
            
            tts_manager = get_tts_manager()
            is_enabled = self.tts_enabled_var.get()
            
            # 전역 설정 업데이트 (런타임에서만)
            if hasattr(tts_manager, 'is_tts_available'):
                TTS_ENABLED = is_enabled and tts_manager.is_tts_available()
            else:
                TTS_ENABLED = is_enabled
            
            # 비활성화 시 현재 음성 정지
            if not is_enabled and hasattr(tts_manager, 'stop_speech'):
                tts_manager.stop_speech()
            
            self._update_tts_status()
            
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[UI] TTS 토글 오류: {e}")
            # 오류 발생 시 기본값으로 설정
            TTS_ENABLED = False
            self._update_tts_status()
    
    def _sync_values(self):
        """모드 변경 시 값 동기화"""
        if self.mode_var.get() == "bpm":
            self._on_bpm_change()
        else:
            self._on_interval_change()
    
    def _update_input_visibility(self):
        """입력 필드 표시/숨김 처리"""
        if self.mode_var.get() == "bpm":
            self.seconds_frame.pack_forget()
            self.bpm_frame.pack()
        else:
            self.bpm_frame.pack_forget()
            self.seconds_frame.pack()
    
    def _update_tempo_info(self, bpm):
        """템포 정보 업데이트"""
        try:
            description = TimingUtils.get_bpm_description(bpm)
            self.tempo_label.config(text=f"{bpm} BPM - {description}")
        except:
            self.tempo_label.config(text="BPM 정보")
    
    def set_button_commands(self, start_command, stop_command, debug_command=None):
        """버튼 명령어 설정"""
        self.start_button.config(command=start_command)
        self.stop_button.config(command=stop_command)
        # 디버그 버튼이 존재할 때만 명령어 설정
        if debug_command and self.debug_button and ENABLE_DEBUG_UI and not RELEASE_MODE:
            self.debug_button.config(command=debug_command)
    
    def get_interval_value(self):
        """간격 입력값 가져오기 (항상 초 단위로 반환)"""
        try:
            value = float(self.interval_entry.get())
            return max(MIN_INTERVAL, min(MAX_INTERVAL, value))
        except:
            return DEFAULT_INTERVAL
    
    def get_current_bpm(self):
        """현재 BPM 값 가져오기"""
        try:
            return float(self.bpm_entry.get())
        except:
            return DEFAULT_BPM
    
    def get_current_mode(self):
        """현재 입력 모드 반환"""
        return self.mode_var.get()
    
    def get_duration_minutes(self):
        """지속 시간 입력값 가져오기 (분 단위)"""
        try:
            value = float(self.duration_entry.get())
            return max(0, min(MAX_DURATION_MINUTES, value))
        except:
            return DEFAULT_DURATION_MINUTES
    
    def update_remaining_time(self, remaining_seconds):
        """남은 시간 표시 업데이트"""
        if remaining_seconds <= 0:
            self.remaining_time_label.config(text="")
            return
        
        # 분:초 형식으로 변환
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        if minutes > 0:
            time_text = f"남은 시간: {minutes}분 {seconds:02d}초"
        else:
            time_text = f"남은 시간: {seconds}초"
        
        # 10초 미만일 때 색상 변경
        if remaining_seconds < 10:
            self.remaining_time_label.config(text=time_text, fg="red")
        elif remaining_seconds < 30:
            self.remaining_time_label.config(text=time_text, fg="orange")
        else:
            self.remaining_time_label.config(text=time_text, fg="blue")
    
    def clear_remaining_time(self):
        """남은 시간 표시 지우기"""
        self.remaining_time_label.config(text="")
    
    def _create_power_status(self):
        """전원 상태 표시 생성"""
        self.power_status_label = tk.Label(
            self.master,
            text="",
            font=("Arial", 10),
            fg="green"
        )
        self.power_status_label.pack(pady=2)
        self._update_power_status()
    
    def _update_power_status(self):
        """전원 관리 상태 업데이트"""
        try:
            from power_manager import get_power_manager
            
            power_manager = get_power_manager()
            
            if not power_manager.is_power_management_available():
                self.power_status_label.config(text="💻 전원 관리: 사용 불가", fg="gray")
            elif power_manager.is_power_management_active():
                status_info = power_manager.get_power_status_info()
                self.power_status_label.config(text=f"🛡️ {status_info}", fg="green")
            else:
                if PREVENT_SLEEP_MODE or PREVENT_SCREEN_SAVER or KEEP_DISPLAY_ON:
                    self.power_status_label.config(text="😴 전원 관리: 대기 중", fg="orange")
                else:
                    self.power_status_label.config(text="💻 전원 관리: 비활성화", fg="gray")
                    
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[UI] 전원 상태 업데이트 오류: {e}")
            self.power_status_label.config(text="💻 전원 관리: 오류", fg="red")
    
    def update_power_status_display(self):
        """전원 상태 표시 업데이트 (외부 호출용)"""
        self._update_power_status()
    
    def update_pitch_display(self, pitch_text, color):
        """음정 화면 업데이트"""
        self.pitch_label.config(text=pitch_text, fg=color)
        self.master.update_idletasks()  # 강제 렌더링 시도
        
        # 실제 출력 시간 기록
        actual_time = time.time()
        self.current_pitch_display_time = actual_time
        return actual_time
    
    def update_debug_info(self, debug_text):
        """디버그 정보 업데이트 (릴리즈 모드에서는 아무것도 하지 않음)"""
        if RELEASE_MODE or not ENABLE_DEBUG_UI or not self.debug_label:
            return
            
        # BPM 정보도 포함하여 표시
        bpm_info = f" | BPM: {self.get_current_bpm():.1f}"
        self.debug_label.config(text=debug_text + bpm_info)
    
    def check_rendering_completion(self, expected_text):
        """렌더링 완료 여부 확인"""
        try:
            current_displayed_text = self.pitch_label.cget('text')
            return current_displayed_text == expected_text
        except:
            return False
    
    def set_button_states(self, start_enabled, stop_enabled):
        """버튼 상태 설정"""
        start_state = tk.NORMAL if start_enabled else tk.DISABLED
        stop_state = tk.NORMAL if stop_enabled else tk.DISABLED
        
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)
    
    def set_display_text(self, text, color="black"):
        """화면 텍스트 설정"""
        self.pitch_label.config(text=text, fg=color)
    
    def _on_window_resize(self, event):
        """윈도우 크기 변경 이벤트 처리"""
        if event.widget != self.master:
            return
            
        # 크기 변경이 유의미할 때만 처리
        new_size = (self.master.winfo_width(), self.master.winfo_height())
        if (abs(new_size[0] - self.last_window_size[0]) > RESIZE_THRESHOLD or 
            abs(new_size[1] - self.last_window_size[1]) > RESIZE_THRESHOLD):
            
            self.last_window_size = new_size
            self.font_update_needed = True
            # 지연된 폰트 업데이트 (디바운싱)
            self.master.after(FONT_UPDATE_DELAY_MS, self._update_font_if_needed)
    
    def _update_font_if_needed(self):
        """필요한 경우에만 폰트 크기 업데이트"""
        if not self.font_update_needed:
            return
            
        self.font_update_needed = False
        
        try:
            width, height = self.last_window_size
            new_font_size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, int(min(width, height) * FONT_SCALE_FACTOR)))
            
            if abs(new_font_size - self.current_font_size) > FONT_SIZE_CHANGE_THRESHOLD:
                self.current_font_size = new_font_size
                self.main_font.configure(size=new_font_size)
        except:
            pass

    # 하위 호환성을 위한 별칭들
    def update_scale_display(self, scale_text, color):
        """하위 호환성을 위한 별칭"""
        return self.update_pitch_display(scale_text, color)
    
    def _create_tts_status(self):
        """TTS 상태 표시 생성"""
        self.tts_status_label = tk.Label(
            self.master,
            text="",
            font=("Arial", 10),
            fg="blue"
        )
        self.tts_status_label.pack(pady=2)
        self._update_tts_status()
    
    def _update_tts_status(self):
        """TTS 상태 업데이트"""
        try:
            from tts_manager import get_tts_manager
            
            tts_manager = get_tts_manager()
            
            # 안전한 메서드 호출 확인
            if not hasattr(tts_manager, 'is_tts_available') or not tts_manager.is_tts_available():
                self.tts_status_label.config(text="🔇 TTS: 사용 불가", fg="gray")
            elif TTS_ENABLED:
                if hasattr(tts_manager, 'get_tts_status_info'):
                    status_info = tts_manager.get_tts_status_info()
                else:
                    status_info = "TTS: 상태 불명"
                
                if hasattr(tts_manager, 'is_currently_speaking') and tts_manager.is_currently_speaking():
                    self.tts_status_label.config(text=f"🗣️ {status_info}", fg="green")
                else:
                    self.tts_status_label.config(text=f"🎤 {status_info}", fg="blue")
            else:
                self.tts_status_label.config(text="🔇 TTS: 비활성화", fg="gray")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[UI] TTS 상태 업데이트 오류: {e}")
            self.tts_status_label.config(text="🔇 TTS: 오류", fg="red")
    
    def update_tts_status_display(self):
        """TTS 상태 표시 업데이트 (외부 호출용)"""
        self._update_tts_status()
    
    def get_tts_enabled(self):
        """TTS 활성화 상태 반환"""
        return self.tts_enabled_var.get() if hasattr(self, 'tts_enabled_var') else TTS_ENABLED