import logging
import random
from time import sleep

from bot.keys import press_key
from bot.mouse import move_mouse, click, attack_move
from window.window import LeagueWindow
from bot.minimap import MinimapZones
from lcu.server import GameServer, GameServerError

log = logging.getLogger(__name__)

# Use accurate positions from minimap.py
MINI_MAP_UNDER_TURRET = MinimapZones.get("base_blue")
MINI_MAP_CENTER_MID = MinimapZones.get("mid_lane")
MINI_MAP_ENEMY_NEXUS = MinimapZones.get("base_red")
ULT_DIRECTION = MinimapZones.get("top_lane")  # Reused as a placeholder direction
AFK_OK_BUTTON = (0.4981, 0.4647)
SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.58)
SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)

league = None
window_width = 0
window_height = 0
window_left = 0
window_top = 0

def convert_ratio(ratio):
    return (
        window_left + int(window_width * ratio[0]),
        window_top + int(window_height * ratio[1])
    )

def shop():
    press_key('p')
    coords = convert_ratio(random.choice(SHOP_ITEM_BUTTONS))
    move_mouse(*coords)
    click(*coords, button='left')
    coords = convert_ratio(SHOP_PURCHASE_ITEM_BUTTON)
    move_mouse(*coords)
    click(*coords, button='left')
    press_key('esc')
    coords = convert_ratio(SYSTEM_MENU_X_BUTTON)
    move_mouse(*coords)
    click(*coords, button='left')

def upgrade_abilities():
    press_key('ctrl+r')
    abilities = ['ctrl+q', 'ctrl+w', 'ctrl+e']
    random.shuffle(abilities)
    for ability in abilities:
        press_key(ability)

def left_click(ratio):
    coords = convert_ratio(ratio)
    move_mouse(*coords)
    click(*coords, button='left')
    sleep(1)

def right_click(ratio):
    coords = convert_ratio(ratio)
    move_mouse(*coords)
    click(*coords, button='right')
    sleep(1)

def attack_click(ratio):
    coords = convert_ratio(ratio)
    attack_move(*coords)
    sleep(1)

def keypress(key):
    press_key(key)
    sleep(1)

def play(game_server, attack_position, retreat, time_to_lane):
    league.focus()
    shop()
    upgrade_abilities()
    left_click(AFK_OK_BUTTON)
    attack_click(attack_position)
    keypress('d')
    sleep(time_to_lane)

    for _ in range(8):
        if game_server.get_summoner_health() < 0.7:
            keypress('f')
            right_click(retreat)
            sleep(4)
            break
        if game_server.summoner_is_dead():
            return
        attack_click(attack_position)
        sleep(5)
        right_click(retreat)
        sleep(3)

    if game_server.summoner_is_dead():
        return

    keypress('f')
    attack_click(ULT_DIRECTION)
    keypress('r')
    sleep(1)
    right_click(MINI_MAP_UNDER_TURRET)
    sleep(4)
    keypress('b')
    sleep(10)

# Run
if __name__ == "__main__":
    league = LeagueWindow()
    league.focus()
    x1, y1, x2, y2 = league.rect
    window_left, window_top = x1, y1
    window_width = x2 - x1
    window_height = y2 - y1
    print(f"Game window size: {window_width}x{window_height}")

    try:
        game_server = GameServer()
        if not game_server.is_running():
            raise GameServerError("Game is not currently running.")
    except GameServerError as e:
        print(f"[ERROR] Could not connect to game server: {e}")
        exit(1)

    play(game_server, attack_position=MINI_MAP_CENTER_MID, retreat=MINI_MAP_UNDER_TURRET, time_to_lane=5)
