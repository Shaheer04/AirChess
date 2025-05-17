import mediapipe as mp
import math

mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.7,
                      min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

PINCH_THRESHOLD = 0.1

def detect_hands(image_rgb):
    return hands.process(image_rgb)

def draw_landmarks(image, results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style())

def is_pinching(hand_landmarks, width, height):
    if hand_landmarks and hand_landmarks.landmark:
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        distance = math.sqrt((thumb_tip.x - index_finger_tip.x)**2 + (thumb_tip.y - index_finger_tip.y)**2)
        pinch_point_x = int((thumb_tip.x + index_finger_tip.x) / 2 * width)
        pinch_point_y = int((thumb_tip.y + index_finger_tip.y) / 2 * height)
        return distance < PINCH_THRESHOLD, (pinch_point_x, pinch_point_y)
    return False, None

def close_hands():
    hands.close()   