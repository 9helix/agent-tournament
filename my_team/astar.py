class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(
    shared_map: dict[tuple[int,int],str],
    current_position: tuple[int, int],
    target_position: tuple[int, int],flag_collider:str
) -> list[tuple[int, int]]:
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, current_position)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, target_position)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list - use dict/set for O(1) lookup
    open_dict = {current_position: start_node}  # position -> node mapping
    closed_set = set()  # just positions

    max_iterations = 10000  # Safety limit
    iterations = 0

    while open_dict and iterations < max_iterations:
        iterations += 1
        
        # Get the current node with lowest f value
        current_node = min(open_dict.values(), key=lambda node: node.f)
        current_position = current_node.position

        # Pop current off open dict, add to closed set
        del open_dict[current_position]
        closed_set.add(current_position)

        # Found the goal
        if current_position == target_position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (
                current_position[0] + new_position[0],
                current_position[1] + new_position[1],
            )

            # Make sure within range and walkable
            if node_position not in shared_map:
                continue
            if shared_map[node_position] in "#/" + flag_collider:
                continue

            # Skip if already in closed set
            if node_position in closed_set:
                continue

            # Calculate scores
            g = current_node.g + 1
            h = ((node_position[0] - target_position[0]) ** 2) + (
                (node_position[1] - target_position[1]) ** 2
            )
            f = g + h

            # If in open list with better score, skip
            if node_position in open_dict:
                if g >= open_dict[node_position].g:
                    continue

            # Create and add new node
            new_node = Node(current_node, node_position)
            new_node.g = g
            new_node.h = h
            new_node.f = f
            open_dict[node_position] = new_node

    return None  # No path found
