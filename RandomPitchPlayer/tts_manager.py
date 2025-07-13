"""
RandomPitchPlayer TTS (Text-to-Speech) 관리자
gTTS와 pygame을 사용한 음정 음성 안내 기능
"""
import threading
import time
import tkinter as tk
import queue
import os
import tempfile
import io
from config import *

# gTTS 및 pygame 라이브러리 임포트
_tts_available = False
_pygame_available = False

try:
    from gtts import gTTS
    _tts_available = True
    
    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
        print("[TTS] gTTS 라이브러리 사용 가능")
        
except ImportError as e:
    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
        print(f"[TTS] gTTS 라이브러리 임포트 실패: {e}")
        print("[TTS] pip install gtts 로 설치하세요")

try:
    import pygame
    _pygame_available = True
    
    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
        print("[TTS] pygame 라이브러리 사용 가능")
        
except ImportError as e:
    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
        print(f"[TTS] pygame 라이브러리 임포트 실패: {e}")
        print("[TTS] pip install pygame 로 설치하세요")


class TTSManager:
    """RandomPitchPlayer TTS 기능을 관리하는 클래스 (gTTS + pygame 버전)"""
    
    def __init__(self, master=None):
        self.master = master  # tkinter 루트 위젯 참조
        self.tts_enabled = TTS_ENABLED and _tts_available and _pygame_available
        self.rate = TTS_RATE  # gTTS에서는 직접 사용하지 않지만 호환성 유지
        self.volume = TTS_VOLUME
        self.voice_index = TTS_VOICE_INDEX
        self.use_korean = TTS_LANGUAGE_KOREAN
        
        # 오디오 캐시 (음정별로 미리 생성된 오디오 파일)
        self.audio_cache = {}
        self.temp_dir = None
        
        # pygame mixer 관련
        self.mixer_initialized = False
        
        # 큐 기반 TTS 처리
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.tts_thread = None
        self.stop_event = threading.Event()
        
        self._initialize_tts()
        self._start_tts_worker()
    
    def set_master(self, master):
        """tkinter 마스터 설정 (늦은 초기화용)"""
        self.master = master
    
    def _initialize_tts(self):
        """TTS 시스템 초기화"""
        if not self.tts_enabled:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] TTS가 비활성화되어 있음")
            return
        
        try:
            # pygame mixer 초기화
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] pygame mixer 초기화 시작")
            
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.mixer_initialized = True
            
            # 볼륨 설정
            pygame.mixer.music.set_volume(self.volume)
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] pygame mixer 초기화 완료 - 볼륨: {self.volume}")
            
            # 임시 디렉토리 생성
            self.temp_dir = tempfile.mkdtemp(prefix="random_pitch_tts_")
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 임시 디렉토리 생성: {self.temp_dir}")
            
            # 음정별 오디오 파일 미리 생성
            self._pregenerate_audio_files()
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] gTTS 초기화 완료")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] TTS 초기화 실패: {e}")
                print(f"[TTS] 오류 타입: {type(e).__name__}")
                import traceback
                print(f"[TTS] 오류 상세: {traceback.format_exc()}")
            self.tts_enabled = False
    
    def _pregenerate_audio_files(self):
        """모든 음정에 대한 오디오 파일 미리 생성"""
        if not self.tts_enabled:
            return
        
        try:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] 음정별 오디오 파일 생성 시작")
            
            # 언어 설정
            lang = 'ko' if self.use_korean else 'en'
            
            # 각 음정에 대해 오디오 파일 생성
            for pitch in SCALES:
                try:
                    # 텍스트 가져오기
                    if self.use_korean:
                        text = TTS_PITCH_TEXTS.get(pitch, pitch)
                    else:
                        text = TTS_PITCH_TEXTS_EN.get(pitch, pitch)
                    
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] {pitch} 음정 오디오 생성 중: '{text}' (언어: {lang})")
                    
                    # gTTS로 음성 생성
                    tts = gTTS(text=text, lang=lang, slow=False)
                    
                    # 임시 파일에 저장
                    audio_path = os.path.join(self.temp_dir, f"pitch_{pitch}.mp3")
                    tts.save(audio_path)
                    
                    # 캐시에 저장
                    self.audio_cache[pitch] = audio_path
                    
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] {pitch} 음정 오디오 생성 완료: {audio_path}")
                    
                except Exception as e:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] {pitch} 음정 오디오 생성 실패: {e}")
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 총 {len(self.audio_cache)}개 음정 오디오 파일 생성 완료")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 오디오 파일 생성 중 오류: {e}")
    
    def _start_tts_worker(self):
        """TTS 워커 스레드 시작"""
        if not self.tts_enabled:
            return
        
        self.stop_event.clear()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print("[TTS] TTS 워커 스레드 시작")
            # 초기화 완료 후 TTS 테스트 실행 (별도 스레드)
            test_thread = threading.Thread(target=self._delayed_test, daemon=True)
            test_thread.start()
    
    def _delayed_test(self):
        """지연된 TTS 테스트"""
        time.sleep(1)  # 1초 대기
        self.test_tts()
    
    def _tts_worker(self):
        """TTS 워커 스레드 - 큐에서 순차적으로 TTS 처리"""
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print("[TTS] 워커 스레드 시작")
        
        # TTS 처리 루프
        while not self.stop_event.is_set():
            try:
                # 큐에서 TTS 요청 대기 (타임아웃 0.5초)
                speech_request = self.speech_queue.get(timeout=0.5)
                
                if speech_request is None:  # 종료 신호
                    break
                
                pitch, text = speech_request
                self.is_speaking = True
                
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] 음성 안내 시작: {pitch} -> '{text}'")
                
                # 캐시된 오디오 파일로 재생
                if pitch in self.audio_cache and self.mixer_initialized:
                    try:
                        audio_path = self.audio_cache[pitch]
                        
                        if os.path.exists(audio_path):
                            # pygame으로 오디오 재생
                            pygame.mixer.music.load(audio_path)
                            pygame.mixer.music.play()
                            
                            # 재생 완료까지 대기
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                            
                            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                                print(f"[TTS] 음성 안내 완료: {pitch} -> '{text}'")
                        else:
                            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                                print(f"[TTS] 오디오 파일이 존재하지 않음: {audio_path}")
                    
                    except Exception as e:
                        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                            print(f"[TTS] 음성 재생 오류: {e}")
                
                else:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] {pitch} 음정의 캐시된 오디오가 없거나 mixer가 초기화되지 않음")
                
                self.is_speaking = False
                
            except queue.Empty:
                # 타임아웃 - 계속 루프
                continue
            except Exception as e:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] 워커 스레드 오류: {e}")
                self.is_speaking = False
        
        if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
            print("[TTS] TTS 워커 스레드 종료")
    
    def speak_pitch_async(self, pitch):
        """음정을 비동기적으로 음성 안내 (논블로킹)"""
        if not self.tts_enabled:
            return
        
        try:
            # 음정에 해당하는 텍스트 가져오기
            if self.use_korean:
                text = TTS_PITCH_TEXTS.get(pitch, pitch)
            else:
                text = TTS_PITCH_TEXTS_EN.get(pitch, pitch)
            
            # 큐 크기 확인 (너무 많이 쌓이면 스킵)
            if self.speech_queue.qsize() > 5:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] 큐가 너무 많이 쌓임 (크기: {self.speech_queue.qsize()}), TTS 요청 스킵: {pitch}")
                return
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 비동기 음성 안내 요청: {pitch} -> '{text}' (큐 크기: {self.speech_queue.qsize()})")
                
            # 큐에 TTS 요청 추가
            self.speech_queue.put((pitch, text))
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 비동기 음성 안내 오류: {e}")
    
    def speak_pitch_sync_main_thread(self, pitch):
        """메인 스레드에서 동기적으로 음성 안내 (gTTS + pygame 버전)"""
        if not self.tts_enabled:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 메인 스레드 TTS 스킵 - enabled: {self.tts_enabled}")
            return
        
        try:
            # 음정에 해당하는 텍스트 가져오기
            if self.use_korean:
                text = TTS_PITCH_TEXTS.get(pitch, pitch)
            else:
                text = TTS_PITCH_TEXTS_EN.get(pitch, pitch)
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 메인 스레드 음성 안내 시작: {pitch} -> '{text}'")
            
            # 캐시된 오디오 파일로 즉시 재생
            if pitch in self.audio_cache and self.mixer_initialized:
                audio_path = self.audio_cache[pitch]
                
                if os.path.exists(audio_path):
                    # pygame으로 오디오 재생 (논블로킹)
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 메인 스레드 음성 안내 시작됨: {pitch}")
                else:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 오디오 파일이 존재하지 않음: {audio_path}")
            else:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] {pitch} 음정의 캐시된 오디오가 없거나 mixer가 초기화되지 않음")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 메인 스레드 음성 안내 오류: {e}")
                print(f"[TTS] 오류 타입: {type(e).__name__}")
                import traceback
                print(f"[TTS] 오류 상세: {traceback.format_exc()}")
    
    def stop_speech(self):
        """현재 음성 안내 정지"""
        if not self.tts_enabled:
            return
        
        try:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 음성 안내 정지 요청. 현재 상태: speaking={self.is_speaking}, queue_size={self.speech_queue.qsize()}")
            
            # 큐 비우기
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            
            # pygame 음악 정지
            if self.mixer_initialized:
                try:
                    pygame.mixer.music.stop()
                except Exception as e:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] pygame 음악 정지 중 오류: {e}")
            
            # 상태 리셋
            self.is_speaking = False
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] 음성 안내 정지 완료")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 음성 정지 오류: {e}")
            
            # 강제 상태 리셋
            self.is_speaking = False
    
    def speak_pitch_sync(self, pitch):
        """음정을 동기적으로 음성 안내 (블로킹) - gTTS 버전"""
        if not self.tts_enabled:
            return
        
        try:
            # 음정에 해당하는 텍스트 가져오기
            if self.use_korean:
                text = TTS_PITCH_TEXTS.get(pitch, pitch)
            else:
                text = TTS_PITCH_TEXTS_EN.get(pitch, pitch)
            
            # 캐시된 오디오 파일로 재생
            if pitch in self.audio_cache and self.mixer_initialized:
                audio_path = self.audio_cache[pitch]
                
                if os.path.exists(audio_path):
                    # pygame으로 오디오 재생 (블로킹)
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    # 재생 완료까지 대기
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 동기 음성 안내: {pitch} -> '{text}'")
                else:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 오디오 파일이 존재하지 않음: {audio_path}")
            else:
                if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                    print(f"[TTS] {pitch} 음정의 캐시된 오디오가 없습니다")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] 동기 음성 안내 오류: {e}")
    
    def _has_korean_voice(self):
        """한국어 음성 사용 가능 여부 확인 (gTTS는 항상 가능)"""
        return True
    
    def is_currently_speaking(self):
        """현재 음성 안내 중인지 반환"""
        # pygame 재생 상태도 확인
        has_queue = not self.speech_queue.empty()
        pygame_playing = False
        
        if self.mixer_initialized:
            try:
                pygame_playing = pygame.mixer.music.get_busy()
            except:
                pass
        
        return self.is_speaking or has_queue or pygame_playing
    
    def is_tts_available(self):
        """TTS 기능 사용 가능 여부 반환"""
        return self.tts_enabled
    
    def get_tts_status_info(self):
        """TTS 상태 정보 반환"""
        if not _tts_available:
            return "TTS: gTTS 라이브러리 없음"
        
        if not _pygame_available:
            return "TTS: pygame 라이브러리 없음"
        
        if not self.tts_enabled:
            return "TTS: 비활성화"
        
        if self.is_currently_speaking():
            lang_text = "한국어" if self.use_korean else "영어"
            return f"TTS: 음성 안내 중 (gTTS {lang_text})"
        else:
            lang_text = "한국어" if self.use_korean else "영어"
            return f"TTS: 대기 중 (gTTS {lang_text})"
    
    def test_tts(self):
        """TTS 기능 테스트"""
        if not self.tts_enabled:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] TTS가 비활성화되어 있습니다")
            return False
        
        try:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] TTS 테스트 시작")
            
            # 큐에 테스트 요청 추가
            test_text = "테스트" if self.use_korean else "Test"
            self.speech_queue.put(("TEST", test_text))
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] TTS 테스트 요청 완료")
            
            return True
            
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] TTS 테스트 실패: {e}")
            return False
    
    def cleanup(self):
        """TTS 리소스 정리"""
        try:
            # TTS 활동 정지
            self.tts_enabled = False
            self.stop_speech()
            
            # 워커 스레드 종료
            if self.tts_thread and self.tts_thread.is_alive():
                self.stop_event.set()
                self.speech_queue.put(None)  # 종료 신호
                self.tts_thread.join(timeout=2.0)
            
            # pygame mixer 정리
            if self.mixer_initialized:
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    self.mixer_initialized = False
                except Exception as mixer_error:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] pygame mixer 정리 중 오류 (무시됨): {mixer_error}")
            
            # 임시 파일들 정리
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    import shutil
                    shutil.rmtree(self.temp_dir)
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 임시 디렉토리 정리 완료: {self.temp_dir}")
                except Exception as temp_error:
                    if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                        print(f"[TTS] 임시 디렉토리 정리 오류 (무시됨): {temp_error}")
            
            # 모든 상태 리셋
            self.audio_cache.clear()
            self.is_speaking = False
            
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print("[TTS] TTS 리소스 정리 완료")
                
        except Exception as e:
            if ENABLE_CONSOLE_LOGS and not RELEASE_MODE:
                print(f"[TTS] TTS 리소스 정리 오류 (무시됨): {e}")


# 전역 TTS 매니저 인스턴스
_tts_manager_instance = None

def get_tts_manager():
    """TTS 매니저 싱글톤 인스턴스 반환"""
    global _tts_manager_instance
    if _tts_manager_instance is None:
        _tts_manager_instance = TTSManager()
    return _tts_manager_instance

def cleanup_tts_global():
    """전역 TTS 매니저 정리 (프로그램 종료 시 사용)"""
    global _tts_manager_instance
    if _tts_manager_instance is not None:
        try:
            _tts_manager_instance.cleanup()
            _tts_manager_instance = None
        except Exception as e:
            # 종료 시 모든 오류 무시
            pass

# 프로그램 종료 시 자동 정리를 위한 atexit 등록
import atexit
try:
    atexit.register(cleanup_tts_global)
except:
    # atexit 등록 실패 시 무시
    pass