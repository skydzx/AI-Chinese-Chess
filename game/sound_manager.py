# game/sound_manager.py
import os
import pygame

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.enabled = True
        except:
            self.enabled = False

    def play_move(self):
        """播放落子声音"""
        pass  # 可添加音效文件

    def play_capture(self):
        """播放吃子声音"""
        pass

    def play_check(self):
        """播放将军声音"""
        pass
