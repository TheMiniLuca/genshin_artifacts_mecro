import ctypes
import threading
import time
from typing import List

import cv2
import keyboard
from PIL import ImageGrab
from pytesseract import pytesseract

from artifacts import *

user32 = ctypes.windll.user32

pytesseract.tesseract_cmd = r'C:\Users\kchah\AppData\Local\tesseract.exe'


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


def move_mouse(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)


def get_mouse_position():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    point = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def click_mouse():
    # user32.SetCursorPos(x, y)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # left down
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # left up


def get_mouse_position_in_active_window():
    hwnd = user32.GetForegroundWindow()

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.ScreenToClient(hwnd, ctypes.byref(pt))
    return pt.x, pt.y


def capture_and_save(x1, y1, x2, y2, path):
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Save the image to the specified path
    screenshot.save(path)


def preprocess_image(img_path):
    # Load the image
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remove noise from the image
    gray = cv2.medianBlur(gray, 3)

    # Threshold the image to simplify the text
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return thresh


def extract_text_from_image(img_path) -> List[str]:
    img = preprocess_image(img_path)

    # Extract text from image
    # custom_config = r'-l kor+eng --oem 3 --psm 4'
    text = pytesseract.image_to_string(img, lang="kor+eng")
    return text.splitlines()


@auto_str
class Stats:
    def __init__(self, name: int, value: float | int, percent: bool):
        self.name = name
        self.value = value
        self.percent = percent

    def __str__(self) -> str:
        return auto_str(self)


@auto_str
class Artifact:
    def __init__(self, name: str | None, part: str | None, main_status: Stats | None, status: List[Stats]):
        self.name = name
        self.part = part
        self.main_status = main_status
        self.status = status

    def __str__(self) -> str:
        return auto_str(self)


def get_status(value: str) -> Stats | None:
    status_value = [c.value for c in Status]
    status_name = [c.name for c in Status]
    for (stat, name) in zip(status_value, status_name):
        if '%' in stat and '%' in value:
            return Stats(stat, float(value.split("+")[1].replace("%", "")), True)
        if stat in value:
            return Stats(stat, int(value.split("+")[1]), False)
    return None


def get_part(value: str) -> str | None:
    part_list = [c.value for c in Part]
    part_name = [c.name for c in Part]
    for (part, name) in zip(part_list, part_name):
        if part in value:
            return part
    return None


def get_main_status(key: str, value: str) -> Stats | None:
    status_value = [c.value for c in Status]
    status_name = [c.name for c in Status]
    for (stat, name) in zip(status_value, status_name):
        if '%' in stat and '%' in value:
            return Stats(stat, float(value.replace("%", "")), True)
        if stat in key:
            return Stats(stat, int(value), False)
    return None


def get_name(value: str) -> Stats | None:
    artifact_list = [c.value for c in ArtifactName]
    artifact_name = [c.name for c in ArtifactName]
    for (artifact, name) in zip(artifact_list, artifact_name):
        if artifact in value:
            return artifact
    return None


def extract_artifact_from_text(texts: List[str]) -> Artifact:
    status: List[Status] = []
    part = get_part(texts[2])
    main_status = get_main_status(texts[4], texts[6])
    for i in range(10, 14):
        stats = get_status(texts[i])
        if stats is not None:
            status.append(stats)

    if len(status) == 3:
        name = get_name(texts[13])
    else:
        name = get_name(texts[14])
    return Artifact(name, part, main_status, status)


def get_image_index_path(index):
    return "C:\\Users\\kchah\\Desktop\\artifacts_genshin\\artifacts_" + str(index) + ".png"


artifactList = []


def click_artifact(x, y, index):
    move_mouse(x, y)
    click_mouse()
    time.sleep(0.5)
    print("성유물---")
    path = get_image_index_path(index)
    capture_and_save(984, 181, 1473, 997, path)
    extract = extract_text_from_image(path)
    print(extract)
    artifactList.append(extract_artifact_from_text(extract))
    print(artifactList[len(artifactList) - 1])
    index += 1


def start_keyboard_thread():
    while True:
        index = 0
        x, y = (54 + 68), 110 + 80
        keyboard.wait(']')
        # x += 9 + 68 * 2
        # click_artifact(x, y, index)
        # index += 1
        for l in range(1):
            for i in range(6):
                click_artifact(x, y, index)
                index += 1
                x += 9 + 68 * 2
            y += 7 + 81 * 2
            move_mouse(x, y)
            for i in range(6):
                click_artifact(x, y, index)
                index += 1
                x -= 9 + 68 * 2
            y += 7 + 81 * 2


def get_location():
    while True:
        keyboard.wait('shift')
        print(get_mouse_position_in_active_window())


t = threading.Thread(target=start_keyboard_thread)
t.start()
t1 = threading.Thread(target=get_location)
t1.start()
