import pyautogui
import time

time.sleep(5)

pyautogui.hotkey('ctrl', 'f')

time.sleep(1)

pyautogui.write("source", interval=0.1)
pyautogui.press("enter")

time.sleep(1)

pyautogui.moveTo(0, 0)
screen_width, screen_height = pyautogui.size()
steps = 1
for i in range(screen_width - 1):
    for j in range(screen_height - 1):
        pyautogui.moveTo(i, j, duration=0.5)

