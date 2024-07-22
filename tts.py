from gtts import gTTS
import pygame
import os
import threading
import time

class TTS:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.current_audio_file = None
        self.playback_thread = None

    def text_to_speech(self, text, audio_file):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(audio_file)
            self.current_audio_file = audio_file
            print(f"Audio file created: {audio_file}")
        except Exception as e:
            print(f"An error occurred while creating audio file: {e}")

    def _play_audio_thread(self, audio_file):
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            self.is_playing = False
        except Exception as e:
            print(f"An error occurred while playing audio: {e}")
            self.is_playing = False

    def play_audio(self, audio_file):
        if self.is_playing:
            self.stop_audio()
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()  # Wait for any existing playback to finish
        
        self.playback_thread = threading.Thread(target=self._play_audio_thread, args=(audio_file,))
        self.playback_thread.start()

    def stop_audio(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                pygame.mixer.music.unload()
                print(f"Audio file stopped: {self.current_audio_file}")
            except Exception as e:
                print(f"An error occurred while stopping audio: {e}")

    def cleanup(self):
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.remove(self.current_audio_file)
                print(f"Deleted audio file: {self.current_audio_file}")
            except PermissionError:
                print(f"Could not delete {self.current_audio_file}. It may still be in use.")
            self.current_audio_file = None
