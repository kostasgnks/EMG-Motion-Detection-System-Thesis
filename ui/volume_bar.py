import cv2

def volume_bar(frame, value, color):
    bar_width = 30
    bar_height = 200
    frame_h, frame_w = frame.shape[:2]
    bar_x = 50
    bar_y = frame_h - bar_height - 50

    fill_height = int((value / 800) * bar_height)
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (180, 180, 180),
        2,
    )
    cv2.rectangle(
        frame,
        (bar_x, bar_y + bar_height - fill_height),
        (bar_x + bar_width, bar_y + bar_height),
        color,
        -1,
    )
    value_text = f"{int(value)}"
    (text_w, text_h), baseline = cv2.getTextSize(
        value_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
    )
    text_x = bar_x + bar_width // 2 - text_w // 2 + 2
    text_y = bar_y - 15

    rect_x1 = text_x - 10
    rect_y1 = text_y - text_h - 8
    rect_x2 = text_x + text_w + 10
    rect_y2 = text_y + 8
    cv2.rectangle(
        frame,
        (rect_x1, rect_y1),
        (rect_x2, rect_y2),
        (40, 40, 40),
        -1,
        cv2.LINE_AA,
    )
    cv2.rectangle(
        frame,
        (rect_x1, rect_y1),
        (rect_x2, rect_y2),
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        value_text,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )