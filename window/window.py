import time
import win32gui
import win32con
import pyautogui
from bot.mouse import click, move_mouse
from bot.keys import cast_ability
from bot.minimap import MinimapZones

class LeagueWindow:
    def __init__(self):
        self.hwnd = self._find_window()
        self.rect = win32gui.GetWindowRect(self.hwnd)

    def _find_window(self):
        def callback(h, extra):
            if "League of Legends" in win32gui.GetWindowText(h) and win32gui.IsWindowVisible(h) :
                extra.append(h)
        handles = []
        win32gui.EnumWindows(callback, handles)
        if not handles:
            raise Exception("Window not found")
        return handles[0]

    def focus(self):
        # Try to bring the window to the foreground by clicking its top-left corner
        x, y, _, _ = self.rect
        pyautogui.click(x + 10, y + 10)  # click near the top-left to trigger focus
        time.sleep(0.1)
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def center(self):
        x, y, x2, y2 = self.rect
        return (x + (x2 - x) // 2, y + (y2 - y) // 2)

    
    def click_minimap(self, rel_x, rel_y):
        """
        Clicks on the minimap using relative (0.0–1.0) zone coords,
        scaled to dynamic window size using ratios from MinimapZones.
        """
        x1, y1, x2, y2 = self.rect
        window_width = x2 - x1
        window_height = y2 - y1

        # Import from MinimapZones
        mm = MinimapZones
        minimap_left = x1 + int(window_width * mm.minimap_left_ratio)
        minimap_top = y1 + int(window_height * mm.minimap_top_ratio)
        minimap_width = int(window_width * mm.minimap_width_ratio)
        minimap_height = int(window_height * mm.minimap_height_ratio)

        # Translate relative zone coords to actual screen coords
        click_x = minimap_left + int(rel_x * minimap_width)
        click_y = minimap_top + int(rel_y * minimap_height)

        self.focus()
        time.sleep(0.2)
        click(click_x, click_y, button='right')
        time.sleep(0.2)

    def p(self):
        print(self.hwnd)
        print(self.rect)

    # def test_inputs(self):
    #     print("Focusing window...")
    #     self.focus()
    #     time.sleep(0.5)

    #     # Cast Q at the center of the screen
    #     x, y = self.center()
    #     a(f"Casting Q at center: ({x}, {y})")
    #     self.input.cast_ability('q', target_x=x, target_y=y)

    #     time.sleep(1)

    def test_zones(self):
        self.focus()
        time.sleep(1)

        zones = MinimapZones.zones  # dict of zone_name -> (x%, y%)
        for name, (rel_x, rel_y) in zones.items():
            print(f"Hovering over {name} at ({rel_x}, {rel_y})")
            self.click_minimap(rel_x, rel_y)
            time.sleep(1)

    def test_center(self):
        self.focus()
        x, y = self.center()
        print(f"Center of window: ({x}, {y})")
        move_mouse(x, y)
        time.sleep(0.5)
        click(x, y, button='right')


        


win = LeagueWindow()
win.p()
# win.test_zones()
# win.test_center()
