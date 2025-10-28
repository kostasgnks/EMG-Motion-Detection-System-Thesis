import math
from queue import Queue, Empty
from threading import Lock
from enum import Enum

import cv2
import mediapipe as mp

from emg_reader import EMGReader
from ui.countdown import countdown
from ui.text_box import text_box
from ui.volume_bar import volume_bar
from ui.user_input import UserSelect

# === Serial Parameters ===
SERIAL_PORT = "COM5"
BAUD_RATE = 115200

SENSOR_PRESENT_VALUES = range(0, 2500)
ANGLE_RANGE = range(0, 130)

def calculate_angle(a, b, c):
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]

    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]

    cosine_angle = sum(ba[i] * bc[i] for i in range(2)) / (
        math.sqrt(sum(x**2 for x in ba)) * math.sqrt(sum(x**2 for x in bc))
    )
    angle = math.acos(max(-1, min(1, cosine_angle)))
    return math.degrees(angle)

class Arm(Enum):
    LEFT = 0
    RIGHT = 1

class MeasurementResult:
    def __init__(self, arm: Arm, values) -> None:
        self.arm = arm
        self.values = values

# === Main Application Window ===
class MainApp:
    def __init__(self, database):
        self.database = database

        self.app_started_lock = Lock()
        self.app_started_lock.acquire(False)
        self.started = False

        self.emg_data = Queue(300)
        self.emg_thread = EMGReader(SERIAL_PORT, BAUD_RATE, self.emg_data)
        self.value = 0
        self.info_text = ""
        self.angle_left = None
        self.angle_right = None
        self.draw_skeleton = False

        self.enter_key_lock = Lock()
        self.enter_key_lock.acquire()
        self.angle_range_lock = Lock()
        self.angle_range_lock.acquire()

        self.should_play_video = False
        self.video_loop = False
        self.video_cap: cv2.VideoCapture = cv2.VideoCapture()

        self.show_bar = False
        self.show_box = False
        self.measuring = False
        self.seconds = 0.0
        self.measurements = []
        self.current_arm = None

        self.show_user_view = False
        self.user_view = UserSelect(50, 50, 400, 50, self.database)

    def wearing_sensor(self):
        return self.value in SENSOR_PRESENT_VALUES

    def get_color(self):
        v = max(0, min(800, int(self.value)))
        r = int((v / 800) * 255)
        g = int((1 - v / 800) * 255)
        color = (0, g, r)  # OpenCV uses BGR
        if v <= 400:
            # Green to Yellow
            ratio = v / 400
            b = 0
            g = 255
            r = int(255 * ratio)
        else:
            # Yellow to Red
            ratio = (v - 400) / 400
            b = 0
            g = int(255 * (1 - ratio))
            r = 255
        return (b, g, r)

    def camera_loop(self):
        if not self.started:
            self.app_started_lock.release()
            self.started = True

        mp_pose = mp.solutions.pose  # type: ignore
        mp_drawing = mp.solutions.drawing_utils  # type: ignore
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            try:
                self.value = self.emg_data.get_nowait()
            except Empty:
                pass
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            # Map self.value (0-800) to a color gradient from green to red
            # Green: (0,255,0), Red: (0,0,255)
            if result.pose_landmarks:
                landmarks = result.pose_landmarks.landmark
                # Draw all landmarks and connections in default color
                if self.draw_skeleton:
                    mp_drawing.draw_landmarks(
                        frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )
                p1 = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                p2 = mp_pose.PoseLandmark.RIGHT_ELBOW.value

                if self.draw_skeleton:
                    h, w, _ = frame.shape
                    x1, y1 = int(landmarks[p1].x * w), int(landmarks[p1].y * h)
                    x2, y2 = int(landmarks[p2].x * w), int(landmarks[p2].y * h)

                    # Draw the connection in red (BGR: 0,0,255), thickness 4
                    cv2.line(frame, (x1, y1), (x2, y2), self.get_color(), 4)

                # Δεξί ώμος, αγκώνας, καρπός

                # Υπολογισμός γωνίας αγκώνα
                self.angle_left = int(calculate_angle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER], landmarks[mp_pose.PoseLandmark.LEFT_ELBOW], landmarks[mp_pose.PoseLandmark.LEFT_WRIST]))
                self.angle_right = int(calculate_angle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER], landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW], landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]))
                    
                if self.draw_skeleton:
                    if self.angle_right is not None:
                        cx, cy = int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x * frame.shape[1]), int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y * frame.shape[0])
                        cv2.putText(
                            frame,
                            f'{int(self.angle_right)} deg',
                            (cx - 50, cy - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 255),
                            2,
                            cv2.LINE_AA
                        )
                    if self.angle_left is not None:
                        cx, cy = int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x * frame.shape[1]), int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y * frame.shape[0])
                        cv2.putText(
                            frame,
                            f'{int(self.angle_left)} deg',
                            (cx - 50, cy - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 255),
                            2,
                            cv2.LINE_AA
                        )
                                    
                if self.angle_in_range():
                    try:
                        self.angle_range_lock.release()
                    except RuntimeError:
                        pass

            if self.show_box:
                text_box(frame, self.info_text)
            if self.should_play_video:
                self.handle_video_frame(frame)
            if self.show_bar:
                volume_bar(frame, self.value, self.get_color())
            if self.measuring:
                countdown(frame, self.seconds, self.current_arm)
                self.measurements.append(self.value)
            if self.show_user_view:
                self.user_view.draw(frame)

            frame = cv2.resize(frame, (854, 480))
            cv2.imshow("Camera Feed", frame)
            key = cv2.waitKey(1) & 0xFF
            self.user_view.handle_key(key)
            if key == 13: # Enter key
                try:
                    if not self.user_view.active:
                        self.enter_key_lock.release()
                except RuntimeError:
                    pass

        cap.release()
        cv2.destroyAllWindows()

    def handle_video_frame(self, frame):
        if self.video_cap.isOpened():
            self.video_cap.read()
            ret_vid, vid_frame = self.video_cap.read()
            if ret_vid:
                # Resize video frame to fit in a corner (e.g., 320x180)
                vid_frame = cv2.resize(vid_frame, (300, 188))
                # Overlay video frame on top-right corner
                h, w, _ = frame.shape
                vid_h, vid_w = vid_frame.shape[:2]
                x1 = w - vid_w - 10
                y1 = 10
                x2 = w - 10
                y2 = 10 + vid_h
                frame[y1:y2, x1:x2] = vid_frame

    def closeEvent(self, event):
        self.emg_thread.stop()
        event.accept()

    def play_video(self, name, loop=False):
        self.video_loop = loop
        self.video_cap = cv2.VideoCapture(name)
        self.should_play_video = True
    
    def wait_for_enter(self):
        self.enter_key_lock.acquire()

    def angle_in_range(self):
        if self.angle_left is not None and self.angle_left in ANGLE_RANGE:
            self.current_arm = Arm.LEFT
            return True
        elif self.angle_right is not None and self.angle_right in ANGLE_RANGE:
            self.current_arm = Arm.RIGHT
            return True
        return False

    def wait_for_angle(self):
        self.angle_range_lock.acquire()
        return self.current_arm

    def start(self):
        self.emg_thread.start()
        self.camera_loop()
        self.emg_thread.stop()