# game/sound_manager.py
import os
import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            print(f"Sound initialization failed: {e}")

    def _generate_sounds(self):
        """程序生成音效"""
        # 落子声音 - 短促的click声
        self.move_sound = self._create_click_sound(frequency=800, duration=0.05)

        # 吃子声音 - 较沉的click声
        self.capture_sound = self._create_click_sound(frequency=400, duration=0.08)

        # 将军声音 - 较长的提示音
        self.check_sound = self._create_alert_sound()

    def _create_click_sound(self, frequency, duration):
        """创建click音效"""
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        # 添加包络使声音短促
        envelope = np.exp(-t * 30)
        wave = envelope * np.sin(2 * np.pi * frequency * t)
        # 转换为16位整数
        sound_data = (wave * 32767).astype(np.int16)
        # 立体声
        stereo = np.column_stack((sound_data, sound_data))
        return pygame.sndarray.make_sound(stereo)

    def _create_alert_sound(self):
        """创建将军提示音"""
        sample_rate = 22050
        duration = 0.15
        t = np.linspace(0, duration, int(sample_rate * duration))
        # 频率扫描
        frequency = 600 + 200 * t / duration
        wave = np.sin(2 * np.pi * frequency * t)
        envelope = np.exp(-t * 5)
        wave = envelope * wave
        sound_data = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((sound_data, sound_data))
        return pygame.sndarray.make_sound(stereo)

    def play_move(self):
        """播放落子声音"""
        if self.enabled:
            self.move_sound.play()

    def play_capture(self):
        """播放吃子声音"""
        if self.enabled:
            self.capture_sound.play()

    def play_check(self):
        """播放将军声音"""
        if self.enabled:
            self.check_sound.play()
