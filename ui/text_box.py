import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np


def text_box(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.9
    thickness = 2

    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    padding_x, padding_y = 50, 50

    box_w = text_w + 2 * padding_x
    box_h = text_h + 2 * padding_y

    frame_h, frame_w = frame.shape[:2]
    box_x1, box_y1 = 20, 20
    box_x2, box_y2 = 20 + box_w, 20 + box_h

    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (30, 30, 30), -1)
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 255, 255), 2)

    text_x = box_x1 + padding_x
    text_y = box_y1 + padding_y + text_h // 2

    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    try:
        font_pil = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(text_h * 1.2))
    except IOError as err:
        print(err)
        font_pil = ImageFont.load_default()
    draw.text((text_x, text_y - text_h // 2), text, fill=(255, 255, 255), font=font_pil)
    frame[:,:,:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)