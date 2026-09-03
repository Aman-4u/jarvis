import cv2
import mediapipe as mp
import pyautogui
import time
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
last_action_time = 0
cooldown = 1.5

def count_fingers(lm):
    tips = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(1 if lm[tips[0]].x < lm[tips[0]-1].x else 0)
    for tip in tips[1:]:
        fingers.append(1 if lm[tip].y < lm[tip-2].y else 0)
    return fingers

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
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
                cv2.putText(img, "CLICK", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

            if total == 5 and current_time - last_action_time > cooldown:
                pyautogui.press("space")
                last_action_time = current_time
                cv2.putText(img, "PLAY/PAUSE", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

            cv2.putText(img, f"Fingers: {total}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)

    cv2.imshow("JARVIS Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()