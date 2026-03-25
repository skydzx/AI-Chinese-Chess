# game/sound_manager.py
"""音效管理器 - 暂时禁用以避免与Qt冲突"""

class SoundManager:
    def __init__(self):
        # 暂时禁用音效，避免pygame与Qt冲突
        self.enabled = False

    def play_move(self):
        """播放落子声音"""
        pass

    def play_capture(self):
        """播放吃子声音"""
        pass

    def play_check(self):
        """播放将军声音"""
        pass
