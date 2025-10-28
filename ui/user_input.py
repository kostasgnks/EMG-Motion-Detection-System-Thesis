import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from database import Database

class UserSelect:
    def __init__(
        self, x, y, w, h, database, font_scale=1, color=(255, 255, 255), bg_color=(50, 50, 50)
    ):
        self.database: Database = database
        self.rect = (x, y, w, h)
        self.text = ""
        self.active = True
        self.showing_help = False
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = font_scale
        self.color = color
        self.bg_color = bg_color

        self.measurements = []
        # Path to a TTF font that supports Greek, e.g., DejaVuSans
        self.pil_font_path = "C:/Windows/Fonts/arial.ttf"
        self.pil_font_size = int(28 * font_scale)

    def draw(self, frame):
        if self.active:
            self.draw_user_select(frame)
        else:
            self.draw_measurements(frame)

    def draw_user_select(self, frame):
        h_frame, w_frame = frame.shape[:2]

        box_w = int(w_frame * 0.5)
        box_h = int(h_frame * 0.15)
        x = (w_frame - box_w) // 2
        y = (h_frame - box_h) // 2
        self.rect = (x, y, box_w, box_h)

        cv2.rectangle(frame, (x, y), (x + box_w, y + box_h), self.bg_color, -1)
        border_color = (0, 255, 0) if self.active else (200, 200, 200)
        cv2.rectangle(frame, (x, y), (x + box_w, y + box_h), border_color, 4)

        roi = frame[y:y+box_h, x:x+box_w]
        roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(roi_pil)
        try:
            font_size = int(box_h * 0.40)
            font = ImageFont.truetype(self.pil_font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        prompt = "Εισάγετε το όνομα χρήστη"
        prompt_bbox = font.getbbox(prompt)
        prompt_w = prompt_bbox[2] - prompt_bbox[0]
        prompt_h = prompt_bbox[3] - prompt_bbox[1]
        prompt_x = (box_w - prompt_w) // 2
        prompt_y = int(box_h * 0.13) - prompt_h // 2

        pil_color = (self.color[2], self.color[1], self.color[0]) if len(self.color) == 3 else self.color

        draw.text((prompt_x, prompt_y), prompt, font=font, fill=pil_color)

        input_bbox = font.getbbox(self.text)
        input_w = input_bbox[2] - input_bbox[0]
        input_h = input_bbox[3] - input_bbox[1]
        input_x = (box_w - input_w) // 2
        input_y = int(box_h * 0.60) - input_h // 2
        draw.text((input_x, input_y), self.text, font=font, fill=pil_color)

        frame[y:y+box_h, x:x+box_w] = cv2.cvtColor(np.array(roi_pil), cv2.COLOR_RGB2BGR)

    def draw_measurements(self, frame):
        x, y, w, h = self.rect

        h_frame, w_frame = frame.shape[:2]
        box_w = int(w_frame * 0.97)
        box_h = int(h_frame * 0.87)
        x = (w_frame - box_w) // 2
        y = (h_frame - box_h) // 2
        w, h = box_w, box_h
        self.rect = (x, y, w, h)

        cv2.rectangle(frame, (x, y), (x + w, y + h), self.bg_color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 5)

        roi = frame[y:y+h, x:x+w]
        roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(roi_pil)
        try:
            base_h = int(h_frame * 0.45)
            font_title = ImageFont.truetype(self.pil_font_path, int(base_h * 0.15))
            font_measure = ImageFont.truetype(self.pil_font_path, int(base_h * 0.10))
            font_msg = ImageFont.truetype(self.pil_font_path, int(base_h * 0.09))
        except Exception:
            font_title = font_measure = font_msg = ImageFont.load_default()

        pil_color = (self.color[2], self.color[1], self.color[0]) if len(self.color) == 3 else self.color
        
        if not self.showing_help:
            title = "Μετρήσεις - " + self.text
            title_bbox = font_title.getbbox(title)
            title_w = title_bbox[2] - title_bbox[0]
            title_h = title_bbox[3] - title_bbox[1]
            title_x = (w - title_w) // 2
            title_y = int(h * 0.07)
            draw.text((title_x, title_y), title, font=font_title, fill=pil_color)

        total_measurements = len(self.measurements)
        measure_h = font_measure.getbbox("Hg")[3] - font_measure.getbbox("Hg")[1]
        total_height = total_measurements * measure_h + (total_measurements - 1) * int(measure_h * 0.6)
        start_y = (h - total_height) // 2

        for idx, measurement in enumerate(self.measurements):
            m_bbox = font_measure.getbbox(measurement)
            m_w = m_bbox[2] - m_bbox[0]
            m_x = (w - m_w) // 2
            m_y = start_y + idx * (measure_h + int(measure_h * 0.6))
            draw.text((m_x, m_y), measurement, font=font_measure, fill=pil_color)

        if not self.showing_help:
            msg = "Πιέστε ENTER για νέα μέτρηση.\nΠιέστε ? για βοήθεια."
            try:
                font_msg = ImageFont.truetype(self.pil_font_path, int(base_h * 0.13))
            except Exception:
                font_msg = ImageFont.load_default()
            lines = msg.split('\n')
            line_heights = []
            line_widths = []
            for line in lines:
                bbox = font_msg.getbbox(line)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1])
            msg_w = max(line_widths)
            msg_h = sum(line_heights) + int(h * 0.04) * (len(lines) - 1)
            msg_x = (w - msg_w) // 2
            msg_y = h - msg_h - int(h * 0.07)
            y_offset = msg_y
            for i, line in enumerate(lines):
                draw.text((msg_x, y_offset), line, font=font_msg, fill=pil_color)
                y_offset += line_heights[i] + int(h * 0.04)

        frame[y:y+h, x:x+w] = cv2.cvtColor(np.array(roi_pil), cv2.COLOR_RGB2BGR)

    def handle_key(self, key):
        if key == 13:  # Enter
            self.text = self.text.strip()
            if len(self.text):
                self.active = False
                self.update_measurements()
        elif key in (8, 127) and self.active:  # Backspace (8 for Windows/Linux, 127 for macOS)
            if self.text:
                self.text = self.text[:-1]
                print(self.text)
        elif 32 <= key <= 126 and self.active:  # Printable ASCII
            self.text += chr(key)
        elif key == ord('?') or key == ord('/'):
            self.showing_help = not self.showing_help
            print(self.showing_help)
            if self.showing_help:
                self.measurements = [
                    "%MVC: Η στιγμιαία ένταση του μυός, κανονικοποιημένη ως ποσοστό της μέγιστης",
                    "σύσπασης (MVC), δηλαδή πόσο κοντά είναι στο 100% η σύσπαση.",
                    "ΑΙ | Assymetry Index: Το ποσοστό απόκλισης της τρέχουσας μέτρησης",
                    "από την μέτρηση αναφοράς κατα την εγγραφή του χρήστη.",
                    "Αν το ποσοστό ΑΙ υπερβαίνει το 15%, υπάρχει περίπτωση να υφίσταται τραυματισμός.",
                    "Σε αυτή την περίπτωση συμβουλευτείτε ιατρό ή ειδικό.",
                    "Το παρών σύστημα δεν αποτελεί ιατρικό εργαλείο και δεν παρέχει εγγυήσεις για την",
                    "εγκυρότητα των αποτελεσμάτων του.",
                    "",
                    "Πιέστε ? για επιστροφή"
                ]
            else:
                self.update_measurements()

    def update_measurements(self):
        m = self.database.get_user_measurements(self.text)
        if m:
            self.measurements = [f"{d.timestamp} - MVC: {d.mvc}% - AI: {d.ai}% - {'Δεξί' if d.arm == 0 else 'Αριστερό'}" for d in self.database.get_user_measurements(self.text)]
        else:
            self.measurements = ["Δεν υπάρχουν μετρήσεις"]

    def reset(self):
        self.text = ""
        self.measurements = []
        self.active = True