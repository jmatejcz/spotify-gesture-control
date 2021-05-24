import cv2
import mediapipe as mp
import time
import math
import time
import socket, pickle, struct
import threading


class handDetector():
    def __init__(self, mode=False, maxHands=2, detection_confidence=0.5, tracking_confidence=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detection_confidence, self.tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils
        self.waiting_time = -1
        self.waiting_for = None

        self.gestures = {
            "starting_position": 0,
            "snap": 1,
            "gap_between_pointer_and_thumb": 2,
            "swing": 3,
            "swing_left": 4,
            "swing_right": 5
        }

    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:  # handLms -> single hand recognized
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def find_lm_positions(self, img, which_hand=0):
        lm_list = []
        try:
            if self.results.multi_hand_landmarks:
                if self.results.multi_hand_landmarks[which_hand]:
                    chosen_hand = self.results.multi_hand_landmarks[which_hand]
                    for nr, lm in enumerate(chosen_hand.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lm_list.append([nr, cx, cy])
        except:
            pass

        return lm_list

    # returns list of distance between certain landmarks
    def lengths_between(self, list_of_coords):
        distance_list = []
        for nr, x, y in list_of_coords:
            pass

    def find_gesture_pre_swing(self, lm_list):
        # all fingers are straight
        # and hand is more or less in the middle 
        len5_8 = math.hypot(lm_list[5][1] - lm_list[8][1], lm_list[5][2] - lm_list[8][2])
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        len1_4 = math.hypot(lm_list[1][1] - lm_list[4][1], lm_list[1][2] - lm_list[4][2])
        if len1_4 > 70 and len5_8 > 70 and len9_12 > 75 and len13_16 > 70 and len17_20 > 50 \
                and len1_4 < 120 and len5_8 < 110 and len9_12 < 120 and len13_16 < 110 and len17_20 < 90 \
                and lm_list[0][1] > 245 and lm_list[0][1] < 395:
            return True
        # print(len1_4, len5_8, len9_12, len13_16, len17_20)

    def find_gesture_pre_snap(self, lm_list):
        # distance beetween middle finger tip and thumb tip
        length_between = math.hypot(lm_list[4][1] - lm_list[12][1], lm_list[4][2] - lm_list[12][2])
        # print(length_between)
        if length_between < 20:
            return True

    def find_gesture_post_snap(self, lm_list):
        # distance beetween middle finger tip and thumb tip
        length_between = math.hypot(lm_list[4][1] - lm_list[12][1], lm_list[4][2] - lm_list[12][2])
        # print(length_between)
        if length_between > 45:
            return True

    def find_gesture_pre_pt_distance(self, lm_list):
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        len4_8 = math.hypot(lm_list[4][1] - lm_list[8][1], lm_list[4][2] - lm_list[8][2])
        if len9_12 > 80 and len13_16 > 80 and len17_20 > 80 and len4_8 < 15:
            return True

    def find_gesture_pointing_thumb_distance(self, lm_list):
        len4_8 = math.hypot(lm_list[4][1] - lm_list[8][1], lm_list[4][2] - lm_list[8][2])
        return len4_8

    def find_gesture_swing_left(self, lm_list):
        if lm_list[0][1] > 450:
            return True

    def find_gesture_swing_right(self, lm_list):
        if lm_list[0][1] < 190:
            return True

    def find_prepositions(self, lm_list):
        if self.find_gesture_pre_swing(lm_list):
            self.waiting_for = self.gestures['swing']
            self.waiting_time = 50

        elif self.find_gesture_pre_snap(lm_list):
            self.waiting_for = self.gestures['snap']
            self.waiting_time = 20

        elif self.find_gesture_pre_pt_distance(lm_list):
            self.waiting_for = self.gestures['gap_between_pointer_and_thumb']
            self.waiting_time = 150

    def find_post_positions(self, lm_list):
        if self.waiting_for == 1:
            if self.find_gesture_post_snap(lm_list):
                self.waiting_time = -1
                return self.gestures["snap"]
        elif self.waiting_for == 2:
            len_thumb_pointer = self.find_gesture_pointing_thumb_distance(lm_list)
            if len_thumb_pointer:
                return self.gestures["gap_between_pointer_and_thumb"], len_thumb_pointer
        elif self.waiting_for == 3:
            if self.find_gesture_swing_left(lm_list):
                self.waiting_time = -1
                return self.gestures["swing_left"]
            elif self.find_gesture_swing_right(lm_list):
                self.waiting_time = -1
                return self.gestures["swing_right"]

    def find_single_hand_gestures(self, lm_list):
        if self.waiting_for is None:
            self.find_prepositions(lm_list)
        else:
            return self.find_post_positions(lm_list)

    def find_gestures(self, lm_list1, lm_list2):
        if self.waiting_time >= 0:
            self.waiting_time -= 1
        else:
            self.waiting_for = None

        if len(lm_list1) > 0 and len(lm_list2) == 0:
            return self.find_single_hand_gestures(lm_list1)

        elif len(lm_list1) > 0 and len(lm_list2) > 0:
            # TODO two-hand gestures
            pass

        else:
            self.waiting_time = -1
            return None


class Socket:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.ip = "" type ip here if gethostbyname doesn't work
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.port = 80

    def send_detected_gesture(self, gesture_id):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        client_socket.send(bytes(str(gesture_id), "utf-8"))

def main():
    client_socket = Socket()

    capture = cv2.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)
    detector = handDetector(detection_confidence=0.7, tracking_confidence=0.6)
    start_time = 0
    end_time = 0
    while True:

        success, img = capture.read()
        start_time = time.time()
        fps = int(1 / (start_time - end_time))
        img = detector.find_hands(img)
        lm_list1 = detector.find_lm_positions(img)
        lm_list2 = detector.find_lm_positions(img, which_hand=1)
        found_gest = detector.find_gestures(lm_list1, lm_list2)
        if found_gest:
            print(found_gest)
            client_socket.send_detected_gesture(found_gest)

        end_time = start_time
        cv2.putText(img, str(fps), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 100, 255), 3)
        cv2.imshow("cam_image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
