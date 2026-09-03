# JARVIS — Personal AI Computer Assistant

A voice, text, and gesture-controlled personal AI assistant for Windows, built with Python and local AI (Ollama).

## Features

- 🎤 **Voice control** — speech-to-text (Google Speech Recognition) + text-to-speech (pyttsx3)
- 🧠 **Local AI chat** — powered by Ollama (phi3:mini), runs fully offline, no paid API
- 💻 **Computer control** — open apps (Chrome, Notepad), take screenshots
- 🌐 **Browser automation** — search YouTube by voice command
- 🧩 **Memory system** — remembers user info (e.g. name) using SQLite, persists across sessions
- 📧 **Email integration** — check unread Gmail via IMAP
- ✋ **Hand gesture control** — webcam-based gesture recognition (MediaPipe + OpenCV) for cursor movement, click, and play/pause — runs in a background thread alongside voice

## Tech Stack

- **Language:** Python
- **AI:** Ollama (local LLM)
- **Voice:** SpeechRecognition, pyttsx3
- **Computer Vision:** OpenCV, MediaPipe
- **Automation:** PyAutoGUI
- **Browser:** webbrowser module
- **Email:** IMAPClient, pyzmail36
- **Storage:** SQLite

## How It Works

```
Voice/Text Input → Command Parsing → Intent Match
        ↓
   [Known command] → Direct Action (open app / screenshot / email / youtube)
   [Unknown command] → Local AI (Ollama) → Natural language response
        ↓
   Text-to-Speech Output

(Parallel thread)
Webcam → MediaPipe Hand Tracking → Gesture Detection → Cursor/Click/Media control
```

## Setup

1. Install Python 3.11
2. Create virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```
   pip install speechrecognition pyttsx3 pyaudio ollama pyautogui opencv-python mediapipe==0.10.14 imapclient pyzmail36
   ```
4. Install [Ollama](https://ollama.com) and pull a model:
   ```
   ollama pull phi3:mini
   ```
5. Set your Gmail App Password in `main.py` (`EMAIL` and `APP_PASSWORD` variables)
6. Run:
   ```
   python main.py
   ```

## Roadmap / Future Improvements

- More accurate gesture recognition (angle-based, not just finger count)
- Wake-word detection ("Hey Jarvis") instead of always-listening
- Automation/scheduling (e.g. daily email summary)
- GUI dashboard instead of console output

## Note

This is a learning project built incrementally to explore AI integration, computer vision, and automation in Python. Built as part of self-learning toward backend + AI development.
