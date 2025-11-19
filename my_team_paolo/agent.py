# First name Last name

""" 
Description of the agent (approach / strategy / implementation) in short points.
This is a universal agent that works for both blue and red teams.
- It uses the __init__ method to define team-specific variables like enemy color, 
  flag tiles, and preferred directions for attacking and returning.
- The update() method uses these variables, allowing the same logic to work for either team.
- A simple random movement model is used, biased towards the current objective 
  (attacking the enemy side or returning to the home side).
"""

from config import *
from map_memory import MapMemory # New
import random

import datetime # New

def log(msg): # New
    with open("agent_debug.log", "a") as f: # New
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f") # New
        f.write(f"[{timestamp}] {msg}\n") # New

class Agent:
    
    def __init__(self, color, index):
        self.color = color
        self.index = index
        self.mov = MapMemory(color) # New
        
        # --- Universal Agent Logic Setup ---
        # Set team-specific goals and identifiers based on the agent's color.
        # This allows the update logic to be color-agnostic.
        if self.color == "blue":
            self.enemy_flag_tile = ASCII_TILES["red_flag"]
            # Directions are relative to the side of the map
            self.attack_direction = "right"
            self.return_direction = "left"
        else: # red
            self.enemy_flag_tile = ASCII_TILES["blue_flag"]
            self.attack_direction = "left"
            self.return_direction = "right"

    def update(self, visible_world, position, can_shoot, holding_flag, shared_knowledge, hp, ammo):

        # 1. update shared map memory
        self.mov.update_map_memory(visible_world, position, shared_knowledge)

        # 2. If no target exists, choose one
        if self.mov.current_target is None:
            self.mov.choose_new_target()

        # 3. Move towards target one step
        direction = self.mov.step_toward_target(position)

        if direction is None:
            # No valid target or arrived → idle
            return "", "up"
        
        log(
            #f"Tick={world_tick} "
            f"{self.color}-{self.index} "
            f"pos={position} "
            f"target={self.mov.current_target} "
            f"dir={direction}"
        )
        return "move", direction

    def terminate(self, reason):
        if reason == "died":
            print(f"{self.color} agent {self.index} died.")