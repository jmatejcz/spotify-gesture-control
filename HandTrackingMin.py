import cv2
import mediapipe as mp 
import time

capture = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
recognition_draw = mp.solutions.drawing_utils

while True:
    success, img = capture.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    #print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks: #handLms -> single hand recognized
            recognition_draw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("cam_image", img)
    cv2.waitKey(1)