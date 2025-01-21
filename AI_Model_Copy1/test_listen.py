import whisper
import sounddevice as sd
import numpy as np
import queue
import threading
import time
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import re
import webbrowser
import os
import random
import pyjokes
import ctypes
import time
import threading
import subprocess
from wikipedia.exceptions import DisambiguationError
from ssid_functions import *
from utils import *
from youtube_mc import remote_ips, ips
# from shared import *
import logging
import requests

# Initialize Whisper model
model = whisper.load_model("base")  # You can replace "base" with other model sizes like "small", "medium", "large"

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, flush=True)
    q.put(indata.copy())

def record_audio():
    """Function to capture live audio input."""
    samplerate = 48000
    device_id = 9  # Adjust if necessary

    print("Listening for commands...")

    try:
        with sd.InputStream(samplerate=samplerate, device=device_id, channels=1, callback=audio_callback):
            while True:
                audio_data = q.get()
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
                yield audio_array
    except Exception as e:
        print(f"Error opening stream: {e}")


def transcribe_audio():
    """Transcribe live audio using Whisper."""
    audio_generator = record_audio()
    audio_chunks = []
    chunk_duration = 2  # Transcribe every 2 seconds of audio

    for chunk in audio_generator:
        audio_chunks.append(chunk)
        if len(audio_chunks) * chunk_duration >= chunk_duration:
            audio = np.concatenate(audio_chunks, axis=0)
            audio_chunks = []  # Reset the chunks after transcription
            # Perform Whisper transcription
            result = model.transcribe(audio, fp16=False)  # Disable fp16 if you're running on CPU
            command = result['text'].strip()
            print(f"Recognized Command: {command}")
            execute_command(command)

# Example function for handling different voice commands
def execute_command(command):
    global is_executing_command
    is_executing_command = True
    print("The command is", command)

    if 'wikipedia' in command:
        search_term = command.replace("wikipedia", "").strip()
        try:
            # Fetch summary from Wikipedia
            results = wikipedia.summary(search_term, sentences=3)
            speak(f"According to Wikipedia, {results}")
            print(results)

        except DisambiguationError as e:
            # Handle disambiguation error
            speak("The term you searched for is ambiguous. Here are some options:")
            print("Disambiguation options:")
            options = e.options[:5]  # Show first 5 disambiguation options
            for option in options:
                print(option)
                speak(option)
            speak("Please be more specific in your search term.")
    elif 'open google' in command:
        speak("Opening Google...")
        webbrowser.open("google.com")
    else:
        speak("I'm not yet coded to answer your query")

    # Other commands as defined previously...
    # Add more command logic here based on your needs.

def speak(text):
    """Text-to-speech function (you can integrate your own TTS method)."""
    print(text)
    # Add a TTS method if needed

# Run the transcription and command execution in a separate thread
def start_listening():
    listening_thread = threading.Thread(target=transcribe_audio)
    listening_thread.start()

if __name__ == "__main__":
    start_listening()
