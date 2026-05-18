"""
Drag a box over the Rocket League chat area to get your CHAT_REGION coords.
Run BEFORE launching RL, then Alt+Tab back to RL.

Usage:
    python calibrate.py

Click and drag over the chat box, then press Enter.
The region dict will be printed — paste it into config.py.
"""
import tkinter as tk
import mss
import numpy as np
from PIL import Image, ImageTk


def pick_region():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        raw = np.array(sct.grab(monitor))

    img = Image.fromarray(raw[:, :, :3])

    root = tk.Tk()
    root.title("Drag to select chat region, then press Enter")
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.88)

    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(root, cursor="crosshair", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    rect_id = [None]
    start = {}
    result = {}

    def on_press(e):
        start["x"], start["y"] = e.x, e.y

    def on_drag(e):
        if rect_id[0]:
            canvas.delete(rect_id[0])
        rect_id[0] = canvas.create_rectangle(
            start["x"], start["y"], e.x, e.y, outline="#00ff00", width=2
        )

    def on_release(e):
        result["x1"] = min(start["x"], e.x)
        result["y1"] = min(start["y"], e.y)
        result["x2"] = max(start["x"], e.x)
        result["y2"] = max(start["y"], e.y)

    def on_enter(_e):
        if not result:
            return
        region = {
            "top": result["y1"],
            "left": result["x1"],
            "width": result["x2"] - result["x1"],
            "height": result["y2"] - result["y1"],
            "mon": 1,
        }
        root.destroy()
        print("\nPaste this into config.py:\n")
        print(f"CHAT_REGION = {region}")

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Return>", on_enter)
    root.mainloop()


if __name__ == "__main__":
    pick_region()
