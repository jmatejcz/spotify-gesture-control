import cv2
import mediapipe as mp 
import time
import math
import time

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
            "snap" : 1,
            "gap_between_pointer_and_thumb" : 2,
            "swing_left" : 3,
            "swing_right" : 4
        }

    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks: #handLms -> single hand recognized
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
                        cx , cy = int(lm.x * w), int(lm.y * h)
                        lm_list.append([nr, cx, cy])
        except:
            pass

        return lm_list



    # returns list of coordinates which was given as argument , for ex. list_of_lms = [1, 5, 12]
    # and lm_list is list of all landmarks
    def lm_coords(self, list_of_lms, lm_list):
        coords = []
        for i in list_of_lms:
            x, y = lm_list[i][1], lm_list[i][2]
            coords.append([i, x, y])

        return coords

    # returns list of distance between certain landmarks
    def lengths_between(self, list_of_coords):
        distance_list = []
        for nr, x, y in list_of_coords:
            pass


    
    def find_gesture_pre_snap(self, lm_list):
        # distance beetween middle finger tip and thumb tip
        x4, y4 = lm_list[4][1], lm_list[4][2]
        x12, y12 = lm_list[12][1], lm_list[12][2]
        length_between = math.hypot(x4-x12, y4-y12)
        #print(length_between)
        if length_between < 20:
            return True

    def find_gesture_post_snap(self, lm_list):
        # distance beetween middle finger tip and thumb tip
        x4, y4 = lm_list[4][1], lm_list[4][2]
        x12, y12 = lm_list[12][1], lm_list[12][2]
        length_between = math.hypot(x4-x12, y4-y12)
        #print(length_between)
        if length_between > 45:
            return True

    def find_gesture_pre_pt_distance(self, lm_list):
        coords = self.lm_coords([4, 8, 9, 12, 13, 16, 17, 20], lm_list)
        len9_12 = math.hypot(coords[2][1]-coords[3][1], coords[2][2]-coords[3][2])
        len13_16 = math.hypot(coords[4][1]-coords[5][1], coords[4][2]-coords[5][2])
        len17_20 = math.hypot(coords[6][1]-coords[7][1], coords[6][2]-coords[7][2])
        len4_8 = math.hypot(coords[0][1]-coords[1][1], coords[0][2]-coords[1][2])
        if len9_12>80 and len13_16>80 and len17_20>80 and len4_8 < 15:
            return True


    def find_gesture_pointing_thumb_distance(self, lm_list):
        coords = self.lm_coords([4, 8, 9, 12, 13, 16, 17, 20], lm_list)
        len9_12 = math.hypot(coords[2][1]-coords[3][1], coords[2][2]-coords[3][2])
        #print(f'length9_12: {len9_12}')
        len13_16 = math.hypot(coords[4][1]-coords[5][1], coords[4][2]-coords[5][2])
        #print(f'length13_16: {len13_16}')
        len17_20 = math.hypot(coords[6][1]-coords[7][1], coords[6][2]-coords[7][2])
        #print(f'length17_20: {len17_20}')

        len4_8 = math.hypot(coords[0][1]-coords[1][1], coords[0][2]-coords[1][2])
        #print(f'length4_8: {len4_8}')
        #if len9_12<30 and len13_16<30 and len17_20<30:
        return len4_8

    def find_gesture_
        



    def find_gestures(self, lm_list1, lm_list2):
        if self.waiting_time >= 0:
            self.waiting_time -= 1
        else:
            self.waiting_for = None

        if len(lm_list1) > 0:
        #print(self.waiting_time)
            if self.find_gesture_pre_snap(lm_list1) and self.waiting_for == None:
                self.waiting_time = 20
                self.waiting_for = self.gestures["snap"]
            
            if self.waiting_for == 1:
                if self.find_gesture_post_snap(lm_list1):
                    self.waiting_time = -1
                    return (self.gestures["snap"])

            if self.find_gesture_pre_pt_distance(lm_list1) and self.waiting_for == None:
                self.waiting_time = 150
                self.waiting_for = self.gestures["gap_between_pointer_and_thumb"]

            len_thumb_pointer = self.find_gesture_pointing_thumb_distance(lm_list1)
            if len_thumb_pointer and self.waiting_for == 2:
                return (self.gestures["gap_between_pointer_and_thumb"], len_thumb_pointer)

        if len(lm_list2) > 0:
            pass

        if len(lm_list1) == 0:
            self.waiting_time = -1
            return None


def main():
    capture = cv2.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)
    detector = handDetector(detection_confidence=0.7, tracking_confidence=0.6)
    start_time = 0
    end_time = 0
    while True:

        success, img = capture.read()
        start_time = time.time() 
        fps = int(1/(start_time - end_time))
        img = detector.find_hands(img)
        lm_list1 = detector.find_lm_positions(img)
        lm_list2 = detector.find_lm_positions(img, which_hand=1)

        found_gest = detector.find_gestures(lm_list1, lm_list2)
        if found_gest: 
            print(found_gest)
        
            
        end_time = start_time
        cv2.putText(img, str(fps), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 100, 255), 3)
        cv2.imshow("cam_image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
