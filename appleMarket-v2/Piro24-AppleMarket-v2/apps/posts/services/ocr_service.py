import numpy as np
import cv2
from paddleocr import PaddleOCR

OCR = PaddleOCR(use_angle_cls=True, lang='korean')

def preprocessimage(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # 업스케일 (작은 글자 인식률 ↑)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 대비 보정 (CLAHE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

    # PaddleOCR 입력 형식 유지 (H, W, 3)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def run_ocr(file_bytes: bytes) -> str:
    img = preprocessimage(file_bytes)

    result = OCR.ocr(img)

    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
        texts = result[0].get("rec_texts", []) or []
        return "\n".join([t for t in texts if isinstance(t, str)])

    texts = []
    lines = result[0] if (isinstance(result, list) and len(result) > 0 and isinstance(result[0], list)) else result

    if isinstance(lines, list):
        for line in lines:
            if not isinstance(line, (list, tuple)) or len(line) < 2:
                continue
            info = line[1]
            if isinstance(info, (list, tuple)) and len(info) >= 1 and isinstance(info[0], str):
                texts.append(info[0])
        return "\n".join(texts)

    return str(result)


