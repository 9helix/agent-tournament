# movement_manager.py
import random
from config import *

class MapMemory:
    """
    Simple exploration/movement memory:
    - Stores known map tiles
    - Remembers visited target tiles
    - Selects new random targets with left/right bias
    - Moves one step toward selected target (straight-line, not pathfinding)
    """

    def __init__(self, team_color):
        #self.team_color = team_color
        
        # Memory structures
        self.known_map = {}              # (x, y) → tile
        #self.visited_targets = set()     # explored goals
        #self.current_target = None       # active goal
        
        self.map_width = WIDTH
        self.map_height = HEIGHT

    # -------------------------------------------------------------
    # Map memory update (converts local visible_world to global map)
    # -------------------------------------------------------------
    def update_map_memory(self, visible_world, agent_pos, shared_knowledge):
        ax, ay = agent_pos
        vr = len(visible_world) // 2  # vision radius

        for dy in range(len(visible_world)):
            for dx in range(len(visible_world[0])):
                tile = visible_world[dy][dx]
                world_x = ax + (dx - vr)
                world_y = ay + (dy - vr)

                # Ignore out-of-bounds tiles
                if not (0 <= world_x < self.map_width): 
                    continue
                if not (0 <= world_y < self.map_height): 
                    continue

                # If this tile is UNKNOWN
                if tile == ASCII_TILES["unknown"]:
                    # If another agent already knows this tile, skip it
                    if (world_x, world_y) in shared_knowledge:
                        continue
                    # otherwise: do NOT store unknown at all
                    # (unknown means "we learned nothing new")
                    continue

                # Store known tiles normally
                shared_knowledge[(world_x, world_y)] = tile
                self.known_map[(world_x, world_y)] = tile

    # REMOVE AFTER INTEGRATION
    # -------------------------------------------------------------
    # TESTING ONLY
    # Select a new random tile to explore
    # -------------------------------------------------------------
    # def choose_new_target(self):
    #     """
    #     Randomly pick a tile the agent hasn't targeted before.
    #     Bias:
    #         Blue → bias toward right side
    #         Red  → bias toward left side
    #     """

    #     valid_empty_tiles = [pos for pos, tile in self.known_map.items()
    #                          if tile != "#" and pos not in self.visited_targets]

    #     if not valid_empty_tiles:
    #         return None

    #     # Apply directional bias
    #     if self.team_color == "blue":
    #         # Weight tiles by x coordinate (more weight on right)
    #         weighted = [(pos, pos[0] + 1) for pos in valid_empty_tiles]
    #     else:
    #         # Weight tiles by distance from right side (more weight on left)
    #         weighted = [(pos, (self.map_width - pos[0])) for pos in valid_empty_tiles]

    #     total = sum(w for _, w in weighted)
    #     pick = random.uniform(0, total)

    #     running = 0
    #     for pos, weight in weighted:
    #         running += weight
    #         if running >= pick:
    #             self.visited_targets.add(pos)
    #             self.current_target = pos
    #             return pos

    #     # Fallback (never happens)
    #     pos = random.choice(valid_empty_tiles)
    #     self.visited_targets.add(pos)
    #     self.current_target = pos
    #     return pos

    # -------------------------------------------------------------
    # TESTING ONLY
    # Step toward current target (simple direct movement)
    # -------------------------------------------------------------
    # def step_toward_target(self, agent_pos):
    #     if self.current_target is None:
    #         return None  # no movement

    #     ax, ay = agent_pos
    #     tx, ty = self.current_target

    #     # If arrived → clear target
    #     if (ax, ay) == (tx, ty):
    #         self.current_target = None
    #         return None

    #     # simple straight-line chase (NOT pathfinding)
    #     if tx > ax:
    #         return "right"
    #     if tx < ax:
    #         return "left"
    #     if ty > ay:
    #         return "down"
    #     if ty < ay:
    #         return "up"

    #     return None
