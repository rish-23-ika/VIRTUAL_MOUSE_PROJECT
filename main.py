import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_width, screen_height = pyautogui.size()

# Initialize webcam
cap = cv2.VideoCapture(0)

# Variables for drag and scroll
dragging = False
prev_y = None
scroll_threshold = 20
click_cooldown = 0.3
last_click_time = 0

# Visual indicator variables
click_indicator = False
click_indicator_time = 0
indicator_duration = 0.2  # seconds

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        current_time = time.time()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get coordinates of relevant landmarks
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                middle_tip = hand_landmarks.landmark[12]

                # Convert to pixel coordinates
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                mx, my = int(middle_tip.x * w), int(middle_tip.y * h)

                # Move mouse with index finger
                screen_x = screen_width * index_tip.x
                screen_y = screen_height * index_tip.y
                pyautogui.moveTo(screen_x, screen_y, duration=0.01)

                # Calculate distances
                pinch_distance = math.hypot(tx - ix, ty - iy)
                right_click_distance = math.hypot(tx - mx, ty - my)
                drag_distance = math.hypot(ix - mx, iy - my)

                # Left click gesture (thumb + index)
                if pinch_distance < 40 and current_time - last_click_time > click_cooldown:
                    pyautogui.click()
                    last_click_time = current_time
                    click_indicator = True
                    click_indicator_time = current_time

                # Right click gesture (thumb + middle)
                elif right_click_distance < 40 and current_time - last_click_time > click_cooldown:
                    pyautogui.click(button='right')
                    last_click_time = current_time

                # Drag gesture (index + middle)
                if drag_distance < 40:
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                else:
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False

                # Scroll gesture (vertical movement)
                if prev_y is not None:
                    dy = iy - prev_y
                    if abs(dy) > scroll_threshold:
                        pyautogui.scroll(-int(dy))
                prev_y = iy

                # Draw visual indicator if click was detected recently
                if click_indicator and current_time - click_indicator_time < indicator_duration:
                    cv2.circle(frame, (ix, iy), 20, (0, 255, 0), -1)  # Green circle
                    cv2.putText(frame, "Click!", (ix + 30, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    click_indicator = False

        cv2.imshow("Virtual Mouse", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()

# Dummy loop to fix the indentation error
for ex in range(1):
    print("Virtual Mouse script executed successfully.")
