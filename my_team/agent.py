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
import math
from map_memory import MapMemory
import astar


class Agent:

    def __init__(self, color, index):
        self.color = color
        self.index = index
        self.holding_flag = False
        self.current_path = []  # list of locations to follow
        # --- Universal Agent Logic Setup ---
        # Set team-specific goals and identifiers based on the agent's color.
        # This allows the update logic to be color-agnostic.
        if self.color == "blue":
            self.enemy_flag_tile = ASCII_TILES["red_flag"]
            # Directions are relative to the side of the map
            self.attack_direction = "right"
            self.return_direction = "left"
        else:  # red
            self.enemy_flag_tile = ASCII_TILES["blue_flag"]
            self.attack_direction = "left"
            self.return_direction = "right"
        self.mapMemory = MapMemory(color)
        self.holding_flag = False
        self.base_position = None
        self.enemy_flag_pos = None

    def update(
        self,
        visible_world,
        position,
        can_shoot,
        holding_flag,
        shared_knowledge,
        hp,
        ammo,
    ):
        self.mapMemory.update_map_memory(visible_world, position, shared_knowledge)
        print(
            f"Agent {self.color} {self.index}, local position: {position}, HP: {hp}, Ammo: {ammo}"
        )

        if self.base_position is None:
            # Assume base is at the first seen flag position
            if "map" in shared_knowledge:
                for pos, char in shared_knowledge["map"].items():
                    if char == (
                        ASCII_TILES["blue_flag"]
                        if self.color == "blue"
                        else ASCII_TILES["red_flag"]
                    ):
                        self.base_position = pos
                        print(
                            f"Agent {self.color} {self.index} set base position to: {self.base_position}"
                        )
                        break
        self.holding_flag = holding_flag

        # --- SHOOT ADJACENT ENEMY ---
        if can_shoot:
            # for i in visible_world:
            #    for j in i:
            #        print(j, end=" ")
            #    print()
            enemy_char = (
                ASCII_TILES["red_agent"] + ASCII_TILES["red_agent_f"]
                if self.color == "blue"
                else ASCII_TILES["blue_agent"] + ASCII_TILES["blue_agent_f"]
            )
            vr = len(visible_world) // 2

            # Change number to how far you want the agent to detect and shot (1 is the square directly next to the agent)
            DIST = 1
            directions = {
                "up": [
                    #(vr - DIST, vr - DIST),
                    #(vr, vr),
                    (vr - DIST * 2, vr),
                ],
                "down": [
                    #(vr + DIST, vr - DIST),
                    (vr + DIST * 2, vr),
                ],
                "left": [
                    (vr + DIST, vr - DIST),(vr - DIST, vr - DIST),
                    (vr, vr - DIST * 2),
                ],
                "right": [
                    (vr + DIST, vr + DIST),(vr - DIST, vr + DIST),
                    (vr, vr + DIST * 2),
                ],
            }
            if self.color == "blue":
                directions["left"].append((vr, vr))
            else:
                directions["right"].append((vr, vr))

            for direction, dirs in directions.items():
                for y, x in dirs:
                    if visible_world[y][x] in enemy_char:
                        print(f"Agent {self.color} {self.index} shoots {direction}")
                        return ("shoot", direction)

        if self.holding_flag:
            print(f"Agent {self.color} {self.index} is holding the flag.")
            # flag collider not mentioned since we need to the flags location
            path = astar.astar(
                shared_knowledge["map"], position, self.base_position, ""
            )
            if path and len(path) > 1:
                self.current_path = path[1:]  # exclude current position
                next_step = self.current_path.pop(0)
                print("position:", position)
                print("next step:", next_step)
                return self.determine_direction(position, next_step)

        # --- ENEMY FLAG OVERRIDE ---
        if not self.holding_flag:
            if self.enemy_flag_pos is None:
                if "map" in shared_knowledge:
                    for pos, char in shared_knowledge["map"].items():
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
                    print(
                        f"Agent {self.color} {self.index} targeting enemy flag at {self.enemy_flag_pos}"
                    )
                    path = astar.astar(
                        shared_knowledge["map"], position, self.enemy_flag_pos, ""
                    )

                    if path and len(path) > 1:
                        self.current_path = path[1:]  # discard current position
                        next_step = self.current_path.pop(0)
                        return self.determine_direction(position, next_step)

        if self.current_path:
            print(
                f"Agent {self.color} {self.index} following path: {self.current_path}"
            )
            next_step = self.current_path.pop(0)
            return self.determine_direction(position, next_step)
        else:
            if "map" in shared_knowledge:
                target = self.pick_desination(
                    shared_knowledge["map"], shared_knowledge, position, visible_world
                )
                print(f"Agent {self.color} {self.index} picking destination: {target}")
                if target:
                    path = astar.astar(
                        shared_knowledge["map"],
                        position,
                        target,
                        "{" if self.color == "blue" else "}",
                    )
                    print(f"Agent {self.color} {self.index} computed path: {path}")
                    if path and len(path) > 1:
                        self.current_path = path[1:]  # exclude current position
                        next_step = self.current_path.pop(0)
                        print("position:", position)
                        print("next step:", next_step)
                        return self.determine_direction(position, next_step)
            else:
                return None, None

        return None, None

    def terminate(self, reason):
        if reason == "died":
            print(f"{self.color} agent {self.index} died.")

    def pick_desination(
        self,
        visible_world: dict[tuple[int, int], str],
        shared_knowledge: dict,
        current_position: tuple[int, int],
        agent_visible_world: list[list[str]] = None,
    ):
        visited_tiles = self.mapMemory.get_visited_tiles(shared_knowledge)

        visible_tiles_set = set()
        if agent_visible_world:
            ax, ay = current_position
            vr = len(agent_visible_world) // 2
            for dy in range(len(agent_visible_world)):
                for dx in range(len(agent_visible_world[0])):
                    world_x = ax + (dx - vr)
                    world_y = ay + (dy - vr)
                    visible_tiles_set.add((world_x, world_y))

        candidates = [
            pos
            for pos, char in visible_world.items()
            if pos not in visited_tiles
            and char
            not in "#/"
            + (
                ASCII_TILES["blue_flag"]
                if self.color == "blue"
                else ASCII_TILES["red_flag"]
            )
        ]

        # Calculate progress towards enemy side (0 to 1)
        x_current = current_position[0]
        if self.color == "blue":
            linear_progress = x_current / WIDTH
        else:
            linear_progress = (WIDTH - 1 - x_current) / WIDTH

        linear_progress = max(0.0, min(1.0, linear_progress))

        # Sigmoid function for non-linear progress
        k = 8  # decay rate
        midpoint = 0.65  # after this much progress, decay speeds up
        sigmoid = 1 / (1 + math.exp(-k * (linear_progress - midpoint)))
        min_sigmoid = 1 / (1 + math.exp(-k * (0 - midpoint)))
        max_sigmoid = 1 / (1 + math.exp(-k * (1 - midpoint)))

        progress = (sigmoid - min_sigmoid) / (max_sigmoid - min_sigmoid)
        progress = max(0.0, min(1.0, progress))

        # Apply decay based on progress
        DIRECTION_PRIORITY_DECAY = 0.6
        CENTER_PRIORITY_DECAY = 1.3
        DIRECTION_PRIORITY_INITIAL = 2.7
        CENTER_PRIORITY_INITIAL = 1.8

        direction_priority = DIRECTION_PRIORITY_INITIAL - (
            DIRECTION_PRIORITY_DECAY * progress
        )
        center_priority = CENTER_PRIORITY_INITIAL - (CENTER_PRIORITY_DECAY * progress)
        weights = []
        if candidates:
            max_x = max(pos[0] for pos in candidates)

            for x, y in candidates:
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
                weight = (direction_priority**x_score) * (center_priority**y_score)

                DEPENDENCY_PENALTY = 2.5
                if (x, y) not in visible_tiles_set:
                    weight **= (1/DEPENDENCY_PENALTY)

                weights.append(weight)

        if candidates and weights:
            selected_coord = random.choices(candidates, weights=weights, k=1)[0]

            new_visited = []
            new_visited.append(selected_coord)
            x, y = selected_coord
            # Mark adjacent tiles as visited to encourage exploration
            new_visited.append((x + 1, y))
            new_visited.append((x - 1, y))
            new_visited.append((x, y + 1))
            new_visited.append((x, y - 1))

            self.mapMemory.add_visited_tiles(shared_knowledge, new_visited)
            return selected_coord
        else:
            print("No '1's found in the map.")
            return None

    def determine_direction(self, position, next_step):
        dx = next_step[0] - position[0]
        dy = next_step[1] - position[1]
        if dx == 1:
            direction = "right"
        elif dx == -1:
            direction = "left"
        elif dy == 1:
            direction = "down"
        elif dy == -1:
            direction = "up"
        print(direction)
        return ("move", direction)
