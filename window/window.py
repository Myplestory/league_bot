import time
import win32gui
import win32con
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
        # Bring the window to foreground
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)

        # Get window center coordinates
        x1, y1, x2, y2 = win32gui.GetWindowRect(self.hwnd)
        center_x = x1 + (x2 - x1) // 2
        center_y = y1 + (y2 - y1) // 2

        # Move mouse and perform a gentle click at center
        move_mouse(center_x, center_y)
        time.sleep(0.05)
        click(center_x, center_y, button='left')
        time.sleep(0.1)


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

    def get_dimensions(self):
        self.rect = win32gui.GetWindowRect(self.hwnd)
        x1, y1, x2, y2 = map(int, self.rect)  # convert to ints
        return {
            'left': x1,
            'top': y1,
            'width': x2 - x1,
            'height': y2 - y1
        }

        


win = LeagueWindow()
win.p()
