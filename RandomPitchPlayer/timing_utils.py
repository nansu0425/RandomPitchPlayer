"""
RandomPitchPlayer BPM 및 타이밍 유틸리티
BPM과 초 간격 간의 변환 및 관리
"""
from config import DEFAULT_BPM, MIN_BPM, MAX_BPM, DEFAULT_INTERVAL, MIN_INTERVAL, MAX_INTERVAL


class TimingUtils:
    """RandomPitchPlayer BPM과 초 간격 변환을 담당하는 유틸리티 클래스"""
    
    @staticmethod
    def bpm_to_interval(bpm):
        """BPM을 초 간격으로 변환"""
        try:
            bpm = max(MIN_BPM, min(MAX_BPM, float(bpm)))
            interval = 60.0 / bpm  # 1분(60초) / BPM = 초당 간격
            return round(interval, 3)
        except (ValueError, ZeroDivisionError):
            return DEFAULT_INTERVAL
    
    @staticmethod
    def interval_to_bpm(interval):
        """초 간격을 BPM으로 변환"""
        try:
            interval = max(MIN_INTERVAL, min(MAX_INTERVAL, float(interval)))
            bpm = 60.0 / interval  # 60초 / 간격 = BPM
            return round(bpm, 1)
        except (ValueError, ZeroDivisionError):
            return DEFAULT_BPM
    
    @staticmethod
    def validate_bpm(bpm_value):
        """BPM 값 유효성 검사"""
        try:
            bpm = float(bpm_value)
            return MIN_BPM <= bpm <= MAX_BPM
        except ValueError:
            return False
    
    @staticmethod
    def validate_interval(interval_value):
        """초 간격 값 유효성 검사"""
        try:
            interval = float(interval_value)
            return MIN_INTERVAL <= interval <= MAX_INTERVAL
        except ValueError:
            return False
    
    @staticmethod
    def get_bpm_description(bpm):
        """BPM에 따른 템포 설명 반환 (음악적 템포 표기법)"""
        if bpm < 60:
            return "매우 느림 (Largo)"
        elif bpm < 80:
            return "느림 (Adagio)"
        elif bpm < 100:
            return "보통 (Moderato)"
        elif bpm < 120:
            return "조금 빠름 (Allegretto)"
        elif bpm < 160:
            return "빠름 (Allegro)"
        elif bpm < 200:
            return "매우 빠름 (Presto)"
        else:
            return "극도로 빠름 (Prestissimo)"