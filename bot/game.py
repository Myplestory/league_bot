import logging
import random
import json
import pyautogui
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
    
        
        self.MINI_MAP_UNDER_TURRET = MinimapZones.get("base_blue")
        self.MINI_MAP_CENTER_MID = MinimapZones.get("mid_lane")
        self.MINI_MAP_ENEMY_NEXUS = MinimapZones.get("base_red")
        self.ULT_DIRECTION = MinimapZones.get("top_lane")
        self.AFK_OK_BUTTON = (0.4981, 0.4647)
        self.SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
        self.SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.58)
        self.SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)

        self.minimap_coords = {}
        self.update_window_dimensions()
        self.update_minimap_coords()
        self.update_screen_ui_coords()

        
        self.LOADING_SCREEN_TIME = 3
        self.MINION_CLASH_TIME = 85
        self.FIRST_TOWER_TIME = 1500
        self.MAX_GAME_TIME = 3000

        self.BOT_T3_TURRET = "Turret_T200_L0_P3"
        self.BOT_T2_TURRET = "Turret_T200_L0_P2"
        self.BOT_T1_TURRET = "Turret_T200_L0_P1"
        self.BOT_INHIB = "Inhib_T200_L0_P1"

        self.MID_T3_TURRET = "Turret_T200_L1_P3"
        self.MID_T2_TURRET = "Turret_T200_L1_P2"
        self.MID_T1_TURRET = "Turret_T200_L1_P1"
        self.MID_INHIB = "Inhib_T200_L1_P1"

        self.TOP_T3_TURRET = "Turret_T200_L2_P3"
        self.TOP_T2_TURRET = "Turret_T200_L2_P2"
        self.TOP_T1_TURRET = "Turret_T200_L2_P1"
        self.TOP_INHIB = "Inhib_T200_L2_P1"

        self.NEXUS_TOWERS = ["Turret_T200_L1_P5","Turret_T200_L1_P4"]


### RATIO AND SCREEN UTILS ###

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
    
    def convert_screen_ratio(self, ratio):
        """Convert a screen-relative ratio (0.0–1.0) to coordinates within the League window."""
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
    
    def update_screen_ui_coords(self):
        """Precompute screen-relative UI element coordinates like shop buttons."""
        self.SHOP_ITEM_COORDS = [self.convert_screen_ratio(r) for r in self.SHOP_ITEM_BUTTONS]
        self.SHOP_PURCHASE_COORD = self.convert_screen_ratio(self.SHOP_PURCHASE_ITEM_BUTTON)
        self.SYSTEM_MENU_X_COORD = self.convert_screen_ratio(self.SYSTEM_MENU_X_BUTTON)
        self.AFK_OK_COORD = self.convert_screen_ratio(self.AFK_OK_BUTTON)


### GAME MECHANICS ###

    def shop(self):
        self.league.focus()
        print("Opening shop")
        press_key('p')
        coords = random.choice(self.SHOP_ITEM_COORDS)
        move_mouse(*coords)
        click(*coords, button='right')
        print("shop purchase")
        press_key('p')


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

### CONVERT TOWER COORDS ###

    def convert_stage(self, macro):
        hm = {
            "Turret_T200_L0_P3": "x",  # Bot T3
            "Turret_T200_L0_P2": "x",  # Bot T2
            "Turret_T200_L0_P1": "x",  # Bot T1
            "Inhib_T200_L0_P1": "x",   # Bot Inhib

            "Turret_T200_L1_P3": "x",  # Mid T3
            "Turret_T200_L1_P2": "x",  # Mid T2
            "Turret_T200_L1_P1": "x",  # Mid T1
            "Inhib_T200_L1_P1": "x",   # Mid Inhib

            "Turret_T200_L2_P3": "x",  # Top T3
            "Turret_T200_L2_P2": "x",  # Top T2
            "Turret_T200_L2_P1": "x",  # Top T1
            "Inhib_T200_L2_P1": "x",   # Top Inhib

            "Turret_T200_L1_P5": "x",  # Nexus Tower 1
            "Turret_T200_L1_P4": "x"   # Nexus Tower 2
        }
        return hm[macro]
        

### PLAY GAME ###

    def play(self):
        try:
            self.game_start()
            self.game_play_loop()
        except KeyboardInterrupt:
            print("\n[BOT] Interrupted manually. Stopping...")
        except GameServerError as e:
            print(f"[ERROR] Game server error: {e}")

