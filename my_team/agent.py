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
import random
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
        self.base_position=None
        self.enemy_flag_pos=None
    def update(self, visible_world, position, can_shoot, holding_flag, shared_knowledge, hp, ammo):
        self.mapMemory.update_map_memory(visible_world, position, shared_knowledge)
        print(f"Agent {self.color} {self.index}, local position: {position}, HP: {hp}, Ammo: {ammo}")

        if self.base_position is None:
            # Assume base is at the first seen flag position
            for pos, char in shared_knowledge.items():
                if char == (ASCII_TILES["blue_flag"] if self.color == "blue" else ASCII_TILES["red_flag"]):
                    self.base_position = pos
                    print(f"Agent {self.color} {self.index} set base position to: {self.base_position}")
                    break 
        self.holding_flag = holding_flag
        if self.holding_flag:
            print(f"Agent {self.color} {self.index} is holding the flag.")
            #flag collider not mentioned since we need to the flags location
            path=astar.astar(shared_knowledge, position, self.base_position,"")
            if path and len(path)>1:
                self.current_path=path[1:] #exclude current position
                next_step=self.current_path.pop(0)
                print("position:",position)
                print("next step:",next_step)
                return self.determine_direction(position,next_step)
            
        # --- ENEMY FLAG OVERRIDE ---
        if not self.holding_flag:
            if self.enemy_flag_pos is None:
                for pos, char in shared_knowledge.items():
                    if char == self.enemy_flag_tile:
                        self.enemy_flag_pos = pos
                        break

            if self.enemy_flag_pos:
                # If reached flag position, stay there
                if position == self.enemy_flag_pos:
                    print(f"Agent {self.color} {self.index} waiting at flag position.")
                    return None, None

                # Check if we are already targeting the flag
                target_is_flag = False
                if self.current_path and len(self.current_path) > 0:
                    if self.current_path[-1] == self.enemy_flag_pos:
                        target_is_flag = True

                # If not targeting flag (or no path), try to route to it
                if not target_is_flag:
                    print(f"Agent {self.color} {self.index} targeting enemy flag at {self.enemy_flag_pos}")
                    path = astar.astar(
                        shared_knowledge,
                        position,
                        self.enemy_flag_pos,
                        ""
                    )

                    if path and len(path) > 1:
                        self.current_path = path[1:]  # discard current position
                        next_step = self.current_path.pop(0)
                        return self.determine_direction(position, next_step)
            
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


    def terminate(self, reason):
        if reason == "died":
            print(f"{self.color} agent {self.index} died.")

    def pick_desination(
        self, visible_world: dict[tuple[int, int], str], visited_tiles: list[tuple[int, int]]
    ):
        candidates = [pos for pos, char in visible_world.items() if char not in "#/"+(ASCII_TILES["blue_flag"] if self.color=="blue" else ASCII_TILES["red_flag"])]
        
        DIRECTION_PRIORITY=2 #agents determination to go to the opponents side or return to their side
        CENTER_PRIORITY = 1.2 # Preference for the middle of the map (adjust as needed)

        weights = []
        if candidates:
            # Determine max_x for weighting logic when moving left
            max_x = max(pos[0] for pos in candidates)

            for (x, y) in candidates:
                # 1. Direction Weight (X-axis)
                if self.color == "blue" or (self.holding_flag and self.color == "red"):
                    # Blue attacking or Red returning -> Go Right (increase x)
                    x_score = x
                else:
                    # Red attacking or Blue returning -> Go Left (decrease x)
                    x_score = max_x - x
                
                # 2. Center Weight (Y-axis)
                # Calculate distance from the middle row (HEIGHT / 2)
                # Closer to middle = higher score
                dist_from_center = abs(y - (HEIGHT / 2))
                y_score = (HEIGHT / 2) - dist_from_center
                
                # Combine weights: Direction is primary, Center is secondary
                weight = (DIRECTION_PRIORITY ** x_score) * (CENTER_PRIORITY ** y_score)
                weights.append(weight)

        if candidates and weights:
            selected_coord = None
            while selected_coord is None or selected_coord in visited_tiles:
                selected_coord = random.choices(candidates, weights=weights, k=1)[0]
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