from board import read_board, Board
import numpy as np
from game_solvers.logger import LOG
from itertools import combinations
from game_solvers.sporcle_parser import DOWNLOAD_BASE_PATH
from pathlib import Path


SKYSCRAPER_PUZZLES_PATH = DOWNLOAD_BASE_PATH / "skyscraper_logic_puzzles"

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    # Rules to run once
    buildings_seen_limits_max_square_value(board)
    board.display()

    while board.is_live:
        changed = any(
            [
                square_has_one_possible_value(board),
                value_in_group_has_one_possible_square(board)
            ]
        )
        print(board.is_live)
        if not changed:
            break

    return board.is_solved


def square_has_one_possible_value(board: Board) -> bool:
    """If a square only has one possible value, assign it."""
    # Check all squares
    updated = False
    for square in board.all_squares():
        sub_values = square.sub_values
        if len(square.sub_values) == 1:
            square_coords = square.coords
            value = sub_values[0]
            board.assign_value(square_coords, value)
            LOG.info(f"Square at {square_coords} has only one possible value - {value}")
            updated = True
    board.display()
    return updated


def value_in_group_has_one_possible_square(board: Board) -> bool:
    """If a value in a row/col can only fit in one square, assign it."""

    def has_one_possible_square(group: np.ndarray):
        """Return list of values which occur once in sub_values, with Square"""
        res = []
        all_values = np.concatenate([g.sub_values for g in group])
        values, counts = np.unique_counts(all_values)
        for value, count in zip(values, counts):
            if count != 1:
                continue
            value = int(value)
            # One possible place for value
            for square in group:
                if value in square.sub_values:
                    res.append((square, value))
        return res

    updated = False
    success_log_msg = "In {} {} the value {} is only possible in square at {}."

    for row_idx, row in enumerate(board.board_state):
        res = has_one_possible_square(row)
        if res:
            updated = True
            for square, value in res:
                coords = square.coords
                LOG.info(success_log_msg.format("row", row_idx, value, coords))
                board.assign_value(coords, value)
    
    for col_idx, col in enumerate(board.board_state.T):
        res = has_one_possible_square(col)
        if res:
            updated = True
            for square, value in res:
                coords = square.coords
                LOG.info(success_log_msg.format("column", col_idx, value, coords))
                board.assign_value(coords, value)
    return updated


def buildings_seen_limits_max_square_value(board: Board) -> None:
    """If x buildings seen then tallest building in square one is 2 + N - r + i
    N = Grid size
    r = Rule
    i = square index
    
    E.g.
    If only one building is seen, the first building is the tallest (blocks the rest).
    
    Run once.
    """
    LOG.info("Applying max limits to rows and columns based on the rules")
    for direction, rules in board.visible_buildings.items():
        for idx, rule in enumerate(rules):
            if rule == 0:
                # 0 represents no rule
                continue
            max_allowed_value = 1 + board.game_size - rule # + idx
            # Group is in correct direction based on viewing
            group = board.get_group(direction, idx)
            for idx, g in enumerate(group):
                g.sub_values = [s for s in g.sub_values if s <= max_allowed_value + idx]


    # Im missing something with this limiting thing.

    #e.g. 4 [][][][] -> [1][2][3][4]
    # 1 [][][][] -> [4][123][123][123]
    # 2 [][][][] -> [123][]


if __name__ == "__main__":
    for csv_path in SKYSCRAPER_PUZZLES_PATH.iterdir():
        csv_path = SKYSCRAPER_PUZZLES_PATH / "skyscrapers-logic-puzzle-i.csv"
        board = read_board(csv_path)
        solved = solve_board(board)
        if not solved or solved:
            board.display(solved)
            exit()