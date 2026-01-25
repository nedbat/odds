"""A simple terminal-based 2048 game."""

import dataclasses
import itertools
import random

from typing import Callable


@dataclasses.dataclass
class Tile:
    num: int
    merged: bool = False


class Board:
    def __init__(self, size=4):
        self.n = size
        self.tiles: dict[tuple[int, int], Tile] = {}

    def draw(self):
        SPACE_PARTS = [
            "╭╌╌╌╌╌╌╮",
            "┊      ┊",
            "┊      ┊",
            "┊      ┊",
            "╰╌╌╌╌╌╌╯",
        ]
        TILE_PARTS = [
            "╔══════╗",
            "║      ║",
            "║      ║",
            "║      ║",
            "╚══════╝",
        ]
        for row in range(self.n):
            for rowrow in range(5):
                for col in range(self.n):
                    tile = self.tiles.get((col, row))
                    if tile is None:
                        print(SPACE_PARTS[rowrow], end="")
                    else:
                        if rowrow == 2:
                            print(f"║{tile.num:^6}║", end="")
                        else:
                            print(TILE_PARTS[rowrow], end="")
                print()

    def add_random_tile(self):
        all_squares = set(itertools.product(range(self.n), repeat=2))
        empties = list(all_squares - self.tiles.keys())
        empty = random.choice(empties)
        num = 2 if random.random() < 0.9 else 4
        self.tiles[empty] = Tile(num)

    def slide(self, dx, dy):
        cols = range(self.n)
        if dx == 1:
            cols = reversed(cols)
        rows = range(self.n)
        if dy == 1:
            rows = reversed(rows)

        merged = 0
        any_moved = False
        for row, col in itertools.product(rows, cols):
            tile = self.tiles.get((col, row))
            if tile is None:
                continue
            while True:
                ncol = col + dx
                nrow = row + dy
                if (ncol not in range(self.n)) or (nrow not in range(self.n)):
                    break
                next_tile = self.tiles.get((ncol, nrow))
                if next_tile is None:
                    del self.tiles[(col, row)]
                    col, row = ncol, nrow
                    self.tiles[(col, row)] = tile
                    any_moved = True
                elif next_tile.num == tile.num and not next_tile.merged:
                    del self.tiles[(col, row)]
                    next_tile.num += tile.num
                    merged += next_tile.num
                    next_tile.merged = True
                    any_moved = True
                    break
                else:
                    break
        for tile in self.tiles.values():
            tile.merged = False

        return any_moved, merged

    def any_move(self):
        if len(self.tiles) < self.n * self.n:
            return True
        for row in range(self.n):
            for col in range(self.n):
                tile = self.tiles[(col, row)]
                for dx, dy in MOVES.values():
                    ntile = self.tiles.get((col + dx, row + dy))
                    if ntile is not None and ntile.num == tile.num:
                        return True
        return False

    def max_number(self):
        return max(self.tiles.values(), key=lambda t: t.num).num


MOVES = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}


def game(
    size: int,
    goal: int,
    output_fn: Callable[[Board], None],
    move_fn: Callable[[int], str],
) -> bool:
    board = Board(size=size)
    board.add_random_tile()
    board.add_random_tile()
    score = 0

    while True:
        output_fn(board)
        if not board.any_move():
            return False
        if board.max_number() == goal:
            return True
        move = move_fn(score)
        if move in MOVES:
            any_moved, merged = board.slide(*MOVES[move])
            if any_moved:
                score += merged
                board.add_random_tile()


def interactive_game():
    print("Welcome! Your goal is to get a 2048 tile.")
    print("Moves: 'a' left, 's' down, 'd' right, 'w' up.")

    def move_fn(score):
        return input(f"{score} Move> ")

    def output_fn(board):
        board.draw()

    if game(size=4, goal=2048, output_fn=output_fn, move_fn=move_fn):
        print("You win!")
    else:
        print("You lose!")


def board_from_list(numss):
    board = Board()
    for row, cols in enumerate(numss):
        for col, num in enumerate(cols):
            if num:
                board.tiles[(col, row)] = Tile(num)
    return board


if __name__ == "__main__":
    interactive_game()
