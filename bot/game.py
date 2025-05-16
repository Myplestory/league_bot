import logging
import random
from time import sleep

from bot.keys import press_key
from bot.mouse import move_mouse, click, attack_move
from window.window import LeagueWindow
from bot.minimap import MinimapZones
from lcu.server import GameServer, GameServerError

log = logging.getLogger(__name__)

class GameBot:
    def __init__(self):
        self.league = LeagueWindow()
        self.update_window_dimensions()
        self.server = GameServer()
        
        self.minimap_coords = {}
        self.update_minimap_coords()
        
        self.MINI_MAP_UNDER_TURRET = MinimapZones.get("base_blue")
        self.MINI_MAP_CENTER_MID = MinimapZones.get("mid_lane")
        self.MINI_MAP_ENEMY_NEXUS = MinimapZones.get("base_red")
        self.ULT_DIRECTION = MinimapZones.get("top_lane")
        self.AFK_OK_BUTTON = (0.4981, 0.4647)
        self.SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
        self.SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.58)
        self.SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)


    def update_window_dimensions(self):
        self.league.focus()
        print(self.league)
        dims = self.league.get_dimensions()
        self.window_left = dims['left']
        self.window_top = dims['top']
        self.window_width = dims['width']
        self.window_height = dims['height']
        print(f"Updated window size: {self.window_width}x{self.window_height}")
        log.info(f"Updated window size: {self.window_width}x{self.window_height}")

    def convert_ratio(self, ratio):
        self.update_window_dimensions()
        return (
            self.window_left + int(self.window_width * ratio[0]),
            self.window_top + int(self.window_height * ratio[1])
        )
    
    def convert_minimap_zone(self, zone_ratio):
        """Converts a minimap-relative zone to screen coordinates using minimap position/scale."""
        self.update_window_dimensions()
        dims = self.league.get_dimensions()

        mm_left = dims['left'] + int(dims['width'] * MinimapZones.minimap_left_ratio)
        mm_top = dims['top'] + int(dims['height'] * MinimapZones.minimap_top_ratio)
        mm_width = int(dims['width'] * MinimapZones.minimap_width_ratio)
        mm_height = int(dims['height'] * MinimapZones.minimap_height_ratio)

        rel_x, rel_y = zone_ratio
        screen_x = mm_left + int(mm_width * rel_x)
        screen_y = mm_top + int(mm_height * rel_y)
        return screen_x, screen_y
    

    def update_minimap_coords(self):
        """Convert all minimap-relative zones to screen coordinates."""
        self.update_window_dimensions()
        dims = self.league.get_dimensions()

        mm_left = dims['left'] + int(dims['width'] * MinimapZones.minimap_left_ratio)
        mm_top = dims['top'] + int(dims['height'] * MinimapZones.minimap_top_ratio)
        mm_width = int(dims['width'] * MinimapZones.minimap_width_ratio)
        mm_height = int(dims['height'] * MinimapZones.minimap_height_ratio)

        self.minimap_coords = {
            name: (
                mm_left + int(rel_x * mm_width),
                mm_top + int(rel_y * mm_height)
            )
            for name, (rel_x, rel_y) in MinimapZones.zones.items()
        }
    
    def get_minimap_coords(self, zone_name):
        """Get cached minimap screen coords; auto-update if needed."""
        if zone_name not in self.minimap_coords:
            self.update_minimap_coords()
        return self.minimap_coords[zone_name]



    def shop(self):
        press_key('p')
        coords = self.convert_ratio(random.choice(self.SHOP_ITEM_BUTTONS))
        move_mouse(*coords)
        click(*coords, button='left')
        coords = self.convert_ratio(self.SHOP_PURCHASE_ITEM_BUTTON)
        move_mouse(*coords)
        click(*coords, button='left')
        press_key('esc')
        coords = self.convert_ratio(self.SYSTEM_MENU_X_BUTTON)
        move_mouse(*coords)
        click(*coords, button='left')

    def upgrade_abilities(self):
        press_key('ctrl+r')
        abilities = ['ctrl+q', 'ctrl+w', 'ctrl+e']
        random.shuffle(abilities)
        for ability in abilities:
            press_key(ability)

    def left_click(self, ratio):
        coords = self.convert_ratio(ratio)
        move_mouse(*coords)
        click(*coords, button='left')
        sleep(1)

    def right_click(self, ratio):
        coords = self.convert_ratio(ratio)
        move_mouse(*coords)
        click(*coords, button='right')
        sleep(1)

    def attack_click(self, ratio):
        coords = self.convert_ratio(ratio)
        attack_move(*coords)
        sleep(1)

    def keypress(self, key):
        press_key(key)
        sleep(1)

    def go_mid(self):
        coords = self.get_minimap_coords("mid_lane")
        print(f"[ACTION] Going mid lane at {coords}")
        attack_move(*coords)
        sleep(1)

    def go_bot(self):
        coords = self.get_minimap_coords("bot_lane")
        print(f"[ACTION] Going bot lane at {coords}")
        attack_move(*coords)
        sleep(1)

    def go_top(self):
        coords = self.get_minimap_coords("top_lane")
        print(f"[ACTION] Going top lane at {coords}")
        attack_move(*coords)
        sleep(1)


    def play(self):
        """Main loop: buy, go mid, attack, retreat if low HP, repeat."""
        print("[BOT] Starting gameplay loop...")
        try:
            while True:
                if self.server.summoner_is_dead():
                    print("[BOT] Dead. Waiting to respawn...")
                    sleep(5)
                    continue
                hp = self.server.get_summoner_health()
                print(f"[BOT] Current HP: {hp * 100:.1f}%")
                # Step 1: Shop and upgrade
                self.shop()
                self.upgrade_abilities()
                # Step 2: Go mid and attack
                self.go_mid()
                # Step 3: Sustain combat for a short burst
                for _ in range(5):
                    sleep(2)
                    if self.server.summoner_is_dead():
                        break
                    hp = self.server.get_summoner_health()
                    if hp < 0.4:
                        print("[BOT] HP low, retreating and recalling...")
                        self.right_click(self.MINI_MAP_UNDER_TURRET)
                        sleep(3)
                        self.keypress('b')  # Recall
                        sleep(10)
                        break
                    # Simulate continued aggression
                    self.go_mid()
        except KeyboardInterrupt:
            print("\n[BOT] Interrupted manually. Stopping...")
        except GameServerError as e:
            print(f"[ERROR] Game server error: {e}")


if __name__ == "__main__":
    bot = GameBot()

    try:
        if not bot.server.is_running():
            raise GameServerError("Game is not currently running.")
    except GameServerError as e:
        print(f"[ERROR] Could not connect to game server: {e}")
        exit(1)

    # Run zone test or play logic:
    bot.play()
    # bot.play(attack_position=bot.MINI_MAP_CENTER_MID, retreat=bot.MINI_MAP_UNDER_TURRET, time_to_lane=5)
