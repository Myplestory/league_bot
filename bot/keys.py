import pyautogui
import time
import random
from bot.mouse import move_mouse

def press_key(key):
    pyautogui.press(key)

def cast_ability(key, target_x=None, target_y=None):
    if target_x is not None and target_y is not None:
        move_mouse(target_x, target_y, duration=random.uniform(0.05, 0.15))
        time.sleep(0.05)
    press_key(key)