### GAME STAGES ###

    def game_start(self):
        log.info("Waiting for Minion Clash")
        sleep(10)
        self.shop()
        self.keypress('y')  # lock screen
        self.upgrade_abilities()
        while self.server.get_game_time() < self.MINION_CLASH_TIME:
            self.right_click(self.MINI_MAP_UNDER_TURRET)  # to prevent afk warning popup
            self.left_click(self.AFK_OK_BUTTON)
        log.info("Playing Game")

    def game_play_loop(self):
        try:
            while True:
                self.server.update_data()
                if self.server.get_summoner_health == 0:
                    sleep(5)
                    continue
                current_time = self.server.get_game_time()
                # if current_time < self.LOADING_SCREEN_TIME:
                #     loading_screen(game_server)
                if current_time < self.MINION_CLASH_TIME:
                    self.game_start()
                elif current_time < self.FIRST_TOWER_TIME:
                    self.game_play(self.MINI_MAP_CENTER_MID)
                elif current_time < self.MAX_GAME_TIME:
                    data = json.loads(self.server.data)
                    events = data.get("events",{}).get("Events", [])
                    destroyed_turrets = set()
                    for event in events:
                        if event.get("EventName") == "TurretKilled":
                            turret_id_full = event.get("TurretKilled", "")
                            if "Turret_T200_L1" in turret_id_full:
                                parts = turret_id_full.split("_")
                                if len(parts) >= 4:
                                    turret_id = f"{parts[0]}_{parts[1]}_{parts[2]}"
                                    destroyed_turrets.add(turret_id)
                    for turret in [self.MID_T1_TURRET, self.MID_T2_TURRET, self.MID_T3_TURRET]:
                        if turret not in destroyed_turrets:
                            print(turret)
                            self.game_play(self.convert_stage(turret))
                        else:
                            print("[BOT] All mid turrets down. Pushing NEXUS.")
                            # self.game_play(self.MID_TURRET_POSITIONS.get("NEXUS"))
                else:
                    pass
                    raise GameServerError("Game has exceeded the max time limit")
        except KeyboardInterrupt:
            print("\n[BOT] Interrupted manually. Stopping...")
        except GameServerError as e:
            print(f"[ERROR] Game server error: {e}")


    def game_play(self, stage):
        """Main loop: buy, level up, go mid, attack, retreat, back"""
        print("[BOT] Starting gameplay loop...")
        try:
            if self.server.summoner_is_dead():
                print("[BOT] Dead. Waiting to respawn...")
                sleep(5)
            self.shop()
            self.upgrade_abilities()
            self.left_click(self.AFK_OK_BUTTON)
            # Walk to lane
            self.attack_click(self.MINI_MAP_CENTER_MID)
            self.keypress('d')  # Ghost
            sleep(self.TIME_TO_LANE)
            # Engage in burst combat loop
            for _ in range(8):
                if self.server.summoner_is_dead():
                    print("[BOT] Died during combat.")
                    break
                hp = self.server.get_summoner_health()
                print(f"[BOT] Current HP: {hp * 100:.1f}%")
                # if hp < 0.7:
                #     print("[BOT] HP low. Flashing and retreating.")
                #     self.keypress('f')  # Flash
                #     self.right_click(self.RETREAT_POSITION)
                #     sleep(4)
                #     break
                # self.attack_click(self.MID_ATTACK_POSITION)
                # sleep(5)
                # self.right_click(self.RETREAT_POSITION)
                # sleep(3)
            if self.server.summoner_is_dead():
                print("Dead, passing")
            # Ult and recall
            print("[BOT] Using ultimate and recalling...")
            self.keypress('f')  # Optional flash
            self.attack_click(self.ULT_DIRECTION)
            self.keypress('r')  # Ult
            sleep(1)
            self.right_click(self.MINI_MAP_UNDER_TURRET)
            sleep(4)
            self.keypress('b')  # Recall
            sleep(10)

        except KeyboardInterrupt:
            print("\n[BOT] Interrupted manually. Stopping...")
        except GameServerError as e:
            print(f"[ERROR] Game server error: {e}")



    



if __name__ == "__main__":
    bot = GameBot()
    try:
        if not bot.server.is_running():
            raise GameServerError("Game is not currently running.")
        else:
                # Run zone test or play logic:
                bot.play()
                # bot.play(attack_position=bot.MINI_MAP_CENTER_MID, retreat=bot.MINI_MAP_UNDER_TURRET, time_to_lane=5)
    except GameServerError as e:
        print(f"[ERROR] Could not connect to game server: {e}")
        exit(1)


