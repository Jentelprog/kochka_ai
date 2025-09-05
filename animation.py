import cv2
import random as r
import sounddevice as sd
import numpy as np
from scipy.signal import stft


def animate(position):
    if position == "bad":
        t1 = r.randint(100, 200)
        cv2.imshow("animation", kochka1)
        cv2.waitKey(t1)
        t2 = r.randint(30, 100)
        cv2.imshow("animation", kochka2)
        cv2.waitKey(t2)
        t3 = r.randint(400, 500)
        cv2.imshow("animation", kochka3)
        cv2.waitKey(t3)
    else:
        t1 = r.randint(50, 100)
        cv2.imshow("animation", kochka1)
        cv2.waitKey(t1)
        t2 = r.randint(50, 500)
        cv2.imshow("animation", kochka2)
        cv2.waitKey(t2)
        t3 = r.randint(500, 1000)
        cv2.imshow("animation", kochka3)
        cv2.waitKey(t3)


idle = cv2.imread(r"kochka\kochka_idle.png")
kochka1 = cv2.imread(r"kochka\kochka1.png")
kochka2 = cv2.imread(r"kochka\kochka2.png")
kochka3 = cv2.imread(r"kochka\kochka3.png")

fs = 48000
duration = 0.5
frequency_threshold = 100

# Use Stereo Mix (index 30)
sd.default.device = 12

position = "bad"
while True:
    data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()

    f, t, Zxx = stft(data[:, 0], fs=fs, nperseg=1024)
    magnitude = np.abs(Zxx).mean(axis=1)
    max_freq = f[np.argmax(magnitude)]

    if max_freq > frequency_threshold:
        animate(position=position)
        position = "good"
    else:
        position = "bad"
        cv2.imshow("animation", idle)
        cv2.waitKey(1)
    print(position)
