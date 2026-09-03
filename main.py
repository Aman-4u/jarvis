import os
import threading
import time
import math
import pyautogui
import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import sqlite3
import cv2
import mediapipe as mp
from imapclient import IMAPClient
import pyzmail

engine = pyttsx3.init()

EMAIL = "amanpateljml06@gmail.com"
APP_PASSWORD = "bvvpurkhmateorf"

# ---------- MEMORY ----------
def init_memory():
    conn = sqlite3.connect("data/memory.db")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

def save_memory(key, value):
    conn = sqlite3.connect("data/memory.db")
    conn.cursor().execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_memory(key):
    conn = sqlite3.connect("data/memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def forget_memory(key):
    conn = sqlite3.connect("data/memory.db")
    conn.cursor().execute("DELETE FROM memory WHERE key = ?", (key,))
    conn.commit()
    conn.close()

# ---------- VOICE ----------
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio).lower()
    except:
        return ""

def chat_with_ai(command):
    response = ollama.chat(model="phi3:mini", messages=[{"role": "user", "content": command}])
    return response["message"]["content"]

def open_youtube_search(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

def check_emails():
    try:
        server = IMAPClient("imap.gmail.com", ssl=True)
        server.login(EMAIL, APP_PASSWORD)
        server.select_folder("INBOX")
        messages = server.search(["UNSEEN"])
        count = len(messages)
        if count == 0:
            server.logout()
            return "Koi naya unread email nahi hai."
        latest = messages[-3:]
        subjects = []
        for uid in latest:
            raw = server.fetch([uid], ["BODY[]"])
            msg = pyzmail.PyzMessage.factory(raw[uid][b"BODY[]"])
            subjects.append(msg.get_subject())
        server.logout()
        return f"Tumhare {count} unread emails hain. Recent subjects: {', '.join(subjects)}"
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return "Email check karne me error aaya."

def handle_command(command):
    if "chrome" in command:
        os.startfile("chrome")
        return "Chrome khol raha hoon."
    elif "notepad" in command:
        os.startfile("notepad")
        return "Notepad khol raha hoon."
    elif "screenshot" in command:
        pyautogui.screenshot("screenshot.png")
        return "Screenshot le liya."
    elif "mera naam kya hai" in command:
        name = get_memory("user_name")
        return f"Tumhara naam {name} hai." if name else "Mujhe abhi tumhara naam pata nahi hai."
    elif "mera naam" in command and "hai" in command:
        name = command.replace("mera naam", "").replace("hai", "").strip()
        save_memory("user_name", name)
        return f"Theek hai, main yaad rakhunga tumhara naam {name} hai."
    elif "forget my name" in command or "naam bhool jao" in command:
        forget_memory("user_name")
        return "Theek hai, naam bhula diya."
    elif "email" in command and ("check" in command or "kitne" in command):
        return check_emails()
    elif "youtube" in command and "search" in command:
        words_to_remove = ["youtube", "per", "pe", "search", "karo", "kar do", "on"]
        query = command
        for word in words_to_remove:
            query = query.replace(word, "")
        query = query.strip()
        open_youtube_search(query)
        return f"YouTube pe {query} search kar raha hoon."
    elif "exit" in command or "band karo" in command:
        return "exit"
    else:
        return chat_with_ai(command)

def voice_loop():
    speak("Jarvis ready hai.")
    while True:
        command = listen()
        if command == "":
            continue
        print(f"You said: {command}")
        response = handle_command(command)
        if response == "exit":
            speak("Bye bye!")
            os._exit(0)
        speak(response)

# ---------- GESTURES ----------
def gesture_loop():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    screen_w, screen_h = pyautogui.size()
    last_action_time = 0
    cooldown = 1.5
    frame_count = 0

    def count_fingers(lm):
        tips = [4, 8, 12, 16, 20]
        fingers = [1 if lm[tips[0]].x < lm[tips[0]-1].x else 0]
        for tip in tips[1:]:
            fingers.append(1 if lm[tip].y < lm[tip-2].y else 0)
        return fingers

    while True:
        success, img = cap.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        frame_count += 1

        if frame_count % 2 != 0:
            cv2.imshow("JARVIS Gesture Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark
                fingers = count_fingers(lm)
                total = sum(fingers)
                current_time = time.time()

                index_tip = lm[8]
                thumb_tip = lm[4]
                cursor_x = int(index_tip.x * screen_w)
                cursor_y = int(index_tip.y * screen_h)
                distance = math.hypot((thumb_tip.x - index_tip.x) * w, (thumb_tip.y - index_tip.y) * h)

                if total == 1 and fingers[1] == 1:
                    pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)

                if distance < 30 and current_time - last_action_time > cooldown:
                    pyautogui.click()
                    last_action_time = current_time
                    cv2.putText(img, "CLICK", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                if total == 5 and current_time - last_action_time > cooldown:
                    pyautogui.press("space")
                    last_action_time = current_time
                    cv2.putText(img, "PLAY/PAUSE", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                cv2.putText(img, f"Fingers: {total}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

        cv2.imshow("JARVIS Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------- MAIN ----------
if __name__ == "__main__":
    init_memory()
    gesture_thread = threading.Thread(target=gesture_loop, daemon=True)
    gesture_thread.start()
    voice_loop()