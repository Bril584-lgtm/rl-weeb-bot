"""Screen capture + OCR to read Rocket League chat."""
import numpy as np
import cv2
import mss

try:
    import easyocr
    _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    _USE_EASYOCR = True
except ImportError:
    _USE_EASYOCR = False

try:
    import pytesseract
    _USE_TESSERACT = True
except ImportError:
    _USE_TESSERACT = False


class ChatCapture:
    def __init__(self, region: dict):
        self.region = region
        self._last_frame: np.ndarray | None = None
        self._last_lines: list[str] = []

        if not _USE_EASYOCR and not _USE_TESSERACT:
            raise RuntimeError(
                "No OCR engine found. Install easyocr or pytesseract:\n"
                "  pip install easyocr\n"
                "  OR\n"
                "  pip install pytesseract  (also needs Tesseract binary)"
            )

        engine = "easyocr" if _USE_EASYOCR else "pytesseract"
        print(f"[capture] Using OCR engine: {engine}")

    def _grab(self) -> np.ndarray:
        with mss.mss() as sct:
            return np.array(sct.grab(self.region))

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        # 2x upscale improves OCR accuracy on small game text
        scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        # RL chat is white text on dark semi-transparent background
        _, thresh = cv2.threshold(scaled, 80, 255, cv2.THRESH_BINARY)
        return thresh

    def _changed(self, frame: np.ndarray) -> bool:
        if self._last_frame is None:
            return True
        diff = np.abs(frame.astype(np.int16) - self._last_frame.astype(np.int16))
        return float(diff.mean()) > 2.0

    def _ocr(self, img: np.ndarray) -> list[str]:
        if _USE_EASYOCR:
            results = _reader.readtext(img, detail=0)
            return [r.strip() for r in results if r.strip()]
        # pytesseract fallback
        text = pytesseract.image_to_string(img, config="--psm 6")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def get_new_lines(self) -> list[str]:
        """Return chat lines that weren't visible in the previous scan."""
        frame = self._grab()

        if not self._changed(frame):
            return []

        self._last_frame = frame.copy()
        processed = self._preprocess(frame)
        current = self._ocr(processed)

        prev_set = {l.lower().strip() for l in self._last_lines}
        new = [l for l in current if l.lower().strip() not in prev_set]

        self._last_lines = current
        return new
