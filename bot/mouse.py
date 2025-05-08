import pyautogui
import time
import random

# Move the mouse
def move_mouse(x, y, duration=0.2):
    pyautogui.moveTo(x, y, duration=duration)

# Normal move
def click(x, y, button):
    pyautogui.click(x=x, y=y, button=button)

# Attack move
def attack_move(x, y):
    pyautogui.press('a')
    time.sleep(random.uniform(0.05, 0.1))
    move_mouse(x, y)
    time.sleep(random.uniform(0.05, 0.1))
    pyautogui.click(button='right')