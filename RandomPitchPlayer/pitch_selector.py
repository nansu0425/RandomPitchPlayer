"""
음정 선택 관리자 (Pitch Selector)
중복 방지 로직을 포함한 랜덤 음정 선택 담당
"""
import random
from config import SCALES


class PitchSelector:
    """음정 선택을 관리하는 클래스"""
    
    def __init__(self):
        self.pitches = SCALES.copy()
        self.last_selected_pitch = None
    
    def get_next_pitch(self):
        """중복을 방지하는 다음 음정 선택"""
        if self.last_selected_pitch is None:
            # 첫 번째 선택은 완전 랜덤
            selected = random.choice(self.pitches)
        else:
            # 이전 음정을 제외한 나머지에서 선택
            available_pitches = [pitch for pitch in self.pitches if pitch != self.last_selected_pitch]
            if not available_pitches:
                available_pitches = self.pitches.copy()
            selected = random.choice(available_pitches)
        
        self.last_selected_pitch = selected
        return selected
    
    def reset(self):
        """선택 상태 초기화"""
        self.last_selected_pitch = None


# 하위 호환성을 위한 별칭
ScaleSelector = PitchSelector