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

import re
from config import *
import random
import numpy as np
from map_memory import MapMemory
import astar

class Agent:

    def __init__(self, color, index):
        self.color = color
        self.index = index
        self.holding_flag = False
        self.current_path=[] #list of locations to follow
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
        self.mapMemory=MapMemory(color)
        self.holding_flag=False
    def update(self, visible_world, position, can_shoot, holding_flag, shared_knowledge, hp, ammo):
        self.mapMemory.update_map_memory(visible_world, position, shared_knowledge)
        shared_knowledge=self.mapMemory.known_map
        print(f"Agent {self.color} {self.index}, local position: {position}, HP: {hp}, Ammo: {ammo}")
              
        self.holding_flag = holding_flag
        if self.current_path:
            print(f"Agent {self.color} {self.index} following path: {self.current_path}")
            next_step=self.current_path.pop(0)
            return self.determine_direction(position,next_step)
        else:
            target=self.pick_desination(shared_knowledge, []) #empty list for now, no visited tiles
            print(f"Agent {self.color} {self.index} picking destination: {target}")
            if target:
                path=astar.astar(shared_knowledge, position, target,"{"if self.color=="blue" else "}")
                print(f"Agent {self.color} {self.index} computed path: {path}")
                if path and len(path)>1:
                    self.current_path=path[1:] #exclude current position
                    next_step=self.current_path.pop(0)
                    print("position:",position)
                    print("next step:",next_step)
                    return self.determine_direction(position,next_step)
            else:
                return None,None




        return None,None
        #intentionally below return, will test later
        if self.enemy_flag_tile in np.array(visible_world):
            print(f"{self.color} agent {self.index} sees the enemy flag!")
            #find path to enemy flag
            enemy_flag_position = np.argwhere(np.array(visible_world) == self.enemy_flag_tile)[0]
            path = astar(visible_world, position, tuple(enemy_flag_position))

    def terminate(self, reason):
        if reason == "died":
            print(f"{self.color} agent {self.index} died.")

    def pick_desination(
        self, visible_world: dict[tuple[int, int], str], visited_tiles: list[tuple[int, int]]
    ):
        candidates = [pos for pos, char in visible_world.items() if char not in "#/"+(ASCII_TILES["blue_flag"] if self.color=="blue" else ASCII_TILES["red_flag"])]
        
        if self.color == "blue" or (self.holding_flag and self.color == "red"):
            weights = [(row + 1)**3 for (row, col) in candidates]
        else:
            # Prioritize lower columns (moving left). 
            # Adjusted to avoid negative weights from original logic [1 - col]
            if candidates:
                max_row = max(row for row, col in candidates)
                weights = [(max_row - row + 1)**3 for (row, col) in candidates]
            else:
                weights = []

        if candidates:
            selected_coord = None
            while selected_coord is None or selected_coord in visited_tiles:
                selected_coord = random.choices(candidates, weights=weights, k=1)[0]

                # --- Let's see what happened ---
                #print(f"All '1's (candidates): {candidates}")
                #print(f"Their weights: {weights}")
                #print(f"\nSelected coordinate: {selected_coord}")
            return selected_coord
        else:
            print("No '1's found in the map.")
            return None

    def determine_direction(self,position,next_step):
        dx=next_step[0]-position[0]
        dy=next_step[1]-position[1]
        if dx==1:
            direction="right"
        elif dx==-1:
            direction="left"
        elif dy==1:
            direction="down"
        elif dy==-1:
            direction="up"
        print(direction)
        return ("move", direction)