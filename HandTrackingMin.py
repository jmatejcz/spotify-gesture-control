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
            "swing_right": 5,
            "one_up" : 6,
            "two_up" : 7,
            "three_up" : 8
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
        ''' returns list of all landmarks' coords '''
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

    ''' pre_gestures are starting points of all gestures '''
    ''' after they are detected algorithm start searching for certain ending positions'''
    ''' if ending position is detected in certain amount of frames after staring position '''
    ''' whole gesture is detected '''

    def find_starting_position(self, lm_list):
        ''' all fingers are straight '''
        ''' and hand is more or less in the middle '''
        len5_8 = math.hypot(lm_list[5][1] - lm_list[8][1], lm_list[5][2] - lm_list[8][2])
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        len1_4 = math.hypot(lm_list[1][1] - lm_list[4][1], lm_list[1][2] - lm_list[4][2])
        if len1_4 > 70 and len5_8 > 70 and len9_12 > 75 and len13_16 > 70 and len17_20 > 50 \
                and len1_4 < 120 and len5_8 < 110 and len9_12 < 120 and len13_16 < 110 and len17_20 < 90 \
                and lm_list[0][1] > 245 and lm_list[0][1] < 395:
            return True

    def find_gesture_pre_snap(self, lm_list):
        ''' distance beetween middle finger tip and thumb tip is small enough'''
        length_between = math.hypot(lm_list[4][1] - lm_list[12][1], lm_list[4][2] - lm_list[12][2])

        if length_between < 15:
            return True

    def find_gesture_pre_pt_distance(self, lm_list):
        ''' thumb and pointing finger stick together'''
        ''' other fingers straight '''
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        len4_8 = math.hypot(lm_list[4][1] - lm_list[8][1], lm_list[4][2] - lm_list[8][2])
        if len9_12 > 70 and len13_16 > 70 and len17_20 > 70 and len4_8 < 15:
            return True


    def find_gesture_one_finger(self, lm_list):
        ''' one finger up '''
        len5_8 = math.hypot(lm_list[5][1] - lm_list[8][1], lm_list[5][2] - lm_list[8][2])
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        if len5_8 > 70 and len9_12 < 30 and len13_16 < 30 and len17_20 < 30:
            return True

    def find_gesture_two_fingers(self, lm_list):
        ''' two fingers up '''
        len5_8 = math.hypot(lm_list[5][1] - lm_list[8][1], lm_list[5][2] - lm_list[8][2])
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        if len5_8 > 70 and len9_12 > 30 and len13_16 < 30 and len17_20 < 30:
            return True

    def find_gesture_three_fingers(self, lm_list):
        ''' three fingers up '''
        len5_8 = math.hypot(lm_list[5][1] - lm_list[8][1], lm_list[5][2] - lm_list[8][2])
        len9_12 = math.hypot(lm_list[9][1] - lm_list[12][1], lm_list[9][2] - lm_list[12][2])
        len13_16 = math.hypot(lm_list[13][1] - lm_list[16][1], lm_list[13][2] - lm_list[16][2])
        len17_20 = math.hypot(lm_list[17][1] - lm_list[20][1], lm_list[17][2] - lm_list[20][2])
        if len5_8 > 70 and len9_12 > 70 and len13_16 > 70 and len17_20 < 30:
            return True

    def find_gesture_post_snap(self, lm_list):
        ''' distance beetween middle finger tip and thumb tip '''
        length_between = math.hypot(lm_list[4][1] - lm_list[12][1], lm_list[4][2] - lm_list[12][2])
        if length_between > 45:
            return True

    def find_gesture_pointing_thumb_distance(self, lm_list):
        len4_8 = round(math.hypot(lm_list[4][1] - lm_list[8][1], lm_list[4][2] - lm_list[8][2]))
        return len4_8

    def find_gesture_swing_right(self, lm_list):
        if lm_list[0][1] > 450:
            return True

    def find_gesture_swing_left(self, lm_list):
        if lm_list[0][1] < 190:
            return True

    def find_prepositions(self, lm_list):
        ''' finding prepostions and setting waiting_for to await a certain gesture '''
        ''' waiting_time is number of frames when the algorithm will await for '''
        ''' 2nd part of the gesture '''
        if self.find_starting_position(lm_list):
            self.waiting_for = self.gestures['starting_position']
            self.waiting_time = 50

        elif self.find_gesture_pre_snap(lm_list):
            self.waiting_for = self.gestures['snap']
            self.waiting_time = 20

        elif self.find_gesture_pre_pt_distance(lm_list):
            self.waiting_for = self.gestures['gap_between_pointer_and_thumb']
            self.waiting_time = 100

    def find_post_positions(self, lm_list):
        ''' finding ending positions and returning what gesture was found '''
        if self.waiting_for == 1:
            if self.find_gesture_post_snap(lm_list):
                self.waiting_time = -1
                return self.gestures["snap"]

        elif self.waiting_for == 2:
            len_thumb_pointer = self.find_gesture_pointing_thumb_distance(lm_list)
            if len_thumb_pointer:
                return self.gestures["gap_between_pointer_and_thumb"], len_thumb_pointer

        elif self.waiting_for == 0:
            if self.find_gesture_swing_left(lm_list):
                self.waiting_time = -1
                return self.gestures["swing_left"]

            elif self.find_gesture_swing_right(lm_list):
                self.waiting_time = -1
                return self.gestures["swing_right"]

            elif self.find_gesture_one_finger(lm_list):
                self.waiting_time = -1
                return self.gestures["one_up"]

            elif self.find_gesture_two_fingers(lm_list):
                self.waiting_time = -1
                return self.gestures["two_up"]

            elif self.find_gesture_three_fingers(lm_list):
                self.waiting_time = -1
                return self.gestures["three_up"]

    def find_single_hand_gestures(self, lm_list):
        if self.waiting_for is None:
            self.find_prepositions(lm_list)
        else:
            return self.find_post_positions(lm_list)

    def find_gestures(self, lm_list1, lm_list2):
        ''' returns found gesture '''
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
        #self.host_name = '192.168.56.1'
        self.ip = socket.gethostbyname(self.host_name)
        #self.ip = '79.184.239.4'
        self.port = 5050
        self.delay = 0

    def send_detected_gesture(self, gesture_id):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        client_socket.send(bytes(str(gesture_id), "utf-8"))

def main():
    client_socket = Socket()

    capture = cv2.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)
    detector = handDetector(detection_confidence=0.8, tracking_confidence=0.6)
    start_time = 0
    end_time = 0
    while True:

        success, img = capture.read()
        start_time = time.time()
        fps = int(1 / (start_time - end_time))
        img = detector.find_hands(img)
        lm_list1 = detector.find_lm_positions(img)
        lm_list2 = detector.find_lm_positions(img, which_hand=1)
        if client_socket.delay < 0:
            found_gest = detector.find_gestures(lm_list1, lm_list2)
            if found_gest:
                print(found_gest)
                try:
                    client_socket.send_detected_gesture(found_gest)
                    client_socket.delay = 20
                except:
                    print('failed to send gesture to server')
        else:
            client_socket.delay -= 1
        

        end_time = start_time
        cv2.putText(img, str(fps), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 100, 255), 3)
        cv2.imshow("cam_image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
