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
                if (world_x, world_y) not in shared_knowledge:
                    shared_knowledge[(world_x, world_y)] = tile
                
                if (world_x, world_y) not in self.known_map:
                    self.known_map[(world_x, world_y)] = tile
