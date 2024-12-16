import sys
from enum import Enum

filename = "input"

UNREACHABLE = sys.maxsize


class Direction(Enum):
    EAST = ">"
    NORTH = "^"
    SOUTH = "v"
    WEST = "<"

    def left(self):
        match self:
            case Direction.EAST:
                return Direction.NORTH
            case Direction.NORTH:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.EAST
            case Direction.WEST:
                return Direction.SOUTH

    def offset_x(self):
        match self:
            case Direction.EAST:
                return 1
            case Direction.NORTH:
                return 0
            case Direction.SOUTH:
                return 0
            case Direction.WEST:
                return -1

    def offset_y(self):
        match self:
            case Direction.EAST:
                return 0
            case Direction.NORTH:
                return -1
            case Direction.SOUTH:
                return 1
            case Direction.WEST:
                return 0

    def right(self):
        match self:
            case Direction.EAST:
                return Direction.SOUTH
            case Direction.NORTH:
                return Direction.EAST
            case Direction.SOUTH:
                return Direction.WEST
            case Direction.WEST:
                return Direction.NORTH


class Maze:
    tiles = [[]]

    width = 0
    height = 0

    start_x = 0
    start_y = 0

    end_x = 0
    end_y = 0

    def __init__(self, tiles):
        self.tiles = tiles
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        for y in range(0, self.height):
            for x in range(0, self.width):
                if tiles[x][y] == "S":
                    self.start_x = x
                    self.start_y = y
                elif tiles[x][y] == "E":
                    self.end_x = x
                    self.end_y = y

    def print(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                print(self.tiles[x][y], end="")
            print()

    def remove_dead_ends(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.__is_dead_end(x, y):
                    self.__remove_dead_end(x, y)

    def __is_dead_end(self, x, y):
        if self.tiles[x][y] == "S" or self.tiles[x][y] == "E" or self.tiles[x][y] == "#":
            return False
        open_paths = 0
        if self.tiles[x + 1][y] != "#":
            open_paths += 1
        if self.tiles[x][y - 1] != "#":
            open_paths += 1
        if self.tiles[x][y + 1] != "#":
            open_paths += 1
        if self.tiles[x - 1][y] != "#":
            open_paths += 1
        return open_paths <= 1

    def __remove_dead_end(self, x, y):
        self.tiles[x][y] = "#"
        if self.__is_dead_end(x + 1, y):
            self.__remove_dead_end(x + 1, y)
        if self.__is_dead_end(x, y - 1):
            self.__remove_dead_end(x, y - 1)
        if self.__is_dead_end(x, y + 1):
            self.__remove_dead_end(x, y + 1)
        if self.__is_dead_end(x - 1, y):
            self.__remove_dead_end(x - 1, y)


class UpdateInfo:
    x = 0
    y = 0
    direction = None
    new_distance = UNREACHABLE

    def __init__(self, x, y, direction, new_distance):
        self.x = x
        self.y = y
        self.direction = direction
        self.new_distance = new_distance


def get_maze():
    with open(filename) as file:
        lines = file.read().splitlines()
    width = len(lines[0])
    height = len(lines)
    tiles = []
    for x in range(0, width):
        tiles.append([])
        for y in range(0, height):
            tiles[x].append(lines[y][x])
    return Maze(tiles)


def update_distances(maze, distance_map, x, y, direction, new_distance):
    updates = [UpdateInfo(x, y, direction, new_distance)]

    while 0 < len(updates):
        update = updates[0]

        # don't make walls passable
        if maze.tiles[update.x][update.y] == "#":
            updates.remove(update)
            continue

        # don't make it worse
        if distance_map[update.x][update.y][update.direction] < update.new_distance:
            updates.remove(update)
            continue

        # update
        distance_map[update.x][update.y][update.direction] = update.new_distance

        # update rotated values
        updates.append(UpdateInfo(update.x, update.y, update.direction.left(), update.new_distance + 1000))
        updates.append(UpdateInfo(update.x, update.y, update.direction.right(), update.new_distance + 1000))

        # update neighbor
        updates.append(UpdateInfo(
            update.x - update.direction.offset_x(),
            update.y - update.direction.offset_y(),
            update.direction,
            update.new_distance + 1
        ))

        updates.remove(update)


def create_distance_map(maze):
    # initialize a distances map
    distances = []
    for x in range(0, maze.width):
        distances.append([])
        for y in range(0, maze.height):
            values = dict()
            values[Direction.EAST] = UNREACHABLE
            values[Direction.NORTH] = UNREACHABLE
            values[Direction.SOUTH] = UNREACHABLE
            values[Direction.WEST] = UNREACHABLE
            distances[x].append(values)

    # update all distances
    update_distances(maze, distances, maze.end_x, maze.end_y, Direction.EAST, 0)
    update_distances(maze, distances, maze.end_x, maze.end_y, Direction.NORTH, 0)
    update_distances(maze, distances, maze.end_x, maze.end_y, Direction.SOUTH, 0)
    update_distances(maze, distances, maze.end_x, maze.end_y, Direction.WEST, 0)

    return distances


def add_benches(maze, distance_map, x, y, direction):
    maze.tiles[x][y] = "O"

    # turn left
    if distance_map[x][y][direction.left()] == distance_map[x][y][direction] - 1000:
        add_benches(maze, distance_map, x, y, direction.left())

    # turn right
    if distance_map[x][y][direction.right()] == distance_map[x][y][direction] - 1000:
        add_benches(maze, distance_map, x, y, direction.right())

    # walk
    if distance_map[x + direction.offset_x()][y + direction.offset_y()][direction] == distance_map[x][y][direction] - 1:
        add_benches(maze, distance_map, x + direction.offset_x(), y + direction.offset_y(), direction)


def count_benches(maze):
    number_of_benches = 0
    for x in range(0, maze.width):
        for y in range(0, maze.height):
            if maze.tiles[x][y] == "O":
                number_of_benches += 1
    return number_of_benches


def main():
    maze = get_maze()
    maze.remove_dead_ends()
    distances = create_distance_map(maze)
    add_benches(maze, distances, maze.start_x, maze.start_y, Direction.EAST)
    maze.print()
    number_of_benches = count_benches(maze)
    print("Number of benches: {}".format(number_of_benches))


if __name__ == '__main__':
    main()
