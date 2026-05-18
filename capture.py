"""Screen capture + OCR to read Rocket League chat."""
import threading
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
        self._ocr_running = False
        self._pending_lines: list[str] = []
        self._lock = threading.Lock()

        if not _USE_EASYOCR and not _USE_TESSERACT:
            raise RuntimeError("No OCR engine found. pip install easyocr")

        engine = "easyocr" if _USE_EASYOCR else "pytesseract"
        print(f"[capture] Using OCR engine: {engine}")

    def _grab(self) -> np.ndarray:
        with mss.mss() as sct:
            return np.array(sct.grab(self.region))

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(scaled, 80, 255, cv2.THRESH_BINARY)
        return thresh

    def _changed(self, frame: np.ndarray) -> bool:
        if self._last_frame is None:
            return True
        diff = np.abs(frame.astype(np.int16) - self._last_frame.astype(np.int16))
        return float(diff.mean()) > 2.0

    def _run_ocr(self, img: np.ndarray, prev_set: set):
        if _USE_EASYOCR:
            results = _reader.readtext(img, detail=0)
            current = [r.strip() for r in results if r.strip()]
        else:
            text = pytesseract.image_to_string(img, config="--psm 6")
            current = [l.strip() for l in text.splitlines() if l.strip()]

        new = [l for l in current if l.lower().strip() not in prev_set]

        with self._lock:
            self._last_lines = current
            self._pending_lines.extend(new)
            self._ocr_running = False

    def get_new_lines(self) -> list[str]:
        """Return new chat lines. OCR runs in background — non-blocking."""
        frame = self._grab()

        if self._changed(frame):
            self._last_frame = frame.copy()
            if not self._ocr_running:
                self._ocr_running = True
                prev_set = {l.lower().strip() for l in self._last_lines}
                processed = self._preprocess(frame)
                t = threading.Thread(target=self._run_ocr, args=(processed, prev_set), daemon=True)
                t.start()

        with self._lock:
            if self._pending_lines:
                lines = list(self._pending_lines)
                self._pending_lines.clear()
                return lines
        return []
