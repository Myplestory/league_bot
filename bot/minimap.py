# minimap_zones.py

class MinimapZones:
    """
    Relative minimap coordinates (percent-based).
    These values are approximations and can be tuned per resolution if needed.
    """

    minimap_left_ratio = 0.78
    minimap_top_ratio = 0.6
    minimap_width_ratio = 0.22
    minimap_height_ratio = 0.4


    zones = {
        # Bases
        "base_blue": (0.08, 0.92),
        "base_red":  (0.90, 0.14),

        # Lanes (validated)
        "top_lane":  (0.18, 0.22),
        "mid_lane":  (0.50, 0.54),
        "bot_lane":  (0.82, 0.82),

        # # Jungle camps
        # "ally_jungle":  (0.30, 0.74),  # Blue side jungle near bot
        # "enemy_jungle": (0.70, 0.30),  # Red side jungle near top

        # # Objectives
        # "baron":   (0.24, 0.20),  # Near top-left river
        # "dragon":  (0.76, 0.78),  # Near bottom-right river

        # # River
        # "river_top":    (0.38, 0.32),
        # "river_bot":    (0.62, 0.70),
        # "river_center": (0.50, 0.54),  # Matches mid_lane

        # # Vision control (tri-bushes near base/jungle)
        # "blue_tri": (0.16, 0.84),
        # "red_tri":  (0.84, 0.18),
    }


    @classmethod
    def get(cls, name: str):
        return cls.zones.get(name)
