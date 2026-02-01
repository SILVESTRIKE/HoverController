# -*- coding: utf-8 -*-
import os
import json
import queue
import threading
import time
import pyaudio
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH, MIC_RATE, VOICE_COMMANDS


class VoiceEngine:
    """
    Offline voice recognition engine using Vosk.
    Runs on a separate thread to avoid blocking camera loop.
    """
    def __init__(self):
        self.model_path = VOSK_MODEL_PATH
        self.q = queue.Queue()
        self.running = False
        self.thread = None
        self.model = None
        self.is_mute = True  # Start muted (NAVIGATION mode)
        self.last_text = ""
        
    def initialize(self):
        """Load the Vosk model."""
        if not os.path.exists(self.model_path):
            print(f"ERROR: Vosk model not found at {self.model_path}")
            print("Please download from https://alphacephei.com/vosk/models")
            return False
            
        print("Loading Voice Model... (This may take a moment)")
        try:
            self.model = Model(self.model_path)
            print("Voice Model Loaded.")
            return True
        except Exception as e:
            print(f"Failed to load voice model: {e}")
            return False

    def start(self):
        """Start the audio processing thread."""
        if not self.model:
            if not self.initialize():
                return False
        
        self.running = True
        self.thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.thread.start()
        return True
        
    def stop(self):
        """Stop the audio processing thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def set_mute(self, mute):
        """Set mute state. When muted, voice input is ignored."""
        self.is_mute = mute
        if mute:
            # Clear any pending commands
            with self.q.mutex:
                self.q.queue.clear()

    def _audio_loop(self):
        """Main audio processing loop (runs on separate thread)."""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=MIC_RATE,
                input=True,
                frames_per_buffer=8000
            )
            stream.start_stream()
            
            rec = KaldiRecognizer(self.model, MIC_RATE)
            
            while self.running:
                if self.is_mute:
                    time.sleep(0.1)
                    # Flush stream to avoid backup
                    if stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                    continue
                    
                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    break
                    
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get("text", "").strip()
                    if text:
                        self.last_text = text
                        parsed = self._parse_command(text)
                        self.q.put(parsed)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Voice engine error: {e}")

    def _parse_command(self, text):
        """
        Parse recognized text into command or text input.
        Returns: {"type": "command"|"text", "action": str, "value": str}
        """
        text_lower = text.lower().strip()
        
        # Check against command keywords
        for action, keywords in VOICE_COMMANDS.items():
            if text_lower in keywords:
                return {"type": "command", "action": action, "value": text}
        
        # Not a command, treat as text to type
        return {"type": "text", "action": "type", "value": text}

    def get_command(self):
        """Non-blocking get command from queue."""
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None

    def get_last_text(self):
        """Get the last recognized text for display."""
        return self.last_text
