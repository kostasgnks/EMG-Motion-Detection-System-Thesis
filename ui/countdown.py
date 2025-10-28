import cv2

def countdown(frame, seconds, arm):
    counter_text = f"0:{seconds}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3.0
    thickness = 6
    (text_w, text_h), _ = cv2.getTextSize(counter_text, font, font_scale, thickness)
    frame_h, frame_w = frame.shape[:2]
    text_x = (frame_w - text_w) // 2
    text_y = 80
    cv2.rectangle(
        frame,
        (text_x - 20, text_y - text_h - 20),
        (text_x + text_w + 20, text_y + 20),
        (30, 30, 30),
        -1
    )
    cv2.putText(
        frame,
        counter_text,
        (text_x, text_y),
        font,
        font_scale,
        (0, 255, 255),
        thickness,
        cv2.LINE_AA
    )

    label_text = "Deksi xeri" if arm.value == 0 else "Aristero xeri"
    label_font_scale = 1.2
    label_thickness = 3
    (label_w, label_h), _ = cv2.getTextSize(label_text, font, label_font_scale, label_thickness)
    label_x = 30
    label_y = frame_h - 30
    cv2.rectangle(
        frame,
        (label_x - 10, label_y - label_h - 10),
        (label_x + label_w + 10, label_y + 10),
        (30, 30, 30),
        -1
    )
    cv2.putText(
        frame,
        label_text,
        (label_x, label_y),
        font,
        label_font_scale,
        (0, 255, 255),
        label_thickness,
        cv2.LINE_AA
    )